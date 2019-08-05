import SimpleITK as sitk
import cv2
import numpy as np
import time
import matplotlib.pyplot as plt
# import theano
import matplotlib.pyplot as plt
import math
import sklearn.cluster as clstr
from sklearn.mixture import GaussianMixture
print cv2.__version__

start = time.time()

outputDirPath = 'C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Thresh_'

reader = sitk.ImageFileReader()
writer = sitk.ImageFileWriter()

reader.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Reg_8_GaborliversSmall.nrrd')
imageR = reader.Execute()

caster = sitk.CastImageFilter()
caster.SetOutputPixelType(sitk.sitkUInt8)

gauss = sitk.SmoothingRecursiveGaussianImageFilter()
gauss.SetGlobalDefaultCoordinateTolerance(10)
print gauss.GetSigma()
gauss.SetSigma(2)
gausRes =gauss.Execute(caster.Execute(imageR))
writer.SetFileName(outputDirPath+'01.nrrd')
writer.Execute(gausRes)

# ahe = sitk.AdaptiveHistogramEqualizationImageFilter ()
# ahe.Execute(gausRes)
# writer.SetFileName(outputDirPath+'02.nrrd')
# writer.Execute(sitk.RescaleIntensity(ahe.Execute(gausRes)))

conn = sitk.ConnectedThresholdImageFilter()
conn.SetSeedList([(96,156,37),(113,90,53)])
conn.SetConnectivity(6)
conn.SetUpper(90)
conn.SetLower(0)
testRegionGrow = conn.Execute(gausRes)
tt = sitk.GetArrayFromImage(testRegionGrow)
# xx = np.ones((15,15,15))*255
writer.SetFileName(outputDirPath+'growReg01.nrrd')
writer.Execute(testRegionGrow)

npImage = sitk.GetArrayFromImage(imageR)
npImage[96:96+15][156:156+15][37:37+15] = 255
otsu = sitk.OtsuThresholdImageFilter()
otsu.SetInsideValue(1)
otsu.SetOutsideValue(0)
resOtsu = otsu.Execute(caster.Execute(sitk.RescaleIntensity(imageR)))



arraRes = sitk.GetArrayFromImage(resOtsu)
# for x in range(arraRes.shape[0]):
#     for y in range(arraRes.shape[1]):
#         for z in range(arraRes.shape[2]):
#             if arraRes[x][y][z] > 0:
#                 print str(x)+ ','+str(y)+ ','+str(z)


conn.ClearSeeds()
conn.SetSeed((90,100,46))
conn.SetLower(-1)
conn.SetUpper(100)
conn.SetReplaceValue(255)
conn.SetNumberOfThreads(1)
conn.SetConnectivity(6)
testRegionGrowOtsu = conn.Execute(resOtsu)
writer.SetFileName(outputDirPath+'resOtsuGrow.nrrd')
writer.Execute(sitk.RescaleIntensity(conn.Execute(resOtsu)))