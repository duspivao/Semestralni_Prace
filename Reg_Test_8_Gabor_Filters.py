import SimpleITK as sitk
import numpy as np
import cv2
import time

start = time.time()

outputDirPath = 'C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Reg_8_Gabor'



reader = sitk.ImageFileReader()
writer = sitk.ImageFileWriter()

reader.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/CT.nrrd')
imageR = reader.Execute()

caster = sitk.CastImageFilter()
caster.SetOutputPixelType(sitk.sitkUInt8)
image = caster.Execute(imageR)

#
# imArray = sitk.GetArrayFromImage(caster.Execute(imageR))
# coords = np.argwhere(imArray)
# x_min, y_min, z_min = coords.min(axis=0)
# x_max, y_max, z_max = coords.max(axis=0)
# cropped = imArray[x_min:x_max+1, y_min:y_max+1, z_min:z_max+1]
# image = sitk.GetImageFromArray(cropped)
#
# writer.SetFileName(outputDirPath+'liversSmall.nrrd')
# writer.Execute(image)


# A simple convolution function that returns the filtered images.
# def getFilterImages(filters, img):
#     featureImages = []
#     for filter in filters:
#         kern, params = filter
#         fimg = cv2.filter2D(img, cv2.CV_8UC3, kern)
#         featureImages.append(fimg)
#     return featureImages





size = 256
filter = sitk.GaborImageSource()
filter.SetOutputPixelType(sitk.sitkUInt8)

filters = []
for i in range(0,5,1):
    filter.SetSize([size]*3)
    filter.SetSigma([size*.2*(1+i)]*3)
    filter.SetMean([size*(0.5+i/10)]*3)
    filter.SetFrequency(.1+(i/10))
    filter.SetOutputPixelType(sitk.sitkUInt8)
    g = filter.Execute()
    filters.append(g)
    writer.SetFileName(outputDirPath + 'f'+str(i)+'.nrrd')
    writer.Execute(g)
print 'all fitleres prepared'

ide = 1
for kern in filters:
    print 'convolving no '+str(ide)
    print kern.GetDimension()
    print image.GetDimension()

    conv = sitk.ConvolutionImageFilter()
    conv.NormalizeOn()
    res = conv.Execute(image, kern)
    writer.SetFileName(outputDirPath + 'g'+str(ide)+'.nrrd')
    writer.Execute(res)
    ide += 1
#

# writer.SetFileName(outputDirPath+'g1.nrrd')
stop = time.time()

print stop-start