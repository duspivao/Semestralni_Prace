import SimpleITK as sitk
import time
outputDirPath = 'C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Reg_7_'
start = time.time()


reader = sitk.ImageFileReader()

reader.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/onlyLivers.nrrd')
imageR = reader.Execute()

caster = sitk.CastImageFilter()
caster.SetOutputPixelType(sitk.sitkUInt8)
image = caster.Execute(imageR)
# thresholdFilter = sitk.ThresholdImageFilter()
# thresholdFilter.SetLower(4000.0)
# tImg = thresholdFilter.Execute(image)
writer = sitk.ImageFileWriter()
writer.SetFileName(outputDirPath+'Source.nrrd')
writer.Execute(image)

# test = sitk.ConnectedThreshold(image, seedList=[(165,263,101),(114,246,120)], lower=100, upper=255)
test = sitk.ConfidenceConnected(image, seedList=[(165,263,101),(114,246,120)],
                                    numberOfIterations=5,
                                    multiplier=2.,
                                    initialNeighborhoodRadius=3,
                                    replaceValue=1)



writer.SetFileName(outputDirPath+'RES.nrrd')
writer.Execute(test)
stop = time.time()

print stop-start