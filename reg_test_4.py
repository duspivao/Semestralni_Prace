import SimpleITK as sitk
# import cv2
import numpy

reader = sitk.ImageFileReader()

reader.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Test_11.nrrd')
image = reader.Execute()
outputDirPath = 'C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test'
treshHoldFilter = sitk.ThresholdImageFilter()
treshHoldFilter.SetLower(1500)
print  numpy.amax(sitk.GetArrayFromImage(image))
treshHoldFilter.SetUpper(1000000.0)
f6 = treshHoldFilter.Execute(image)

writer2 = sitk.ImageFileWriter()
writer2.SetFileName(outputDirPath + '/' + 'Test_X10.nrrd')
writer2.Execute(f6)
#
# caster = sitk.CastImageFilter()
# caster.SetOutputPixelType(sitk.sitkUInt8)
# # otsu = sitk.OtsuThresholdImageFilter()
# # OtsuRes = otsu.Execute(caster.Execute(image))
# # print otsu.GetThreshold()
# # print otsu.GetInsideValue()
# # print otsu.GetOutsideValue()
# # #
# writer = sitk.ImageFileWriter()
# # writer.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Otsu_Threshold_Test.nrrd')
# # writer.Execute(OtsuRes)
# # #
# #
# # cont = sitk.BinaryContourImageFilter()
# # cont.SetFullyConnected(True)
# #
# # writer.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/orig.nrrd')
# # writer.Execute(caster.Execute(image))
# # writer.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Contour_Threshold_Test.nrrd')
# # cont.Execute(caster.Execute(image))
# # writer.Execute(cont.Execute(caster.Execute(image)))
#
# # f5 = imgFiltered
# # removing very small contours through area parameter noise removal
# treshHoldFilter = sitk.ThresholdImageFilter()
# treshHoldFilter.SetLower(15)
# treshHoldFilter.SetUpper(255)
# f6 = treshHoldFilter.Execute(caster.Execute(image))
# writer.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test' + '/' + 'Test_10.nrrd')
# writer.Execute(f6)
# cv2.cvtColor(sitk.GetArrayFromImage(caster.Execute(f6)), cv2.COLOR_BGR2GRAY)
# im2, contours, hierarchy = cv2.findContours(cv2.cvtColor(cv2sitk.GetArrayFromImage(caster.Execute(f6)), cv2.COLOR_BGR2GRAY),
#                                             cv2.RETR_LIST,
#                                             cv2.CHAIN_APPROX_SIMPLE
#                                             )
# # for cnt in contours:
# #     if cv2.contourArea(cnt) <= 200:
# #         cv2.drawContours(mask, [cnt], -1, 0, -1)
# # im = cv2.bitwise_and(f5, f5, mask=mask)
# # ret, fin = cv2.threshold(im, 15, 255, cv2.THRESH_BINARY_INV)
# # newfin = cv2.erode(fin, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=1)
# #
# # # removing blobs of unwanted bigger chunks taking in consideration they are not straight lines like blood
# # # vessels and also in an interval of area
# # fundus_eroded = cv2.bitwise_not(newfin)
# # xmask = np.ones(image.shape[:2], dtype="uint8") * 255
# # x1, xcontours, xhierarchy = cv2.findContours(fundus_eroded.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
# # for cnt in xcontours:
# #     shape = "unidentified"
# #     peri = cv2.arcLength(cnt, True)
# #     approx = cv2.approxPolyDP(cnt, 0.04 * peri, False)
# #     if len(approx) > 4 and cv2.contourArea(cnt) <= 3000 and cv2.contourArea(cnt) >= 100:
# #         shape = "circle"
# #     else:
# #         shape = "veins"
# #     if (shape == "circle"):
# #         cv2.drawContours(xmask, [cnt], -1, 0, -1)
# #
# # finimage = cv2.bitwise_and(fundus_eroded, fundus_eroded, mask=xmask)
# # blood_vessels = cv2.bitwise_not(finimage)