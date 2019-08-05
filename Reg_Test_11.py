import SimpleITK as sitk
import numpy as np
import time
import scipy.signal as sps
import sklearn.cluster as clstr
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import normalize
import math

totalStart = time.time()
"""Porovnani sitk convoluce a scipzy pro gabioy"""
reader = sitk.ImageFileReader()
reader.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/onlyLivers.nrrd')
imageR = reader.Execute()

outputDirPath = 'C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Reg_11_GaborSmaller'

writer = sitk.ImageFileWriter()
#
# rotation = itk.Versor
# angleInRadians = 60 * np.pi / 180.0



size = [11,11,11]

image = sitk.GetArrayFromImage(imageR)
gaborFilters = []

# for i in range(5):
#     gab = sitk.GaborImageSource()
#     rotation2 = sitk.VersorTransform((1,1,1), np.pi*0.2*i)
#     gab.SetDirection(rotation2.GetMatrix())
#     gaborFilters.append(sitk.GetArrayFromImage(gab.Execute()))
size = [7,7,7]
for i in range(5):
    gab = sitk.GaborImageSource()
    rotation2 = sitk.VersorTransform((1,1,1), np.pi*0.2*i)
    gab.SetDirection(rotation2.GetMatrix())
    gaborFilters.append(sitk.GetArrayFromImage(gab.Execute()))
    writer.SetFileName(outputDirPath+'f'+str(i)+'.nrrd')
print 'Gabor filter prepared'
print 'Counting convolutions'

convolutions = np.zeros(((len(gaborFilters), int(image.shape[0]), int(image.shape[1]), int(image.shape[2]))),dtype=np.int)

id = 0
for fiter in gaborFilters:
    conv = sps.convolve(image, fiter, mode='same')
    convolutions[id][:][:] = conv
    id += 1

print 'Computing features'
features = []
for x in range(image.shape[0]):
    for y in range(image.shape[1]):
        for z in range(image.shape[2]):

            feature = []
            feature.append( x )
            feature.append( y )
            feature.append( z )

            for i in range(convolutions.shape[0]):
                feature.append(convolutions[i][x][y][z])

            features.append(feature)

print 'Features prepared'
# print 'Features normalization'
# # normalization
# featuresId = 0
# featuresNorm = np.zeros(((len(gaborFilters), int(image.shape[0]), int(image.shape[1]), int(image.shape[2]))),dtype=np.float)
# for feat in features:
#     mean = feat.mean()
#     stddev = feat.std()
#     adjusted_stddev = max(stddev, 1.0/math.sqrt(feat.size))
#     featuresNorm[featuresId][:][:] = (feat - mean) / adjusted_stddev
#     featuresId += 1



print 'Clustering'

print 'Clustering K Means'
startKmeans = time.time()
kmeans = clstr.KMeans()
kmeans.fit(features[:][3:])
labels = kmeans.labels_
print 'Clustering DONE'
output = np.zeros(image.shape)
stopKmeans = time.time()
print 'Time>'+str(stopKmeans-startKmeans)





print 'Clustering Gaussian mixtures'
startGaussMix = time.time()
gaussMix = GaussianMixture(n_components=5)
gaussMix.fit(features[:][3:])
labels2 = gaussMix.predict(features[:][3:])
# gaussMix.predict(test2[:][2:])
print 'Clustering DONE'
output2 = np.zeros(image.shape)
stopGaussMix = time.time()
print 'Time>'+str(stopGaussMix-startGaussMix)
print 'Preparing output images'


for i in range(len(labels)):
    output[int(features[i][0])][int(features[i][1])][int(features[i][2])] = labels[i]
for i in range(len(labels2)):
    output2[int(features[i][0])][int(features[i][1])][int(features[i][2])] = labels2[i]


output *= 255.0/output.max()
output2 *= 255.0/output2.max()

writer.SetFileName(outputDirPath+'KMeans.nrrd')
writer.Execute(sitk.GetImageFromArray(output))

writer.SetFileName(outputDirPath+'GaussMixture.nrrd')
writer.Execute(sitk.GetImageFromArray(output2))

print time.time()-totalStart