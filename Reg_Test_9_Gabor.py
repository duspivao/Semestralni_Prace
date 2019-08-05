import SimpleITK as sitk
import cv2
import numpy as np
import time
# import theano
import matplotlib.pyplot as plt
import math
import sklearn.cluster as clstr
from sklearn.mixture import GaussianMixture
# from sklearn import svm
from sklearn.cluster import AgglomerativeClustering


def constructFeatureVectors(featureImages, img):

    featureVectors = []
    height, width = img.shape
    for row in range(height):
        for col in range(width):
            featureVector = []
            featureVector.append(row)
            featureVector.append(col)
            for featureImage in featureImages:
                featureVector.append(float(featureImage[row][col]))
            featureVectors.append(featureVector)

    return featureVectors


def normalizeData(featureVectors, setMeanToZero, spatialWeight=1):

    means = []
    for col in range(0, len(featureVectors[0])):
        colMean = 0
        for row in range(0, len(featureVectors)):
            colMean += featureVectors[row][col]
        colMean /= len(featureVectors)
        means.append(colMean)

    for col in range(2, len(featureVectors[0])):
        for row in range(0, len(featureVectors)):
            featureVectors[row][col] -= means[col]
    copy = vq.whiten(featureVectors)
    if (setMeanToZero):
        for row in range(0, len(featureVectors)):
            for col in range(0, len(featureVectors[0])):
                copy[row][col] -= means[col]

    for row in range(0, len(featureVectors)):
        copy[row][0] *= spatialWeight
        copy[row][1] *= spatialWeight

    return copy



window_sizes = [64,32,16, 8,6,5, 4, 3]
gabor_sigma=[1.0,2.0,3.0,4.0]
gabor_lambda=0.1
gabor_gamma=0.02
gabor_psi=0
# gabor_thetas=[np.pi / 4, np.pi / 2]
# gabor_thetas=[np.pi / 4, np.pi / 2, 3 * np.pi / 4, np.pi, np.pi/6, 2*np.pi/6,4*np.pi/6,5*np.pi/6]
gabor_thetas = []
for i in range(10):
    gabor_thetas.append(np.pi*i/10)

start = time.time()

outputDirPath = 'C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Reg_8_Gabor'

reader = sitk.ImageFileReader()
writer = sitk.ImageFileWriter()

reader.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Reg_8_GaborliversSmall.nrrd')
imageR = reader.Execute()

caster = sitk.CastImageFilter()
caster.SetOutputPixelType(sitk.sitkUInt8)
image = sitk.GetArrayFromImage(caster.Execute(imageR))

print image.shape
test = image[51, :, :]
# imgplot = plt.imshow(test,cmap='gray')
# plt.show()

num_windows = int(math.pow(image.shape[0], 2) // 4)


krenels = []
means = []
std = []
resArr = []
test = cv2.getGaborKernel((32,32,32), sigma=1, theta=np.pi/10, lambd=0.2, gamma=0.02, psi=0, ktype=cv2.CV_32F)
for sigma in gabor_sigma:
    for size in window_sizes:
        for gabor_theta in gabor_thetas:

            g_kernel = cv2.getGaborKernel((size,size), sigma=sigma, theta=gabor_theta, lambd=gabor_lambda, gamma=gabor_gamma, psi=gabor_psi, ktype=cv2.CV_32F)
            # imgplot = plt.imshow(resu,cmap='gray')
            # plt.show()

            krenels.append(g_kernel)
featureID = 0
resFeauterUnNormalized = np.zeros((len(krenels),test.shape[0],test.shape[1]), dtype=np.float )

for mask in krenels:

    resu = cv2.filter2D(test, cv2.CV_8U, mask)
    # imgplot = plt.imshow(resu,cmap='gray')
    # plt.show()
    print 'vysl>'+str(resu.shape)+' kernel>'+str(mask.shape)+' img>'+str(test.shape)
    resArr.append(resu)
    resFeauterUnNormalized[featureID,:,:] = resu
    featureID += 1

test2 = constructFeatureVectors(resArr,test)


for col in range(0, len(test2[0])):
    colMean = 0
    for row in range(0, len(test2)):
        colMean += test2[row][col]
    colMean /= len(test2)
    means.append(colMean)
print test2[1500]
print resFeauterUnNormalized.shape
test3=[]

for i in range(resFeauterUnNormalized.shape[0]):
    test3.append(resFeauterUnNormalized[i][4][132])


print test3

if test2[1500][2:] == test3:
    print 'heureka'

print 'Clustering K Means'
startKmeans = time.time()
kmeans = clstr.KMeans()
kmeans.fit(test2[:][2:])
labels = kmeans.labels_
output = np.zeros(test.shape)
stopKmeans = time.time()
print 'Time>'+str(stopKmeans-startKmeans)
print 'Clustering Gaussian mixtures'
startGaussMix = time.time()
gm_messy = GaussianMixture(max(list(labels))).fit(test2[:][2:]).predict(test2[:][2:])
output2 = np.zeros(test.shape)
stopGaussMix = time.time()
print 'Time>'+str(stopGaussMix-startGaussMix)


for i in range(len(labels)):
    output[int(test2[i][0])][int(test2[i][1])] = labels[i]
for i in range(len(gm_messy)):
    output2[int(test2[i][0])][int(test2[i][1])] = gm_messy[i]


output *= 255.0/image.max()
output2 *= 255.0/image.max()
f = plt.figure()
f.add_subplot(1,2, 1)
plt.imshow(output,cmap='gray')
# plt.show()
f.add_subplot(1,2, 2)
plt.imshow(output2,cmap='gray')
plt.show()

print '===TEST==='