## inspect_merged_df.py

import pandas as pd
import os

csv_path = '/Users/chaeeunlee/Downloads/saved_3/merge_res/pair_df_merged.csv'

df = pd.read_csv(csv_path, usecols = ['iupac', 'iupac_noised'])

print(f'len(df) = {len(df)}')

## len(df) = 350600