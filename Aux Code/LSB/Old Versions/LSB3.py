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

def encode(depth, stegBytes, pixels):
	if depth > 7 or depth <= 0:
		raise ValueError("Choose a depth between 1 and 7")

	#Works by side effect, overwriting pixels array
	toEncode = []
	for x in stegBytes:
		for b in '{0:08b}'.format(x): #turns a byte into an 8-bit string
			if b == '1':
				toEncode.append(1)
			else:
				toEncode.append(0)



	dString = '{0:03b}'.format(depth)
	mask = 255 #11111110
	pixels[0][0][0] = (pixels[0][0][0] & mask) | int(dString[0],2)
	pixels[0][0][1] = (pixels[0][0][1] & mask) | int(dString[1],2)
	pixels[0][0][2] = (pixels[0][0][2] & mask) | int(dString[2],2)

	#Write the 3 bits corresponding to the write depth in the first three values of the file, with a depth of 1 (to be able to extract it easily while decoding)


	pointer = [0,1,0]
	h,w,_ = np.shape(pixels)

	mask = 256 - 2**depth #For example, if depth = 3, mask will be 11111000


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

	def mergeBytes(pixels, curr, mask, pointer):
		(a,b,c) = pointer
		val = pixels[a][b][c]
		enc = sum([k*(2**(i)) for i,k in enumerate(curr)])

		pixels[a][b][c] = (pixels[a][b][c] & mask) | enc #The and with the mask will zero out the last "depth" bits, and the or operation will then write the correct bits in its place

	for k in range(0, len(toEncode) - depth + 1, depth):
		curr = toEncode[k:k+depth]
		mergeBytes(pixels, curr, mask, pointer)
		
		incPointer(pointer)

	
	if len(toEncode)%depth != 0: #Don't forget to encode any bits that might be left over, which we do with the biggest mask possible
		curr = toEncode[-(len(toEncode)%depth):] #The modulo operations returns the number of leftover bits, which we can access by slicing
		mask = 256 - 2**len(curr) 
		mergeBytes(pixels, curr, mask, pointer)

def createImage(pixels, path):
	format = path.split(".")[-1].upper()
	if format != "PNG" and format != "TIFF" and format != "BMP":
		raise ValueError("Please use a lossless output format: PNG, BMP or TIFF.")

	Image.fromarray(pixels).save(path, format)


#Decode-related functions
def getPixels(path):
	return list(Image.open(path).getdata())

def readLSBs(depth, pixelList, start, length):
	'''
	#Assumes an array of homogeneously-depthed (yeah that's a term) pixels (that is, without the mandatory 1-depth pixel at the beginning for encoding depth itself)
	#Terminology:
		#| --- / --- / --- | --- / --- / --- |		| | = 1 pixel, / --- = 1 byte
		#Each byte contains depth interesting bits, call that unit of length a num. 1 num = depth bits

	nums = start//depth #Index of the startpos, in whole nums -- the real startpos is, in the general case, not a whole num
	r = start%depth #How many bits we should offset from the last whole num before reading


	#Every pixel holds three nums, therefore:
	pix = nums//3 #Index of the pixel containing the starting bit

	interestingPixels = pixelList[pix:pix + length//(3*depth) + 3] #+3 just to be safe
	out = []

	mask = sum([2**k for k in range(depth)])
	for p in interestingPixels
		for i in range(3):
			out.append(p[i] & mask) #Get the depth-many LSBs

	return out[r:r+length]
	'''




def packInBytes(bitList):
	if len(bitList)%8 != 0:
		raise ValueError("Must be a multiple of 8 to pack into byte")

	out = []
	for bytePointer in range(0, len(bitList)-7, 8):
		out.append(sum([k*(2**(7-i)) for i,k in enumerate(bitList[bytePointer:bytePointer+8])])) #Delicious

	return bytes(out)

#def extractFile(pixelList):


#Main loop

if args[0] == "encode":
	#try:
	pix = getCoverPixels(args[2])
	sb = getStegBytes(args[1])
		
	if 4 >= len(args):
		depth = 1		#If no depth is specified, default to 1
	else:
		depth = int(args[4],10)

	print("start Encode")
	encode(depth, sb,pix)
	createImage(pix, args[3])
	t2 = time.time()
	print(str(t2-t1))
	#except Exception as e:
		#print("Error: "+str(e))
		#sys.exit()

elif args[0] == "decode":
	#try:
	extractFile(getPixels(args[1]))
	#except Exception as e:
		#print("Error: "+str(e))
		#sys.exit()




