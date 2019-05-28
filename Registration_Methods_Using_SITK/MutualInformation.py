#!/usr/bin/env python
import os
import itk
import sys
import datetime
import SimpleITK as sitk


########SETUP PARAMETER AND INPUTS FOR REGISTRATION#####
# Input direction for fixed image
label = 'LABELLED_DICOM'
inputFixDirName = 'C:/ZCU/3Dircadb1/3Dircadb1.1/'+label

# Input dircection for moving image
label = 'LABELLED_DICOM'
inputMovDirName = 'C:/ZCU/3Dircadb1/3Dircadb1.7/'+label


# Output direction
# Subfolder with timestamp will be created
outputDirPath = 'C:/ZCU/Results/'
st = datetime.datetime.now().strftime("%d_%m_%y_%H%M")
outputDirPath = outputDirPath+st
if not os.path.exists(outputDirPath):
    os.makedirs(outputDirPath)

# Parameters of registration
numberOfBins = 10
samplingPercentage = 0.20

# Function for read DICOM Images from DIR, and save in nrrd image file
# This function also save image to 3D in format nrrd for next transform
def readDICOMImage(dir, outPutDir, identifier):
    PixelType = itk.ctype('signed short')
    Dimension = 3

    ImageType = itk.Image[PixelType, Dimension]


    namesGenerator = itk.GDCMSeriesFileNames.New()
    namesGenerator.SetUseSeriesDetails(False)
    namesGenerator.SetGlobalWarningDisplay(False)
    namesGenerator.SetDirectory(dir)

    seriesUID = namesGenerator.GetSeriesUIDs()

    if len(seriesUID) < 1:
        print('ERROR: No DICOMS in folder' + dir)
        sys.exit(1)
    if len(seriesUID) > 1:
        print('ERROR: In folder are more series')
        sys.exit(1)
    print('DICOMs red OK from: ' + dir)



    # SHOULD BE just one
    for uid in seriesUID:
        seriesIdentifier = uid

        print('Reading: ' + seriesIdentifier)
        fileNames = namesGenerator.GetFileNames(seriesIdentifier)

        reader = itk.ImageSeriesReader[ImageType].New()
        dicomIO = itk.GDCMImageIO.New()
        reader.SetImageIO(dicomIO)
        reader.SetFileNames(fileNames)

        outFileName = 'DIC_' + identifier + '.nrrd'
        writer = itk.ImageFileWriter[ImageType].New()
        writer.SetFileName(outPutDir+'/'+outFileName)
        writer.UseCompressionOn()
        writer.SetInput(reader.GetOutput())

        print('Writing: ' + outPutDir+'/'+outFileName)
        writer.Update()

        return sitk.ReadImage(outPutDir+'/'+outFileName, sitk.sitkFloat32)

def observer(method) :
    print("{0:3}: Value of metric{1:10.5f}; Optimizer position \t#: ".format(method.GetOptimizerIteration(),
                                           method.GetMetricValue(),
                                           method.GetOptimizerPosition()))

fixImg = readDICOMImage(inputFixDirName,outputDirPath,'FIX')
movImg = readDICOMImage(inputMovDirName,outputDirPath,'MOC')

registration = sitk.ImageRegistrationMethod()
registration.SetMetricAsMattesMutualInformation(numberOfBins)
registration.SetMetricSamplingPercentage(samplingPercentage,sitk.sitkWallClock)
registration.SetMetricSamplingStrategy(registration.RANDOM)
registration.SetOptimizerAsRegularStepGradientDescent(1.0,.001,200)
registration.SetInitialTransform(sitk.TranslationTransform(fixImg.GetDimension()))
registration.SetInterpolator(sitk.sitkLinear)

registration.AddCommand( sitk.sitkIterationEvent, lambda: observer(registration))

outTx = registration.Execute(fixImg, movImg)


print("-------")

print("Optimizer stop condition: {0}".format(registration.GetOptimizerStopConditionDescription()))
print(" Number of iterations: {0}".format(registration.GetOptimizerIteration()))
print(" Final Metric value: {0}".format(registration.GetMetricValue()))
sitk.WriteTransform(outTx,  outputDirPath+'/MutualInformation'+'.tfm')

resampler = sitk.ResampleImageFilter()
resampler.SetReferenceImage(fixImg);
resampler.SetInterpolator(sitk.sitkLinear)
resampler.SetDefaultPixelValue(100)
resampler.SetTransform(outTx)

out = resampler.Execute(movImg)
simg1 = sitk.Cast(sitk.RescaleIntensity(fixImg), sitk.sitkUInt8)
simg2 = sitk.Cast(sitk.RescaleIntensity(out), sitk.sitkUInt8)
cimg = sitk.Compose(simg1, simg2, simg1 // 2. + simg2 // 2.)
sitk.Show(cimg, "MutualInformation Registration")

outFileName = 'DIC_Composed_MI.nrrd'
writer = itk.ImageFileWriter[ itk.Image[itk.ctype('signed short'), 3]].New()
writer.SetFileName(outputDirPath + '/' + outFileName)
writer.UseCompressionOn()
writer.SetInput(cimg)

print('Writing: ' + outputDirPath + '/' + outFileName)
writer.Update()

print("-----END-----")
