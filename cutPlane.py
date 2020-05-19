from sklearn.neighbors import NearestNeighbors
import numpy as np
from scipy.spatial import distance
from numpy import linalg as LA


def localFitPlane(ptList, k, centroid):
    mean = centroid
    res = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    temp = []
    for i in range(len(ptList)):
        pt = ptList[i]
        temp = [pt[0] - mean[0], pt[1] - mean[1], pt[2] - mean[2]]
        res[0][0] += temp[0] * temp[0]
        res[0][1] += temp[0] * temp[1]
        res[0][2] += temp[0] * temp[2]
        res[1][0] += temp[1] * temp[0]
        res[1][1] += temp[1] * temp[1]
        res[1][2] += temp[1] * temp[2]
        res[2][0] += temp[2] * temp[0]
        res[2][1] += temp[2] * temp[1]
        res[2][2] += temp[2] * temp[2]
    for i in range(0, 3):
        for j in range(0, 3):
            res[i][j] = res[i][j] / k
    matrix = np.array(res)
    val, vec = LA.eig(matrix)
    smallest_evec = vec[:, np.argmin(val)]

    # minEigInd = np.where(val == np.amin(val))
    # eigTemp = vec[minEigInd]
    # norm = LA.norm(eigTemp)
    norm = LA.norm(smallest_evec)
    # print(eigTemp)
    eVec = []
    for v in smallest_evec:
        v = v / norm
        eVec.append(v)
    # print(eVec[0])
    return eVec



fin = open('cerealBowl.txt')
filtered = []
for line in fin:
    string = line.split(' ')
    x = float(string[0])
    y = float(string[1])
    z = float(string[2])
    filtered.append([x, y, z])
for i in range(len(filtered)):
    if filtered[i][1] < -0.33:
        filtered[i] = None
pointLst = []
fin.close()
for item in filtered:
    if item:
        pointLst.append(item)
X = np.array(pointLst)
neighbors = NearestNeighbors(n_neighbors=16, algorithm='ball_tree').fit(X)
for ind in range(len(pointLst)):
    knnInd = neighbors.kneighbors([pointLst[ind]], 16, return_distance=False)
    knn = []
    for i in knnInd[0][1:]:
        knn.append(pointLst[i])
    dist = 0
    for temp in knn:
        if temp != None:
            dist += distance.euclidean(temp, pointLst[ind])
            break
    # print(dist)
    # dist > 0.002 for campbells
    if dist > 0.004:
        pointLst[ind] = None
pointLstNew = []
for pt in pointLst:
    if pt != None:
        pointLstNew.append(pt)


temp = np.array(pointLstNew)
xmean = np.mean(temp[:, 0])
ymean = np.mean(temp[:, 1])
zmean = np.mean(temp[:, 2])
centroid = [xmean, ymean, zmean]
# for i in range(len(pointLstNew)):
#     d = distance.euclidean(pointLstNew[i], centroid)
#     # campbells: 0.08
#     if d > 0.1:
#         pointLstNew[i] = None
ptLst = []
for pt in pointLstNew:
    if pt != None:
        ptLst.append(pt)
X = np.array(ptLst)
neighbors = NearestNeighbors(n_neighbors=6, algorithm='ball_tree').fit(X)
for point in ptLst:
    knnInd = neighbors.kneighbors([point], 6, return_distance=False)
    knn = []
    for i in knnInd[0][1:]:
        knn.append(ptLst[i])
    normal = localFitPlane(knn, 5, centroid)
    # print(normal)
    for n in knn:
        sub = [0, 0, 0]
        sub[0] = n[0] - point[0]
        sub[1] = n[1] - point[1]
        sub[2] = n[2] - point[2]
        offset = normal[0] * sub[0] + normal[1] * sub[1] + normal[2] * sub[2]
        n[0] -= offset * normal[0]
        n[1] -= offset * normal[1]
        n[2] -= offset * normal[2]
temp = np.array(ptLst)
xmean = np.mean(temp[:, 0])
ymean = np.mean(temp[:, 1])
zmean = np.mean(temp[:, 2])
centroid = [xmean, ymean, zmean]
# for i in range(len(ptLst)):
#     d = distance.euclidean(ptLst[i], centroid)
#     if d > 0.1:
#         ptLst[i] = None
#         print('klkl')
out = []
for pt in ptLst:
    if pt != None:
        out.append(pt)
fout = open('cerealCut.txt', 'wt')
# Postprocess
for pt in out:
    tempStr = str(pt)
    tempStr = tempStr.replace('[', '')
    tempStr = tempStr.replace(']', '')
    tempStr = tempStr.replace(',', '')
    fout.write(tempStr + "\n")
fout.close()
