
import os
import pandas as pd
import numpy
import cv2
from fpdf import FPDF, XPos, YPos
from PIL import Image
from pdf2image import convert_from_path
import ocrmypdf
import nltk
import re
import regex


from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.col = 0  # Current column
        self.y0 = 0  # Ordinate of column start -> i think this should be paper margin

    def set_col(self, col):
        # Set column position:
        self.col = col
        x = 10 + col * 65
        self.set_left_margin(x)
        self.set_x(x)

    @property
    def accept_page_break(self):

        self.set_col(0)
        # Trigger a page break:
        return True

    ## iter through pandas df instead of batch producing txt file, so that we can add margins between different iupac entries. 
    def chapter_body(self, df):
        self.add_page()

        self.set_font("Helvetica", size=12)

        for index, row in df.iterrows():
            print(row)

            with self.offset_rendering() as dummy:
              dummy.multi_cell(w=60, h=5, txt=row['iupac'])
            if dummy.page_break_triggered:
              self.add_page()



            self.multi_cell(w=60, h=5, txt=row['iupac'], new_y=YPos.NEXT)#, new_x=XPos.LEFT, max_line_height=pdf.font_size, border = 1)#RIGHT, new_y=TOP)
            self.multi_cell(w=60, h=10, txt=' ', new_y=YPos.NEXT)
            self.ln() # not sure what im doing with this -> 이거 없으면 계단식으로 프린트됨. 

        self.set_col(0)

def run_ocr(input_path, output_path):
  # try:
  #   ocrmypdf.ocr(path, path, deskew=True) # do we still need this here? nah we actually don't. have to convert to images anyways if we want to add noise. 
  # except ocrmypdf.PriorOcrFoundError:
    pdf2images = convert_from_path(input_path)

    # convert to opencv image and add noise
    pdf2images = [noise_image(pil2cv(img), method=2) for img in pdf2images] 
    # convert back to pillow image to save
    pdf2images = [cv2pil(img) for img in pdf2images]

    pdf2images[0].save(output_path, save_all=True, append_images=pdf2images[1:]) # saving noised image AS PDF on the same path. 
    ocrmypdf.ocr(output_path, output_path, deskew=True)

    return None


def clean_up_new_line(in_str):
  
    res = re.sub(r'\n[^$]', '-', in_str)
    res = re.sub(r'-(-)+', '-', res)

    return res

def parse_pdf_to_df(pdf_path, char_margin=2.0, line_margin=2.0, boxes_flow=None):
    df = pd.DataFrame() # create empty dataframe
    df['iupac_noised'] = [] # not sure about this one. do we have to specify df size from the get-go?

    fp = open(pdf_path, 'rb')

    rsrcmgr = PDFResourceManager()
    laparams = LAParams(char_margin=char_margin, line_margin=line_margin, boxes_flow=boxes_flow)
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    pages = PDFPage.get_pages(fp)

    item_idx = 0 # idx for each iupac identifier. nothing to do with page number.
    for page_num, page in enumerate(pages):

        print(f'Processing next page... page num = {page_num}')
        interpreter.process_page(page)
        page_layout = device.get_result()

        for textbox in page_layout: # each textbox in a page # well assuming this returns int he r
            
            print(f'Processing next textbox... page num = {page_num}, item_idx = {item_idx}')
        
            if isinstance(textbox, LTTextBox):
            ocr_text = textbox.get_text()
            # ori_text = pair_df['iupac'][item_idx]
            # print(f'ori_text = {ori_text}, \n ocr_text(before newline clean-up) = {ocr_text}')

            # clean up new line
            ocr_text = clean_up_new_line(ocr_text)
            df.at[item_idx, 'iupac_noised'] = ocr_text

            item_idx +=1

    return df

def merge_noised_df(df_ori, df_noised):

    assert (df_ori.shape[0] == df_noised.shape[0]), 'two dataframes have different number of rows'

    pair_df = df_ori.copy(deep=True)
    pair_df['iupac_noised'] = '' 

    num_rows = df_ori.shape[0]

    for row_idx in range(num_rows):
        ori_text = pair_df['iupac'][row_idx]

        noised_text = df_noised['iupac_noised'][row_idx]
        # noised_text = clean_up_new_line(noised_text) # this has to be done prior to calling this function

        if nltk.edit_distance(ori_text, noised_text) < (num_rows//3):
            pair_df.at[row_idx, 'iupac_noised'] = noised_text
        else:
            print(f'row_idx = {row_idx}, edit dist is too high!! \n')

    return pair_df 