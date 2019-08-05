import SimpleITK as sitk
import cv2
import numpy as np
import time
import matplotlib.pyplot as plt


print cv2.__version__

start = time.time()

outputDirPath = 'C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Thresh_'

reader = sitk.ImageFileReader()
writer = sitk.ImageFileWriter()

reader.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Reg_8_GaborliversSmall.nrrd')
imageR = reader.Execute()

caster = sitk.CastImageFilter()
caster.SetOutputPixelType(sitk.sitkUInt8)
image = caster.Execute(imageR)

size = image.GetSize()
# seed = (96,156,37)
seed = (90,152,32)
seg = sitk.Image(image.GetSize(), sitk.sitkUInt8)
seg.CopyInformation(image)
seg[seed] = 1
seg = sitk.BinaryDilate(seg, 5)
seg = sitk.RescaleIntensity(seg,0,255)
writer.SetFileName(outputDirPath+'seed.nrrd')
writer.Execute(seg)

seg_con = sitk.ConnectedThreshold(image, seedList=[seed],
                                  lower=10, upper=100)
writer.SetFileName(outputDirPath+'connected_Seg.nrrd')
writer.Execute(sitk.RescaleIntensity(seg_con))


# automatic find

liversOnlyArray = sitk.GetArrayFromImage(image) > 0
otsuThresholdFilter = sitk.OtsuThresholdImageFilter()
otsuThresholdFilter.SetInsideValue(1)
otsuThresholdFilter.SetOutsideValue(0)
thresholdedImage = otsuThresholdFilter.Execute(image)

writer.SetFileName(outputDirPath+'thresholdedLivers.nrrd')
writer.Execute(thresholdedImage)

thresholdedImageArr = sitk.GetArrayFromImage(thresholdedImage) * liversOnlyArray


gaussFil = sitk.SmoothingRecursiveGaussianImageFilter()
print gaussFil.GetSigma()
gaussFil.SetSigma(2)
bluered = gaussFil.Execute(image)
writer.SetFileName(outputDirPath+'bluered.nrrd')
writer.Execute(bluered)

forContourTest = sitk.GetArrayFromImage(bluered)[53][:][:]
# cannyEdges = cv2.Canny(forContourTest,50,100)
# cannyEdgesImages = cannyEdges.Execute(bluered)




# plt.imshow(np.uint8(forContourTest), cmap='gray')
# plt.show()

edges = cv2.Canny(forContourTest.astype(np.uint8), 10, 70)
plt.imshow(edges, cmap='gray')
plt.show()


# plt.imshow(np.uint8(edges), cmap='gray')
# plt.show()

cannyFilter = sitk.CannyEdgeDetectionImageFilter()
cannyFilter.SetLowerThreshold(1)
cannyFilter.SetUpperThreshold(150)
cannyImage = cannyFilter.Execute(sitk.Cast(bluered, sitk.sitkFloat64))


edges1 = sitk.CannyEdgeDetection(bluered, lowerThreshold=1, upperThreshold=100,
                                 variance=[1, 1, 1])


writer.SetFileName(outputDirPath+'cannyImage.nrrd')
writer.Execute(sitk.RescaleIntensity(edges1))



# contours, hierarchy = cv2.findContours(thresholdedImageArr[53][:][:],cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
contours, hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)

# slice = sitk.GetArrayFromImage(caster.Execute(cannyImage))[53][:][:]
contours1 = contours[0].reshape(-1,2)

# cv2.drawContours(forContourTest, contours, -1, (255,255,255), 3)
id = 0
hull_list = []
for cont in contours:

    print cont.size
    area = cv2.contourArea(cont)
    print area
    if area >1 and area < 100:

        print area

        # ellipse = cv2.fitEllipse(cont)
        M = cv2.moments(cont)
        print M
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

        # mask = np.zeros(forContourTest.shape, np.uint8)
        dd = forContourTest.copy()
        cv2.drawContours(dd, contours, id, (255,255,255), -1)
        plt.imshow(dd, cmap='gray')
        plt.show()
        # cv2.circle(forContourTest, (cX,cY), 3, (0,255,0), thickness=1, lineType=8, shift=0)
        # cv2.putText(forContourTest,str(id), (x,y), cv2.FONT_HERSHEY_SIMPLEX, 1, 255)

        # hull = cv2.convexHull(cont)
        # hull_list.append(hull)

        id += 1
# cv2.drawContours(forContourTest, hull_list, -1, (255,255,255), 3)
plt.imshow(forContourTest, cmap='gray')
plt.show()


# ccc = contours[10]
# for point in ccc:
#     x = point[0][0]
#     y = point[0][1]
#     print point.size
#     cv2.circle(forContourTest, (x, y), 3, (255, 255, 255), thickness=1, lineType=8, shift=0)
#     cv2.putText(forContourTest, str(id), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, 255)
#     id += 1
# plt.imshow(np.uint8(forContourTest), cmap='gray')
# plt.show()
# plt.imshow(forContourTest, cmap='gray')
# plt.show()

# for (x, y) in contours1:
#     cv2.circle(forContourTest, (x, y), 1, (255, 0, 0), 3)
#     cv2.imshow('Output', forContourTest)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
con2 = []

# plt.imshow(edges, cmap='gray'
# plt.show()
# for c in contours:
#     if c.
# for c in contours:
#     if c.size < 10:
#         contours.remove(c)


# cnt = contours[94]
# M = cv2.moments(cnt)
# print( M )
# cx = int(M['m10']/M['m00'])
# cy = int(M['m01']/M['m00'])
# area = cv2.contourArea(cnt)
# empty = np.zeros(thresholdedImageArr.shape)
# # empty[cx-25:cx+25][cy-25:cy+25] = 255
# i = cv2.imread(outputDirPath+'seedTest.png')
# cv2.drawContours(i, contours, 94, (255,0,0),cv2.cv.CV_FILLED, 8, hierarchy )
# # cv2.drawContours(empty, contours, 78, (0,255,0), 3)
# writer.SetFileName(outputDirPath+'seedTest.png')
# writer.Execute(caster.Execute(sitk.GetImageFromArray(i)))

# print str(cx) + ' - ' +str(cy)+' size' + str(area)

