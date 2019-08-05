import cv2
import SimpleITK as sitk
import numpy as np

reader = sitk.ImageFileReader()

reader.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/onlyLivers.nrrd')
image = reader.Execute()
outputDirPath = 'C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Reg_5_'

writer = sitk.ImageFileWriter()


caster = sitk.CastImageFilter()
caster.SetOutputPixelType(sitk.sitkUInt8)

treshHoldFilter = sitk.ThresholdImageFilter()
treshHoldFilter.SetLower(15)
treshHoldFilter.SetUpper(255)
f6 = treshHoldFilter.Execute(image)
writer.SetFileName(outputDirPath+'01.nrrd')
writer.Execute(f6)


# # removing very small contours through area parameter noise removal
# ret, f6 = cv2.threshold(f5, 15, 255, cv2.THRESH_BINARY)

# mask = np.ones(sitk.GetArrayFromImage(image).shape[:2], dtype="uint8") * 255
# # imgArray = .astype("uint8")
# # imgArray = cv2.normalize(src=sitk.GetArrayFromImage(f6), dst=None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
# # print np.amax(imgArray)
# # print np.amin(imgArray)

otsu = sitk.OtsuThresholdImageFilter()
OtsuRes = otsu.Execute(caster.Execute(image))

# blur = sitk.CurvatureFlowImageFilter()
blur = sitk.ConnectedComponentImageFilter()
# blur.SetNumberOfIterations(10)

cont = sitk.GrayscaleErodeImageFilter()
# cont.SetRadius(7)
cont.SetKernelType(sitk.sitkBall)
f7 = cont.Execute(blur.Execute(OtsuRes))
writer.SetFileName(outputDirPath+'02.nrrd')

writer.Execute(f7)

writer.SetFileName(outputDirPath+'03.nrrd')

writer.Execute(blur.Execute(OtsuRes))




# im2, contours, hierarchy = cv2.findContours(cv2.threshold(imgArray,0,255,cv2.THRESH_BINARY),
#                                             cv2.RETR_LIST,
#                                             cv2.CHAIN_APPROX_SIMPLE)
# # for cnt in contours:
#     if cv2.contourArea(cnt) <= 200:
#         cv2.drawContours(mask, [cnt], -1, 0, -1)
# im = cv2.bitwise_and(f5, f5, mask=mask)
# ret, fin = cv2.threshold(im, 15, 255, cv2.THRESH_BINARY_INV)
# newfin = cv2.erode(fin, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=1)
#
# # removing blobs of unwanted bigger chunks taking in consideration they are not straight lines like blood
# # vessels and also in an interval of area
# fundus_eroded = cv2.bitwise_not(newfin)
# xmask = np.ones(fundus.shape[:2], dtype="uint8") * 255
# x1, xcontours, xhierarchy = cv2.findContours(fundus_eroded.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
# for cnt in xcontours:
#     shape = "unidentified"
#     peri = cv2.arcLength(cnt, True)
#     approx = cv2.approxPolyDP(cnt, 0.04 * peri, False)
#     if len(approx) > 4 and cv2.contourArea(cnt) <= 3000 and cv2.contourArea(cnt) >= 100:
#         shape = "circle"
#     else:
#         shape = "veins"
#     if (shape == "circle"):
#         cv2.drawContours(xmask, [cnt], -1, 0, -1)
#
# finimage = cv2.bitwise_and(fundus_eroded, fundus_eroded, mask=xmask)
# blood_vessels = cv2.bitwise_not(finimage)
# return blood_vessels