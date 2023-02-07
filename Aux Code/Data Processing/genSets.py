import os
import random
import shutil
from math import floor

# ----- CONFIG ----- #

path = "C:\\Users\\pierr\\Documents\\Scolaire\\TIPE\\Datasets\\Dataset 7"

trainPercentage = 94
validPercentage = 5
testPercentage = 1


# ----- CODE ----- #

assert trainPercentage+validPercentage+testPercentage == 100

pathSource = path+"\\Raw"

trainPercentage *= .01
validPercentage *= .01
testPercentage *= .01

trainPath = path+"\\train"
validPath = path+"\\valid"
testPath = path+"\\test"

outs = [(trainPath,trainPercentage),(validPath,validPercentage),(testPath,testPercentage)]
exs = ["\\stegos\\","\\cleans\\"]

for p,_ in outs:
    try:
        os.mkdir(p)
        os.mkdir(p+"\\stegos")
        os.mkdir(p+"\\cleans")
    except:
        pass

for ex in exs:
    source = pathSource+ex
    n = len(os.listdir(source))
    for p,per in outs:
        ims = os.listdir(source)
        toMove = random.sample(ims, floor(n*per))
        for f in toMove:
            shutil.move(source+f, p+ex+f)
        


