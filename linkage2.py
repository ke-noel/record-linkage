'''
Basic record linkage between two dataframes.
'''
import recordlinkage as rl


def to_category(df):  # reduce memory usage
    for col in df.columns:
        num_unique_values = len(df[col].unique())
        num_total_values = len(df[col])
        if num_unique_values / num_total_values < 0.5:
            df.loc[:,col] = df[col].astype('category')
        else:
            df.loc[:,col] = df[col]
    return df


# TODO add distribution stuff from Linkage1
class Linkage2(object):
    def __init__(self, dfA, dfB, match_val,
                 block_on=[],
                 comp_exact=[],  # expected format is [[lblA, lblB], ...]
                 comp_string=[],
                 comp_method='jarowinkler'):
        #reduce memory usage, does not work if they refer to the same memory location
        self.dfA = to_category(dfA)  
        self.dfB = to_category(dfB)

        self.match_val = match_val  # value required to be considered a match in compare
        self.block_on = block_on
        self.comp_exact = comp_exact
        self.comp_string = comp_string
        self.comp_method = comp_method

        self.pairs = self.get_pairs()
        self.features = self.get_features()
        self.matches = self.get_matches()

    def get_pairs(self):
        for block in self.block_on:
            indexer = rl.BlockIndex(on=block)
            pairs = indexer.index(self.dfA, self.dfB)
            try:
                combined_pairs = last_pairs.union(pairs)
            except:
                pass
            last_pairs = pairs
        try:  # more than one block
            return combined_pairs
        except:  # one block
            return pairs

    def get_features(self):
        comp = rl.Compare()

        for lbl in self.comp_string:
            comp.string(lbl[0], lbl[1], method=self.comp_method, threshold=0.75, label=lbl[0])
        for lbl in self.comp_exact:
            comp.exact(lbl[0], lbl[1], label=lbl[0])

        return comp.compute(self.pairs, self.dfA, self.dfB)

    def get_matches(self):
        return self.features[self.features.sum(axis=1) > self.match_val]
