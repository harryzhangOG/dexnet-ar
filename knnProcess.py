from sklearn.neighbors import NearestNeighbors
from scipy.spatial import distance
import numpy as np
from numpy import linalg as LA
fin = open('campbells.txt')

# Part 0: preprocess input data
pointLstTemp = [line.split(' ') for line in fin.readlines()]
pointLst = []
for pt in pointLstTemp:
    temp = []
    i = 0
    while i < 3:
        temp.append(float(pt[i]))
        i += 1
    pointLst.append(temp)
fin.close()
# Part 1: isolated outliers removal
X = np.array(pointLst)
neighbors = NearestNeighbors(n_neighbors=11, algorithm='ball_tree').fit(X)
prob_thr = []
for point in pointLst:
    knnInd = neighbors.kneighbors([point], 11, return_distance=False)
    knn = []
    for i in knnInd[0][1:]:
        knn.append(pointLst[i])
    sum = 0
    for temp in knn:
        print(temp)
        sum += distance.euclidean(temp, point[0])
    di = sum / (11 - 1)
    expSum = 0
    for temp in knn:
        expSum += np.exp((-(distance.euclidean(temp, point[0]) / di)))
    LD = expSum / (11 - 1)
    prob_i = 1 - LD
    threshold = 0.1 * di
    prob_thr.append(prob_i)
    # if prob_i > threshold:
    #     point[0] = 0
    #     point[1] = 0
    #     point[2] = 0
    # continue
prob_thr.sort()
for i in range(201):
    point = pointLst[i]
    if prob_thr[i] > 0.003:
        point[0] = 0
        point[1] = 0
        point[2] = 0
# Part 2: non-isolated outliers removal
def normalAverage(list):
    meanPoint = [0, 0, 0]
    for point in pointLst:
        meanPoint[0] += point[0]
        meanPoint[1] += point[1]
        meanPoint[2] += point[2]
    for m in meanPoint:
        m = m / len(pointLst)
    return meanPoint
def localFitPlane(ptList, k):
    mean = normalAverage(ptList)
    res = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    temp = []
    for pt in ptList:
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
    w, v = LA.eig(matrix)
    minEigInd = np.where(w == np.amin(w))
    eigTemp = v[minEigInd]
    norm = LA.norm(eigTemp)
    # print(eigTemp)
    eVec = []
    for v in eigTemp:
        v = v / norm
        eVec.append(v)
    # print(eVec[0])
    return eVec

for point in pointLst:
    knnInd = neighbors.kneighbors([point], 11, return_distance=False)
    knn = []
    for i in knnInd[0][1:]:
        knn.append(pointLst[i])
    normal = localFitPlane(knn, 10)
    # print(normal)
    for n in knn:
        sub = [0, 0, 0]
        sub[0] = n[0] - point[0]
        sub[1] = n[1] - point[1]
        sub[2] = n[2] - point[2]
        offset = normal[0][0] * sub[0] + normal[0][1] * sub[1] + normal[0][2] * sub[2]
        print(normal)
        n[0] -= offset * normal[0][0]
        n[1] -= offset * normal[0][1]
        n[2] -= offset * normal[0][2]
fout = open('filtered_data.txt', 'wt')
# Postprocess
for pt in pointLst:
    tempStr = str(pt)
    tempStr = tempStr.replace('[', '')
    tempStr = tempStr.replace(']', '')
    tempStr = tempStr.replace(',', '')
    fout.write(tempStr + "\n")
fout.close()
