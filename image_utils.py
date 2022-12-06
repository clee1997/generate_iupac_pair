import pandas as pd
import numpy as np
import cv2
from PIL import Image


def add_gaussian_noise(image):
    row,col,ch = image.shape
    mean = 0
    var = 0.01
    sigma = var**0.5
    gauss = np.random.normal(mean,sigma,(row,col,ch))
    gauss = gauss.reshape(row,col,ch)
    noisy = image + gauss
    return noisy

# assumes cv2 image 
def resize_image(image, scaling_factor = 0.5): 
    image = cv2.resize(image, dsize=(0,0), fx=scaling_factor, fy=scaling_factor) 
    return image

# assumes cv2 image 
def noise_image(image, method = 2, scaling_factor = 0.5):
    # method: 1 - gaussian / 2 - resize(deprecate resolution) / 3 - both

    if method == 1:
        return add_gaussian_noise(image)
    elif method == 2:
        return resize_image(image, scaling_factor)
    elif method ==3:
        res = resize_image(image, scaling_factor)
        res = add_gaussian_noise(res)
        return res

def pil2cv(pil_img):
    pil_image = pil_img

    # use numpy to convert the pil_image into a numpy array
    numpy_image = np.array(pil_image)  

    # convert to a openCV2 image and convert from RGB to BGR format
    opencv_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)

    return opencv_image


def cv2pil(cv_img):

    #open image using openCV2
    opencv_image = cv_img.astype(np.uint8)

    # convert from BGR to RGB
    color_coverted = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB)

    # convert from openCV2 to PIL
    pil_image = Image.fromarray(color_coverted)

    return pil_image