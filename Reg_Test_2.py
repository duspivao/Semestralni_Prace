import cv2
import SimpleITK as sitk
import os
import numpy as np
import datetime
import time as cas
import itk



startTime = cas.time()
mov = 'C:/ZCU/3Dircadb1/3Dircadb1.1/PATIENT_DICOM'
mask = 'C:/ZCU/3Dircadb1/3Dircadb1.1/MASKS_DICOM/liver'

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
rel_path = "RegistrationTests/"
st = datetime.datetime.now().strftime("%d_%m_%y_%H%M")
outputDirPath = rel_path+'test'
if not os.path.exists(outputDirPath):
    os.makedirs(outputDirPath)
abs_file_path = os.path.join(script_dir, outputDirPath+'/')


outFileName = 'Test_01.nrrd'
writer2 = sitk.ImageFileWriter()

def readDICOMSerieToImage(folder, *argv):
    """
    load DICOM serie from set folder and optionally save the image. This function also casts image to Int16, because MRI
    can be uInt16
    Args:
        folder - absolute path to resource DICOM folder
        *argv
            [0] - identifier = string that will be used as part of name in result image written by this function
            [1] - resultFolder = string - absolute path where should be saved 3D image in nrrd
            [2] - showImage = int 1/0 1=show image using sitk.Show; 0=don't show nothing
            [3] - save image = int 1/0 1=save image as nrrd
    """
    print("Reading DICOMs from directory:", folder)
    reader = sitk.ImageSeriesReader()

    dicom_names = reader.GetGDCMSeriesFileNames(folder)
    reader.SetFileNames(dicom_names)


    caster = sitk.CastImageFilter()
    caster.SetOutputPixelType(sitk.sitkFloat32)
    image = caster.Execute(reader.Execute())

    size = image.GetSize()
    print("Image size:", size[0], size[1], size[2])


    if len(argv) >= 2:
        identifier = argv[0]
        resultFolder = argv[1]

        nameOfResImgWithPath = resultFolder+identifier+'.nrrd'
        print("Writing image:", nameOfResImgWithPath)
        if len(argv) >= 4:
            if argv[3] == 0:
                return image
            else:
                sitk.WriteImage(image, nameOfResImgWithPath)

        if len(argv) > 2:
            if argv[2] == 1:
                sitk.Show(sitk.ReadImage('C:/Users/duso/PycharmProjects/Semestralni_Prace/Old_tests/Results3/26_07_19_1111/MRI.nrrd'), 'test')
        return image

imageT = readDICOMSerieToImage(mov,'MRI',abs_file_path,0 ,0)



nImg = sitk.GetArrayFromImage(imageT)
mask = readDICOMSerieToImage(mask,'MRI',abs_file_path,0 ,0)
nMask = sitk.GetArrayFromImage(mask)
imageArr = nMask*nImg
writer2.SetFileName(outputDirPath + '/' + 'onlyLivers.nrrd')
writer2.Execute(sitk.GetImageFromArray(imageArr))


aheFilter = sitk.AdaptiveHistogramEqualizationImageFilter()

aheFilter.SetRadius([3,3,3])
imgFiltered = aheFilter.Execute(sitk.GetImageFromArray(imageArr))

writer2.SetFileName(outputDirPath + '/' + outFileName)
writer2.Execute(imgFiltered)


# applying alternate sequential filtering (3 times closing opening)
r1 = cv2.morphologyEx(sitk.GetArrayFromImage(imgFiltered), cv2.MORPH_OPEN,
                      cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=1)
writer2.SetFileName(outputDirPath + '/' + 'Test_02.nrrd')
writer2.Execute(sitk.GetImageFromArray(r1))

R1 = cv2.morphologyEx(r1, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=1)
writer2.SetFileName(outputDirPath + '/' + 'Test_03.nrrd')
writer2.Execute(sitk.GetImageFromArray(R1))

r2 = cv2.morphologyEx(R1, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)), iterations=1)
writer2.SetFileName(outputDirPath + '/' + 'Test_04.nrrd')
writer2.Execute(sitk.GetImageFromArray(r2))

R2 = cv2.morphologyEx(r2, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)), iterations=1)
writer2.SetFileName(outputDirPath + '/' + 'Test_05.nrrd')

writer2.Execute(sitk.GetImageFromArray(R2))
r3 = cv2.morphologyEx(R2, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (23, 23)), iterations=1)
writer2.SetFileName(outputDirPath + '/' + 'Test_06.nrrd')
writer2.Execute(sitk.GetImageFromArray(r3))

R3 = cv2.morphologyEx(r3, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (23, 23)), iterations=1)
# f4 = cv2.subtract(R3, imgFiltered)
writer2.SetFileName(outputDirPath + '/' + 'Test_07.nrrd')
writer2.Execute(sitk.GetImageFromArray(R3))

subtractFilter = sitk.SubtractImageFilter()
subImg = subtractFilter.Execute(sitk.GetImageFromArray(R3),imgFiltered)
writer2.SetFileName(outputDirPath + '/' + 'Test_08.nrrd')
writer2.Execute(subImg)
f5 = aheFilter.Execute(subImg)
writer2.SetFileName(outputDirPath + '/' + 'Test_09.nrrd')
writer2.Execute(f5)

# dist_transform = cv2.distanceTransform(itk.GetArrayFromImage(f5),cv2.DIST_L2,5)
# ret, sure_fg = cv2.threshold(dist_transform,0.7*dist_transform.max(),255,0)
# f6 = itk.GetImageFromArray(sure_fg)
# PixelType = itk.ctype('signed short')
# Dimension = 3
#
ctif = sitk.GrayscaleMorphologicalClosingImageFilter()
f6 = ctif.Execute(f5)

# ImageType = itk.Image[PixelType, Dimension]
# KLMSegmentation = itk.ConnectedThresholdImageFilter[ImageType, ImageType].New()
# KLMSegmentation.SetInput(f5)
# f6 = KLMSegmentation.GetOutput()
writer2.SetFileName(outputDirPath + '/' + 'Test_09_2.nrrd')
writer2.Execute(f6)

mif = sitk.MeanImageFilter()
mif.SetRadius(3)
f6_2 = mif.Execute(f6)

mif.SetRadius(5)
f6_3 = mif.Execute(f6)

writer2.SetFileName(outputDirPath + '/' + 'Test_09_2_1.nrrd')
writer2.Execute(f6_2)
writer2.SetFileName(outputDirPath + '/' + 'Test_09_2_2.nrrd')
writer2.Execute(f6_3)



# f5 = imgFiltered
# removing very small contours through area parameter noise removal
treshHoldFilter = sitk.ThresholdImageFilter()
treshHoldFilter.SetLower(15)
treshHoldFilter.SetUpper(255)
f6 = treshHoldFilter.Execute(f5)
writer2.SetFileName(outputDirPath + '/' + 'Test_10.nrrd')
writer2.Execute(sitk.GetImageFromArray(r1))

# ret, f6 = cv2.threshold(f5, 15, 255, cv2.THRESH_BINARY)
# mask = np.ones(f5.shape[:2], dtype="uint8") * 255

contouFilter = sitk.BinaryContourImageFilter()
resTemp = contouFilter.Execute(sitk.Cast(f6, sitk.sitkUInt8))
writer2.SetFileName(outputDirPath + '/' + 'Test_11.nrrd')
writer2.Execute(sitk.GetImageFromArray(r1))

caster = sitk.CastImageFilter()
caster.SetOutputPixelType(sitk.sitkUInt8)


otsu = sitk.OtsuThresholdImageFilter()
OtsuRes = otsu.Execute(caster.Execute(f6))
writer2.SetFileName(outputDirPath + '/' + 'Test_12.nrrd')
writer2.Execute(OtsuRes)


# im2, contours, hierarchy = cv2.findContours(f6.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
# for cnt in contours:
#     if cv2.contourArea(cnt) <= 200:
#         cv2.drawContours(mask, [cnt], -1, 0, -1)
# im = cv2.bitwise_and(f5, f5, mask=mask)
# ret, fin = cv2.threshold(im, 15, 255, cv2.THRESH_BINARY_INV)
# newfin = cv2.erode(fin, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=1)
#
# # removing blobs of unwanted bigger chunks taking in consideration they are not straight lines like blood
# # vessels and also in an interval of area
# fundus_eroded = cv2.bitwise_not(newfin)
# xmask = np.ones(image.shape[:2], dtype="uint8") * 255
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

stopTime = cas.time()
print str(stopTime-startTime) + 'sec \n====KONEC===='