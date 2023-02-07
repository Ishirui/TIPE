#This script converts all images in a folder to a format fit for NN training

import random
from PIL import Image, ImageOps
from LSBSteg import hide as hide
import os
import math

# ------ CONFIG ----- #

targetShape = (512,512) #Target res of the images
targetColor = False #Whether they should be color or grayscale
embedType = [.25,.5,.25]    #'text' -- as in random english text (few special characters, ascii 65-122) --, 'source' -- using real text from the below source -- or 'bytes'
                            #Put three floats representing the proportion of each you want
textSourcePath = 'C:\\Users\\pierr\\Documents\\Scolaire\\TIPE\\Datasets\\Dataset 1\\shakespeare_allcombined.txt'

embedMin, embedMax = (5000,20001) #Range of bytes to encode (as in message length)

embedRatio = 0 #Proportion of images to hide stuff in
depth = 1 #int between 1 and 7 or 'random'

imagesPath = 'E:\\Boulot\\TIPE\\BDD\\Stego App DB\\ORIGINAL - All Devices, JPG, .9, Auto\\originals\\Sub 2'
outputStegoPath = 'C:\\Users\\pierr\\Documents\\Scolaire\\TIPE\\Datasets\\Dataset 3\\Raw\\stegos'
outputCleanPath = 'C:\\Users\\pierr\\Documents\\Scolaire\\TIPE\\Datasets\\Dataset 3\\Raw\\cleans'

#-----FUNCS------#

def genBytes():
    size = random.randrange(embedMin, embedMax)
    return bytes([random.randrange(256) for i in range(size)])

def genText():
    size = random.randrange(embedMin, embedMax)
    return ''.join([chr(x) for x in [random.randrange(65,123) for i in range(size)] ]) #Beautiful one-liner to generate a random string imo

def genSource(text):
    size = random.randrange(embedMin, embedMax)
    s = random.randrange(0, len(text)-size)
    return text[s:s+size]

# ----- CODE ----- #

rawImgs = os.listdir(imagesPath)

nImgs = len(rawImgs)

print("----- START IMAGE PROCESSING -----")

for i,name in enumerate(rawImgs):
    img = Image.open(imagesPath+"\\"+name)
    img = ImageOps.fit(img, targetShape)
    if not targetColor:
        img = ImageOps.grayscale(img)
    img.save(outputCleanPath+'\\'+name.split('.')[0] + '.png', 'PNG')
    print("Processed"+str(i+1)+" of "+str(nImgs)+" images")

toSteg = random.sample(rawImgs, math.floor(nImgs*embedRatio))

toSteg = [name.split('.')[0] + '.png' for name in toSteg]

print('----- ALL IMAGES PROCESSED -----')
print('----- STARTING StegoText GENERATION ------')

stegTexts = []

text = open(textSourcePath,'r').read()
for i in range(len(toSteg)):
    r = random.random()
    if r <= embedType[0]:
        stegTexts.append(genText())
    elif r <= embedType[0] + embedType[1]:
        stegTexts.append(genSource(text))
    else:
        stegTexts.append(genBytes())

print('----- StegoText GENERATION COMPLETE ------')
print('----- STARTING EMBED -----')

if depth == 'random':
    for i,name in enumerate(toSteg):
        hide(outputCleanPath+'\\'+name, stegTexts[i], outputStegoPath+'\\'+name, random.randrange(8))
        print("Embedded"+str(i+1)+" of "+str(len(toSteg))+" images")
else:
    for i,name in enumerate(toSteg):
        hide(outputCleanPath+'\\'+name, stegTexts[i], outputStegoPath+'\\'+name, depth)
        print("Embedded"+str(i+1)+" of "+str(len(toSteg))+" images")

for name in toSteg:
    os.remove(outputCleanPath+'\\'+name)

print("----- DONE ------")

