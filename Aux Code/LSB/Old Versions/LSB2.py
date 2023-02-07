import sys
import os.path
from PIL import Image
import numpy as np
import time


args = sys.argv[1:]

t1 = time.time()


#Encode-related functions

def getCoverPixels(imagePath):
	return np.array(Image.open(imagePath))

def getStegBytes(filePath):
	if not os.path.isfile(filePath):
		raise ValueError("is not a valid file (maybe a directory ? convert to zip first)")

	rawBytes = open(filePath, "rb").read() #Might raise FileNotFoundError
	name = filePath.split('\\')[-1]
	fileSize = len(rawBytes)
	fileSizeBytes = fileSize.to_bytes(4, 'little')
	nameBytes = name.encode('utf-8')
	nameBytesSizeBytes = len(nameBytes).to_bytes(4, 'little')

	return nameBytesSizeBytes+nameBytes+fileSizeBytes+rawBytes

def encode(stegBytes, pixels):
	#Works by side effect, overwriting pixels array
	toEncode = []
	for x in stegBytes:
		for b in '{0:08b}'.format(x): #turns a byte into an 8-bit string
			toEncode.append(b)


	pointer = [0,0,0]
	h,w,_ = np.shape(pixels)

	def incPointer(pointer):
		if pointer[2] < 2: #3-1
			pointer[2] = pointer[2] + 1
		elif pointer[1] < (w-1):
			pointer[2] = 0
			pointer[1] = pointer[1] + 1
		else:
			pointer[2] = 0
			pointer[1] = 0
			pointer[0] = pointer[0] + 1

	for bit in toEncode:
		(a,b,c) = pointer
		if bit == '1':
			pixels[a][b][c] = pixels[a][b][c] | 1 #OR with 00000001 -- ensures the last bit is 1
		else:
			pixels[a][b][c] = pixels[a][b][c] & 254 #AND with 11111110 -- ensures the last bit is 0
		incPointer(pointer)

def createImage(pixels, path):
	format = path.split(".")[-1].upper()
	if format != "PNG" and format != "TIFF" and format != "BMP":
		raise ValueError("Please use a lossless output format: PNG, BMP or TIFF.")

	Image.fromarray(pixels).save(path, format)


#Decode-related functions
def getPixels(path):
	return list(Image.open(path).getdata())

def readLSBs(pixelList, start, length):
	qs = start//3 #qs = number of whole pixels before the wanted bit, rs = number of bits from the start of the pixel
	rs = start%3 #rs = number of bits from the start of the last pixel

	l = pixelList[qs:qs+(length//3)+2] #+1 to get the whole pixel, +1 to actually include in slicing

	out = []
	for x in l:
		for i in range(3):
			out.append(x[i] & 1) #Get the LSBs

	
	return out[rs:rs+length]

def packInBytes(bitList):
	if len(bitList)%8 != 0:
		raise ValueError("Must be a multiple of 8 to pack into byte")

	out = []
	for bytePointer in range(0, len(bitList)-7, 8):
		out.append(sum([k*(2**(7-i)) for i,k in enumerate(bitList[bytePointer:bytePointer+8])])) #Delicious

	return bytes(out)

def extractFile(pixelList):
	offset = 0
	nameSize = int.from_bytes(packInBytes(readLSBs(pixelList,offset,32)), 'little')
	offset += 32
	name = packInBytes(readLSBs(pixelList,offset,8*nameSize)).decode("utf-8")
	offset += 8*nameSize
	fileSize = int.from_bytes(packInBytes(readLSBs(pixelList,offset,32)), 'little')
	offset += 32

	name = "extracted_"+name

	file = open(name, 'wb')
	file.write(packInBytes(readLSBs(pixelList,offset,8*fileSize)))
	file.close()


#Main loop

if args[0] == "encode":
	try:
		pix = getCoverPixels(args[2])
		sb = getStegBytes(args[1])
		encode(sb,pix)
		createImage(pix, args[3])
		t2 = time.time()
		print(str(t2-t1))
	except Exception as e:
		print("Error: "+str(e))
		sys.exit()

elif args[0] == "decode":
	try:
		extractFile(getPixels(args[1]))
	except Exception as e:
		print("Error: "+str(e))
		sys.exit()




