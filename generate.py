from utils import PDF, run_ocr, parse_pdf_to_df, merge_noised_df
from IPython.display import display 
import pandas as pd
import os

tsv_path = '/Users/chaeeunlee/Downloads/iupac_result/iupac_result.tsv' # or hdd1.
save_path =  '/Users/chaeeunlee/Downloads/saved/'
pdf_path_clean = '/Users/chaeeunlee/Downloads/saved/pdf/pdf_clean.pdf' # '/hdd1/chaeeun/.../pdf_clean.pdf'
pdf_path_noised = '/Users/chaeeunlee/Downloads/saved/pdf/pdf_noised.pdf' # '/hdd1/chaeeun/.../pdf_noised.pdf'

save_df_concat = True
chunk_size = 5000
num_concat = 10
colnames = ['id', 'iupac', 'inchi'] 

# returns generator? 별도의 반복 지정문 없이도, 읽어왔던 부분 바로 다음부터 다시 데이터를 읽어오게 됩니다.
df = pd.read_csv(tsv_path, sep='\t', chunksize=chunk_size, header=None, names=colnames, usecols = ['iupac'])
# returns generator? 별도의 반복 지정문 없이도, 읽어왔던 부분 바로 다음부터 다시 데이터를 읽어오게 됩니다.

frames = []
chunk_idx = 0
for chunk in df:
    chunk_idx +=1
    print(type(chunk)) # regular dataframe # might have to check and make sure the order is right 

    pdf = PDF() # do we really have to call this for every loop?
    pdf.chapter_body(chunk) # If a function parameter is a mutable object (e.g. a DataFrame), then any changes you make in the function will be applied to the object.
    pdf.output(pdf_path_clean) # probs will overwrite over the prev chunk, right?

    run_ocr(pdf_path_clean, pdf_path_noised)

    df_noised = parse_pdf_to_df(pdf_path_noised)
    pair_df = merge_noised_df(chunk, df_noised)

    frames.append(pair_df)

    if (chunk_idx % num_concat == 0) and save_df_concat:
        dfs_concat = pd.concat(frames)
        dfs_concat.set_index(keys=['index'], inplace=True, drop=True)
        dfs_concat_save_path = os.path.join(save_path, f'pair_df_upto_{chunk_idx * chunk_size}th_row.csv')
        dfs_concat.to_csv(dfs_concat_save_path)
        print('\n\n#########################')
        print('######### SAVED #########')
        print('#########################\n\n')
        frames = []