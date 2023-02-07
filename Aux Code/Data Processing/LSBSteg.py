#Module form of the LSB.py script

import sys
import os
from PIL import Image
import numpy as np
from math import ceil
import random

#General functions

def asBits(b, length = 8):
    out = []
    
     #Returns an int array representing the bits of the given bytes/intList object
    for x in b: #x = int
        buff = []
        curr = x
        for _ in range(length):
            buff.append(curr%2)
            curr = curr//2
        buff.reverse()
        out += buff
    return out

def asInt(b):
    s = 0
    p = 1
    for k in reversed(b):
        s += k*p
        p *= 2
    return s
    #Returns the int represented by the b bit array

def readLSBs(b, depth):
    mask = 2**depth - 1
    out = []
    for x in b:
        out.append(x & mask)
    return asBits(out, depth)

#Encode-related functions

def getCoverPixels(path):
	return np.array(Image.open(path))

def getStegBytes(data):
    if type(data) is bytes:
        nameBytes = "rawBytes".encode()
        encodeBytes = data
        size = len(encodeBytes)
    else: #It's str
        if os.path.exists(data):
            path = data
            nameBytes = path.split('\\')[-1].encode()
            size = os.path.getsize(path)
            encodeBytes = open(path, "rb").read()
        else:
            nameBytes = "rawText.txt".encode()
            encodeBytes = data.encode()
            size = len(encodeBytes)
    


    out = len(nameBytes).to_bytes(1, "big")
    out += size.to_bytes(3, "big")
    out += nameBytes
    out += encodeBytes


    #Scheme: depth (3 bits, depth = 1) - length of name (1 byte)-fileSize (3 bytes) - name (variable) - file (variable)
    return out

def nextPoint(p, mask):
    if len(mask) == 2:
        return nextPoint2D(p, mask)
    else:
        return nextPoint3D(p, mask)

def nextPoint2D(p,mask):
    _,b = mask
    x,y = p

    if y < (b-1):
        return (x,y+1)
    else:
        return (x+1,0)

def nextPoint3D(p,mask):
    _,b,c = mask
    x,y,z = p

    if z < (c-1):
        return (x,y,z+1)
    else:
        if y < (b-1):
            return (x,y+1,0)
        else:
            return (x+1, 0, 0)

def merge(sb, pix, depth): #Works by side effect, modifying pix
    if len(np.shape(pix)) == 2:
        p = (0,0) #Monochrome case
    else:
        p = (0,0,0) #Color case
    pointerMask = np.shape(pix)

    #We first encode the depth at the beginning with a depth of 1
    #Depth must be at most 7, so it can be represented with 3 bits, which can fit on the first pixel
    mask = 254 #11111110
    
    for k in '{0:03b}'.format(depth): #The .format instruction returns a string of the number written in binary -- it's a slow conversion, but for 3 bits it's ok 
        pix[p] = (pix[p] & mask) | int(k)
        p = nextPoint(p, pointerMask)


    i = 0
    bitMask = 255 - (2**depth - 1)
    toEnc = asBits(sb)


    while i+depth <= len(toEnc):
        buff = toEnc[i:i+depth]
        pix[p] = (pix[p] & bitMask) | asInt(buff)
            #To overwrite the last depth bits of each channel of each pixel, we first zero them out by ANDing them with a mask: 11110000, with depth trailing zeros
            #Next we OR it with the bits we want to write, padded to the left with zeros
        p = nextPoint(p, pointerMask)
        i += depth

    #There might be remaining bits
    buff = toEnc[i:]
    bm = 255 - (2**len(buff) - 1)
    pix[p] = (pix[p] & bm) | asInt(buff)

def createImage(pixels, path):
	format = path.split(".")[-1].upper()
	if format != "PNG" and format != "TIFF" and format != "BMP":
		raise ValueError("Please use a lossless output format: PNG, BMP or TIFF.")

	Image.fromarray(pixels).save(path, format)

#Decode-related functions
def getPixelBytes(path):
	return Image.open(path).tobytes() #Returns a bytes object of the pixel data
    
def getMeta(pixBytes):
    p = 0
    
    depthBits = readLSBs(pixBytes[p:p+3], 1)
    p += 3

    depth = asInt(depthBits)

    temp = readLSBs(pixBytes[p:p+ceil(8*4/depth)], depth)
    
    nameLengthAndFileSizeBits = temp[:8*4]
    remainder = temp[8*4:]
    
    
    p += ceil(8*4/depth)

    nameLength = asInt(nameLengthAndFileSizeBits[:8])
    fileSize = asInt(nameLengthAndFileSizeBits[8:])

    temp = readLSBs(pixBytes[p:p+ceil(8*nameLength/depth)], depth)
    nameBits = remainder + temp[:8*nameLength-len(remainder)]

    rem = temp[8*nameLength-len(remainder):]

    p += ceil(8*nameLength/depth)

    fileName = bytes([asInt(nameBits[i:i+8]) for i in range(0, len(nameBits), 8)]).decode()

    totalSize = 1+3+fileSize+len(fileName) #1 for storing the length of the name, 3 for storing the file size, the actual name's size, and the actual file's size
    return depth, fileName, fileSize, totalSize, p, rem
    
def extractFile(pixBytes, meta):
    depth, fileName, fileSize, totalSize, p, rem = meta
    
    fileSize *= 8 #To get it in bits
    totalSize *= 8

    #The last pixel byte is not encoded with the same depth ! It's at the depth of however many bits are left..
    leftover = totalSize % depth

    toRead = fileSize-len(rem)-leftover

    fileBits = rem + readLSBs(pixBytes[p:p+ceil(toRead/depth)], depth)

    p += ceil(toRead/depth)

    fileBits += readLSBs(pixBytes[p:p+1], leftover)


    fileBytes = bytes([asInt(fileBits[i:i+8]) for i in range(0, len(fileBits), 8)])

    file = open("extracted_"+fileName, 'wb')
    file.write(fileBytes)
    file.close()
    

#Main funcs

def hide(imagePath, data, outputPath, depth = 1):
    pix = getCoverPixels(imagePath)
    sb = getStegBytes(data)

    merge(sb, pix, depth)
    createImage(pix, outputPath)

def extract(path):
    pb = getPixelBytes(path)

    extractFile(pb, getMeta(pb))

