f1 = open('FR.7z', 'rb')
f2 = open('extracted_FR.7z', 'rb')

b1 = f1.read()
b2 = f2.read()

if b1 == b2:
    print("Files were identical")
else:
    for i in range(len(b1)):
        bit1 = b1[i]
        bit2 = b2[i]

        if bit1 == bit2:
            term = "V"
        else:
            term = "X"

        print(str(i)+": "+str(bit1)+" || "+str(bit2)+" -- "+term)