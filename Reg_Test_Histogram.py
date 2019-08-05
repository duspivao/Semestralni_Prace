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

outputDirPath = 'C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Otsu_'

reader = sitk.ImageFileReader()
writer = sitk.ImageFileWriter()

reader.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Reg_8_GaborliversSmall.nrrd')
imageR = reader.Execute()

caster = sitk.CastImageFilter()
caster.SetOutputPixelType(sitk.sitkUInt8)

otsu = sitk.OtsuThresholdImageFilter()
otsu.SetInsideValue(1)
otsu.SetOutsideValue(0)
res = otsu.Execute(caster.Execute(sitk.RescaleIntensity(imageR)))
print otsu.GetThreshold()
writer.SetFileName(outputDirPath+'res.nrrd')
writer.Execute(sitk.LabelOverlay(caster.Execute(sitk.RescaleIntensity(imageR)),sitk.RescaleIntensity( res)))
res = otsu.Execute(caster.Execute(sitk.RescaleIntensity(imageR)))

writer.SetFileName(outputDirPath+'res2.nrrd')
writer.Execute(sitk.RescaleIntensity( res))

# temp = sitk.GetArrayFromImage(res)
# res2 = cv2.fastNlMeansDenoising(temp)

gauss = sitk.SmoothingRecursiveGaussianImageFilter()
gauss.SetGlobalDefaultCoordinateTolerance(10)
res2 = gauss.Execute(res)
writer.SetFileName(outputDirPath+'res3.nrrd')
writer.Execute(sitk.RescaleIntensity( res2))



oneSlice = np.uint8(sitk.GetArrayFromImage(sitk.RescaleIntensity(res2))[53][:][:])
kernel = np.ones((3,3),np.uint8)
opening = cv2.morphologyEx(oneSlice,cv2.MORPH_OPEN,kernel, iterations = 2)
# plt.imshow(opening,cmap='gray')
# plt.show()
cont = sitk.BinaryContourImageFilter()
cont.SetFullyConnected(False)

cRes = cont.Execute(sitk.RescaleIntensity(caster.Execute(res2)))
writer.SetFileName(outputDirPath+'cont.nrrd')
writer.Execute(cRes)



bmcif = sitk.BinaryMorphologicalClosingImageFilter()
bmcif.SetKernelType(sitk.sitkBall)
bmcif.SetKernelRadius(3)
test = sitk.RescaleIntensity(bmcif.Execute(caster.Execute(res)))
writer.SetFileName(outputDirPath+'bmcif.nrrd')
writer.Execute(test)
test2 = gauss.Execute(test)
writer.SetFileName(outputDirPath+'bmcif2.nrrd')
writer.Execute(test)

seg_con = sitk.ConnectedThreshold(sitk.RescaleIntensity(caster.Execute(imageR)), seedList=[(126,106,51),(130,168,46)],
                                  lower=100, upper=190)

writer.SetFileName(outputDirPath+'regGrow.nrrd')
writer.Execute(sitk.RescaleIntensity(seg_con))
# sure_bg = cv2.dilate(opening,kernel,iterations=3)
# # plt.imshow(sure_bg,cmap='gray')
# # plt.show()
# # Finding sure foreground area
# dist_transform = cv2.distanceTransform(np.uint8(opening), cv2.cv.CV_DIST_L2,5)
# ret, sure_fg = cv2.threshold(dist_transform,0.7*dist_transform.max(),255,0)
#
# # Finding unknown region
# sure_fg = np.uint8(sure_fg)
# unknown = 1-cv2.subtract(np.uint8(sure_bg), sure_fg)
#
# contours, hierarchy = cv2.findContours(np.uint8(sitk.GetArrayFromImage(sitk.RescaleIntensity(res2))[53][:][:]),cv2.RETR_TREE,cv2.CHAIN_APPROX_TC89_L1)
# x = np.zeros(oneSlice.shape)
# cv2.drawContours(x, contours, -1, ( 255,255,255 ))
# plt.imshow(x, cmap='gray')
# plt.show()
#
# for c in contours:
#     # calculate moments for each contour
#     M = cv2.moments(c)
#     print M
#     # calculate x,y coordinate of center
#     if M["m00"] != 0:
#         cX = int(M["m10"] / M["m00"])
#         cY = int(M["m01"] / M["m00"])
#         cv2.circle(oneSlice, (cX, cY), 5, (255, 255, 255), -1)
#     # cv2.putText(oneSlice, "centroid", (cX - 25, cY - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
#
#     # display the image
#         cv2.imshow("Image", oneSlice)
#         cv2.waitKey(0)
# image = sitk.GetArrayFromImage(caster.Execute(imageR))
#
# print image.shape
# test = image[51, :, :]
#
# test *= 255/test.max()
#
# ret, otsu = cv2.threshold(test,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
#
# plt.imshow(otsu,cmap='gray')
# plt.show()
# # plt.hist(test, bins='auto')
# # plt.show()