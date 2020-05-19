import numpy as np
fin = open('cameraIntrinsics.txt')
data = []
for line in fin:
    data.append(line)
string = data[0].split(", s")
for s in range(len(string)):
    string[s] = string[s][13:]
string[0] = string[0][2:]
string[-1] = string[-1][:-2]
for i in range(len(string) - 1):
    string[i] = string[i][:-1]
out = []
for i in range(len(string)):
    temp = string[i].replace(']','').replace('[','')
    lst = temp.split(', ')
    arr = []
    for k in lst:
        arr.append(float(k))
    npTemp = np.array(arr)
    npTemp = npTemp.reshape((3,3))
    out.append(npTemp)
