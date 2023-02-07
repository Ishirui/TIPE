#-----IMPORTS-----#
from PIL import Image
import numpy as np
import os

#-----CONFIG-----#

#inputPath = ""
#outputPath = ""

root = "C:\\Users\\pierr\\Documents\\Scolaire\\TIPE\\Aux Code\\LSB"
outRoot = "C:\\Users\\pierr\\Documents\\Scolaire\\TIPE\\Aux Code\\LSB"

#dirs = ['Old','Raw','test','train','test','valid']
dirs = ['V4']

def getLSBs(path):
    im = Image.open(path)
    pix = np.asarray(im)

    res = np.zeros(np.shape(pix), np.uint8)
    for i,lig in enumerate(pix):
        for j,p in enumerate(lig):
            if type(p) == np.uint8:
                res[i][j] = (p & 1)*255
            else:
                for k,v in enumerate(p):
                    res[i][j][k] = (v & 1)*255 #Extract LSBs

    return res

def makeLSBImage(data, path):
    format = path.split(".")[-1].upper()
    if format != "PNG" and format != "TIFF" and format != "BMP":
        raise ValueError("Please use a lossless output format: PNG, BMP or TIFF.")
    
    Image.fromarray(data).save(path, format)

def changeTitle(st, extra):
    segs = st.split("\\")
    segs[-1] = extra + segs[-1]
    for i,k in enumerate(segs[1:]):
        segs[i+1] = "\\"+k
    return ''.join(segs)

def extract(path,out = None):
    if out == None:
        out = changeTitle(path, "LSBs_")
    makeLSBImage(getLSBs(path),out)

    

for ext in dirs:
    for ext2 in ['test']:
        inputPath = root+"\\"+ext+"\\"+ext2
        outputPath = outRoot+"\\"+ext+"\\"+ext2
        toProc = [x for x in os.listdir(inputPath) if x.lower().endswith(('.png', '.tiff', '.bmp'))]
        k = len(toProc)
        for i,name in enumerate(toProc):
            extract(inputPath+'\\'+name, outputPath+'\\LSBs_'+name)
            print(str(i+1)+" images out of"+str(k)+" processed")
