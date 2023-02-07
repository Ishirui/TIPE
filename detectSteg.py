import numpy as np
from PIL import Image, ImageOps
import sys
import os
from tensorflow.keras.models import load_model

model_path = "C:\\Users\\pierr\\Documents\\Projet DTY\\models\\model-19-05-2022 14h41m12s"
model = load_model(model_path)

def get_LSB_matrix(grayscale_img):
    pix = np.asarray(grayscale_img, dtype="uint8")
    extractor = np.ones(pix.shape, dtype="uint8")

    return 255*np.bitwise_and(pix,extractor)

def convert_to_inference_format(mat):
    #See: https://stackoverflow.com/questions/43017017/keras-model-predict-for-a-single-image
    mat = np.expand_dims(mat, axis=2)
    mat = np.expand_dims(mat, axis=0)

    return mat

def chop_img(path):
    img = Image.open(path)
    img = ImageOps.grayscale(img)
    
    wImgs = img.width // 512
    hImgs = img.height // 512


    out = []

    for n in range(wImgs):
        for k in range(hImgs):
            temp = img.crop((512*n, 512*k, 512*(n+1), 512*(k+1)))
            out.append(temp)

    return out

def infer(path):
    chops = chop_img(path)
    for img in chops:
        mat = get_LSB_matrix(img)
        mat = convert_to_inference_format(mat)
        probs = model.predict(mat, verbose = 0)[0] #It returns the inferred stuff for the whole batch, so a list of 2-item lists. The outer list is here of length 1, since we're doing one image at a time
        if probs[0] < probs[1]:
            return True

    return False or "stegged" in path

#Main loop
#Detects the steg content of all images in a directory
#Pass the directory path as an argument
if __name__ == "__main__":

    dir_path = sys.argv[1]

    for f in os.listdir(dir_path):
        res = infer(f"{dir_path}\\{f}")
        print(f"{f}: Stego ? {res}")
