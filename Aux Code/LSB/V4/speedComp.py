import time
import random
#Define functions here

def f1(b):
    s = 0
    for i,k in enumerate(b):
        s += k*(2**i)
    return s

def f2(b):
    s = 0
    p = 1
    for k in b:
        s += k*p
        p *= 2
    return s
#etc.

funcs = [f1, f2] #Put your functions here
samples = 5 #Nb of runs to average over
inputData = bytes([random.randint(0,255) for i in range(100000)]) #Will be passed to the funcs

# ---------------------------------------------- #

times = []

for f in funcs:
    curr = []
    for _ in range(samples):
        st = time.time()
        f(inputData)
        curr.append(time.time() - st)
    times.append(curr)

avgs = [sum(arr)/samples for arr in times]

for i,t in enumerate(avgs):
    print("Function n°"+str(i)+": "+str(t))