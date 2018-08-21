'''
Basic record linkage (within one dataset)
Creates histograms of distribution of pairs created for the blocks
used as well as the distribution of duplicates per record (calculated
through the record linkage-identified matches with another method to verify.
'''
import recordlinkage as rl
import conversions
import physt
import physt.io
import os


def read_data(path, set_index=True, index='record_id'):
    df = pd.read_csv(path,
                     sep=',',
                     engine='c',
                     skipinitialspace=True,
                     encoding='utf-8')
    if set_index:
        df.set_index(index, inplace=True)
    return df


def to_category(df):  # reduce memory usage
    for col in df.columns:
        num_unique_values = len(df[col].unique())
        num_total_values = len(df[col])
        if num_unique_values / num_total_values < 0.5:
            df.loc[:,col] = df[col].astype('category')
        else:
            df.loc[:,col] = df[col]
    return df


class Linkage1(object):
    def __init__(self, tag, df, match_val,
                 block_on=[],
                 comp_exact=[],  # expected format is [lblA, ...]
                 comp_string=[],
                 comp_method='jarowinkler'):

        self.save_dir = '../' + str(tag)
        self.df = to_category(df)  # reduce memory usage
        self.match_val = match_val  # value required to be considered a match in compare
        self.block_on = block_on
        self.comp_exact = comp_exact
        self.comp_string = comp_string
        self.comp_method = comp_method

        if not os.path.isdir(self.save_dir):
            os.mkdir(self.save_dir)

        self.pairs = None
        self.features = None
        self.matches = None

        # Vars for analysis (histograms, etc.)
        self.pairs_dist = []
        self.real_dup_dist = []
        self.dup_dist = []

        self.pair_cntr = {}  # returns "blockName: count"
        self.dup_dict = {}  # returns "record: duplicates"

        self.total_count = len(self.df.index)
        self.real_dup_count = 0
        self.dup_count = 0
        self.real_unique_count = 0
        self.unique_count = 0

    def get_pairs(self):
        for block in self.block_on:
            indexer = rl.BlockIndex(on=block)
            pairs = indexer.index(self.df)
            self.pair_cntr.update({block: len(pairs)})
            try:
                combined_pairs = last_pairs.union(pairs)
            except:
                pass
            last_pairs = pairs

        # Make list for histogram (distribution of pairs by block)
        for n, block in enumerate(self.pair_cntr):
            for i in range(self.pair_cntr[block]):
                self.pairs_dist.append(n)

        try:  # more than one block
            self.pairs = combined_pairs
        except:  # only one block
            self.pairs = pairs

        conversions.mi_to_csv(self.pairs, self.save_dir + '/pairs.csv')
        conversions.mi_to_parquet(self.pairs, self.save_dir + '/pairs.parquet')

    def get_features(self):
        comp = rl.Compare()

        for lbl in self.comp_string:
            comp.string(lbl, lbl, method=self.comp_method, threshold=0.75, label=lbl)
        for lbl in self.comp_exact:
            comp.exact(lbl, lbl, label=lbl)

        self.features = comp.compute(self.pairs, self.df)

        self.features.index.set_names(['id_0', 'id_1'], inplace=True)
        self.features.reset_index(inplace=True)

        self.features.to_csv(self.save_dir + '/features.csv')
        conversions.df_to_parquet(self.features, self.save_dir + '/features.parquet')

    def get_matches(self):
        self.matches = self.features[self.features.sum(axis=1) >= self.match_val]
        self.matches.to_csv(self.save_dir + '/matches.csv')
        conversions.df_to_parquet(self.matches, self.save_dir + '/matches.parquet')

    # return distribution of duplicates per record; use as check
    def get_real_dup_dist(self):
        cntrs = {i+1: 0 for i in range(10)}
        for cntr in cntrs:
            for record in self.df.index.values:
                cntrs[cntr] += 1 if ('-dup-' + str(cntr - 1) in str(record)) else 0

        # Write data to histogram-friendly list
        for cntr in cntrs:
            self.real_dup_count += cntrs[cntr]
            try:
                cntrs[cntr] -= cntrs[cntrs[cntr] + 1]  # don't double count duplicates
            except:
                pass

            for i in range(cntrs[cntr]):
                self.real_dup_dist.append(cntr)

        self.real_unique_count = self.total_count - self.real_dup_count

    def get_dup_dist(self):
        all_pairs = []
        for n, record in enumerate(self.matches.iloc[:,0]):
            all_pairs.append([record, self.matches.iloc[n][1]])

        for pair in all_pairs:
            # Does pair already have a box?
            if pair[0] in self.dup_dict:
                self.dup_dict[pair[0]].append(pair[1])
            # If the pair isn't in an existing box, make a new box
            elif not (pair[1] in [x for v in self.dup_dict.values() for x in v]):
                self.dup_dict.update({pair[0]: [pair[1]]})

        # get distribution of duplicates per record
        for box in self.dup_dict:
            self.dup_dist.append(len(self.dup_dict[box]))  # add the number of duplicates per record
            self.dup_count += len(self.dup_dict[box])

        self.unique_count = self.total_count - self.dup_count

        # add records with no duplicates
        while len(self.dup_dist) < self.unique_count:
            self.dup_dist.append(0)

    def get_counts(self):
        self.get_real_dup_dist()
        self.get_dup_dist()
        print('Actual record counts: %d unique, %d duplicates'
              %(self.real_unique_count, self.real_dup_count))
        print('Algorithm record counts: %d unique, %d duplicates'
              %(self.unique_count, self.dup_count))

    def make_hist(self, l, name):
        hist = physt.histogram(l, name=name)
        physt.io.save_json(hist, path=self.save_dir+'/'+name)
        return hist

    # remove all duplicate records from dataframe; keep first record found
    def remove_dup(self):
        # ensure dup_dict has been generated
        if not self.dup_dict:
            self.get_dup_dist()
        # really really slow right now; ~45s/9,000
        # could be improved for large datasets by removing dictionary entries as they're matched
        for record in self.df.index.values:
            if (record in [x for v in self.dup_dict.values() for x in v]):
                self.df.drop([record], inplace=True)

        self.df.to_csv(self.save_dir + '/no_dup.csv')
        conversions.df_to_parquet(self.df, self.save_dir + '/no_dup.parquet')


if __name__ == '__main__':
    df =read_data('records/data.0001.csv')
    link = Linkage1('new_data', df, 5, block_on=['SIN', 'DOB'], comp_exact=['SIN', 'DOB', 'PostalCode', 'PhoneNum'], comp_string=['Name', 'Street'])
    link.get_pairs()
    link.get_features()
    link.get_matches()
    link.get_counts()
    link.remove_dup()

