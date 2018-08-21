'''
Type conversions for package.
'''
import pandas as pd
import pyarrow.parquet as pq


def mi_to_csv(mi, path):
    df = pd.DataFrame(index=mi, columns=[])
    df.to_csv(path)


def csv_to_mi(path):
    df = pd.read_csv(path, index_col=[0, 1])
    return df.index


def df_to_parquet(df, path):
    df.to_parquet(path)


def parquet_to_df(path):
    return pd.read_parquet(path)


def mi_to_parquet(mi, path):
    df = pd.DataFrame(index=mi, columns=[''])
    df_to_parquet(df, path)


def parquet_to_mi(path):
    df = pd.read_parquet(path)
    return df.index


