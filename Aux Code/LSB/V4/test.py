import random
import time

test = bytes([random.randint(0,255) for i in range(5000000)])

print("Data Genned")

start_time = time.time()

def bytesToBits(b):
    out = []
    
     #Returns a boolean array representing the bits of the given bytes object
    for x in b: #x = int
        buff = []
        curr = x
        for _ in range(8):
            buff.append(curr%2)
            curr = curr//2
        out += buff
    return out


x = bytesToBits(test)

print("--- %s seconds ---" % (time.time() - start_time))