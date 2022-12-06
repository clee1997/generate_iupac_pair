import os.path
import pandas as pd

saved_path =  '/Users/chaeeunlee/Downloads/saved_3/'
save_path = '/Users/chaeeunlee/Downloads/saved_3/merge_res/'
csv_files = [f for f in os.listdir(saved_path)
            if os.path.isfile(os.path.join(saved_path, f)) and f.startswith('pair_df')]       
num_dfs = len(csv_files)

# print(listdir)

frames = []
# for i in range(num_dfs):
for csv_name in csv_files:
    print(csv_name)
    df = pd.read_csv( os.path.join(saved_path, csv_name) )
    # print(df.describe())
    frames.append(df)

    

# print(frames)
df_merged = pd.concat(frames)
df_merged.drop(['index'], axis=1, inplace=True)
df_merged.reset_index(drop=True, inplace=True)

df_merged_save_path = os.path.join(save_path, 'pair_df_merged.csv')
df_merged.to_csv(df_merged_save_path)

print('\n\n#########################')
print('######### SAVED #########')
print('#########################\n\n')
