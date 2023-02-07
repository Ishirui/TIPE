from PIL import Image

'''

arr = [i for i in range(50)]
depth = 3

print(type(type(3)))

print(arr)

print(len(arr)%depth) # = len(stuff that's gonna be left over)

for k in range(0, len(arr) - depth + 1, depth):
	curr = arr[k:k+depth]
	print(curr)

#print(arr[:-(len(arr)%depth)])
print(arr[-(len(arr)%depth):])



dString = "101"

for k in range(3):
	print(int(dString[k],2c))

'''

'''
arr = [1,2,3]

if not arr[3]:
	print("Kay")
'''

'''
depth = 3
mask = 2**2 + 2**1 + 1

x = int("11011001", 2)

s = '{0:0'+str(depth)+'b}'

for b in s.format(x):
	print(b) #Get the LSBs
'''

def readLSBs(depth, pixelList, start, length):
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
	s = '{0:0'+str(depth)+"b}"
	for p in interestingPixels:
		for i in range(3):
			for b in s.format(p[i] & mask):
				out.append(int(b)) #Get the depth-many LSBs

	print(out)
	return out[r:r+length]


pix = list(Image.open("stegged.png").getdata())

print(readLSBs(3, pix[1:], 0, 32))
x = 5
k = x.to_bytes(4, 'little')
for a in k:
	for b in '{0:08b}'.format(a):
		print(b)