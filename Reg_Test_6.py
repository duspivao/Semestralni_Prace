import datetime
# from skimage.filters import frangi, hessian
import itk
import SimpleITK as sitk
import time

start = time.time()


reader = sitk.ImageFileReader()

reader.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/onlyLivers.nrrd')
image = reader.Execute()
outputDirPath = 'C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Reg_6_'
radius = 3
medianFilter = sitk.MedianImageFilter()
medianFilter.SetRadius(radius)
adaptiveFilter = sitk.AdaptiveHistogramEqualizationImageFilter()
adaptiveFilter.SetRadius(radius)

morphCloseFilter = sitk.GrayscaleMorphologicalClosingImageFilter()
morphCloseFilter.SetKernelRadius(radius)
morphCloseFilter.SetKernelType(sitk.sitkBall)
morphOpenFilter = sitk.GrayscaleMorphologicalOpeningImageFilter()
morphOpenFilter.SetKernelRadius(radius)
# morphOpenFilter.SetKernelType(sitk.sitkBall)
writer = sitk.ImageFileWriter()
r1 = medianFilter.Execute(image)
writer.SetFileName(outputDirPath+'r1.nrrd')
writer.Execute(r1)
r2 = adaptiveFilter.Execute(r1)
writer.SetFileName(outputDirPath+'r2.nrrd')
writer.Execute(r2)
r3 = morphOpenFilter.Execute(r2)
writer.SetFileName(outputDirPath+'r3.nrrd')
writer.Execute(r3)
r4 = morphCloseFilter.Execute(r3)



writer.SetFileName(outputDirPath+'RES.nrrd')
writer.Execute(r4)
stop = time.time()

print stop-start
# Gabor filter?
