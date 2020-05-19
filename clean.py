import numpy
fin = open('dasaniOG.txt')
fout = open('dasani.txt', 'wt')
for line in fin:
    temp = 0
    count = 0
    for i in line:
        temp += 1
        if i == ' ':
            count += 1
        if count == 3:
            fout.write(line[:temp]+"\n")
            break
fin.close()
fout.close()
