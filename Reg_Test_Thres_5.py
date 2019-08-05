import SimpleITK as sitk
import cv2
import numpy as np
from matplotlib import pyplot as plt
from skimage import morphology

outputDirPath = 'C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/ZZZ_'

reader = sitk.ImageFileReader()
writer = sitk.ImageFileWriter()

reader.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Reg_8_GaborliversSmall.nrrd')
imageR = reader.Execute()

caster = sitk.CastImageFilter()
caster.SetOutputPixelType(sitk.sitkUInt8)

imageUint8 = caster.Execute(imageR)
thresholdFilter = sitk.ThresholdImageFilter()

thresholdFilter.SetLower(30)
thresholdFilter.SetUpper(100)
thresholdFilter.SetOutsideValue(0)
# thresholdFilter.SetInsideValue(0)
thresholdedImage = thresholdFilter.Execute(imageUint8)


radius = (3,3,3)

erode = sitk.GrayscaleErodeImageFilter()
dilate = sitk.GrayscaleDilateImageFilter()
erode.SetKernelRadius((3,3,3))
dilate.SetKernelRadius((2,2,2))

res = erode.Execute(dilate.Execute(thresholdedImage))
# res = dilate.Execute(erode.Execute(thresholdedImage))


writer = sitk.ImageFileWriter()


numpyImage = sitk.GetArrayFromImage(thresholdedImage)
plt.imshow(numpyImage[53][:][:], cmap='gray')
plt.show()
binarized = np.where(numpyImage>0, 1, 0)
plt.imshow(binarized[53][:][:], cmap='gray')
plt.show()

print numpyImage.shape
print binarized.shape
res2 = morphology.remove_small_objects(binarized.astype(bool), min_size=20, connectivity=2).astype(int)
plt.imshow(res2[53][:][:], cmap='gray')
plt.show()

res2Img = sitk.GetImageFromArray(res2)

writer.SetFileName(outputDirPath+'thr.nrrd')
writer.Execute(sitk.RescaleIntensity(thresholdedImage))
writer.SetFileName(outputDirPath+'afterMorph.nrrd')
writer.Execute(sitk.RescaleIntensity(res))
writer.SetFileName(outputDirPath+'afterMorph2.nrrd')
writer.Execute(sitk.RescaleIntensity(res2Img))


# imgArray = sitk.GetArrayFromImage(imageUint8)
# sliceX = imgArray[53][:][:]
#
# clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(5,5))
# cl1 = clahe.apply(sliceX)
# oneSliceDenoised = cl1.copy()
# cv2.fastNlMeansDenoising(cl1, oneSliceDenoised, h=40)
# plt.imshow(oneSliceDenoised, cmap='gray')
# plt.show()
#
# # hist = cv2.calcHist(oneSliceDenoised,[0],None,[256],[0,256])
# # plt.hist(oneSliceDenoised.ravel(),256,[20,256])
# # plt.show()
# # hist = cv2.calcHist([cl1],[0],None,[256],[0,256])
#
# ret,thresh1 = cv2.threshold(sliceX,70,110,cv2.THRESH_BINARY_INV)
# thresh = thresh1.copy()
# cv2.fastNlMeansDenoising(cl1, oneSliceDenoised, h=40)
# thresh2 = thresh.copy()
# thresh2 = cv2.GaussianBlur(thresh, ksize=5, sigmaX=1, sigmaY=1)
#
# plt.imshow(thresh2, cmap='gray')
# plt.show()