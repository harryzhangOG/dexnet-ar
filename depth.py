import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from perception import DepthImage as dpi
def bound(x, z):
    # small box
    #if x > 0.03 and x < 0.28 and z > -0.29 and z < 0.2:
    # desktop
    #if x > -0.18 and x < 0.9 and z > -0.7 and z < 0.43:
    # campbells
    if x > -0.69 and x < -0.41 and z > -0.55 and z < -0.21:
    # cereal bowl
    #if x > -0.24 and x < 0.15 and z > -0.27 and z < 0.15:
        return True
    return False

#fin = open('outCereal.txt')
fin = open('campbells.txt')
#fin = open('desktopClean.txt')
#fin = open('cerealBowl.txt')
depth = []
filtered = []
for line in fin:
    string = line.split(' ')
    x = float(string[0])
    y = float(string[1])
    z = float(string[2])
    if (bound(x, z)):
        filtered.append([x, z])
        depth.append(y)
# process z-coordinates
# fout =  open('test.txt', 'wt')
# for i in range(len(filtered)):
#     xz = filtered[i]
#     y = depth[i]
#     l = [xz[0], y, xz[1]]
#     tempStr = str(l) + "\n"
#     tempStr = tempStr.replace('[', '')
#     tempStr = tempStr.replace(']', '')
#     tempStr = tempStr.replace(',', '')
#     fout.write(tempStr)
# fout.close()
print(len(filtered))
maxY = max(depth)
shift = []
for i in depth:
    shift.append(-0.6 * i + maxY)

for point in filtered:
    point[0] = (point[0] + 0.69) * 200 / (-0.41 + 0.69)
    point[1] = (point[1] + 0.55) * 240 / (-0.21 + 0.55)
    # point[0] = (point[0] + 0.18) * 300 / (0.9 + 0.18)
    # point[1] = (point[1] + 0.7) * 300 / (0.43 + 0.7)
# round the (x, y) coordinates
for point in filtered:
    point[0] = round(point[0])
    point[1] = round(point[1])
depthMat = np.full((201, 241), np.inf)
for point in filtered:
    i = int(point[0])
    j = int(point[1])
    d = filtered.index(point)
    depthMat[i][j] = min(depthMat[i][j], shift[d])
# count = 0
# THE INPAINTING METHOD ONLY TAKES IN
for row in depthMat:
    # for cell in row:
    #     if cell == np.inf:
    #         count += 1
    #         cell = 0
    #         print(cell)
    row[row == np.inf] = 0
print(depthMat)
plt.imshow(depthMat)
plt.show()
plt.savefig('og.png')
depthImage = dpi(depthMat)
filledDepth = depthImage.inpaint()
plt.imshow(filledDepth.data)
plt.show()
