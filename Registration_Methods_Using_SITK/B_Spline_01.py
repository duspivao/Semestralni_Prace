#!/usr/bin/env python
import os
import itk
import sys
import datetime
import SimpleITK as sitk


########SETUP PARAMETER AND INPUTS FOR REGISTRATION#####
# Input direction for fixed image
from SimpleITK import ImageRegistrationMethod

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
    print("{0:3}: Value of metric{1:10.5f}; Optimizer position{2}".format(method.GetOptimizerIteration(),
                                           method.GetMetricValue(),
                                           method.GetOptimizerPosition()))
def observer2(method) :
    print "Resolution was changed"

fixImg = readDICOMImage(inputFixDirName,outputDirPath,'FIX')
movImg = readDICOMImage(inputMovDirName,outputDirPath,'MOC')

transformDomainMeshSize=[10]*movImg.GetDimension()
tx = sitk.BSplineTransformInitializer(fixImg,
                                      transformDomainMeshSize )

print("Initial Parameters:");
print(tx.GetParameters())

registration = sitk.ImageRegistrationMethod()
registration.SetMetricAsMattesMutualInformation(50)
registration.SetOptimizerAsGradientDescentLineSearch(learningRate=2.0,
                                                     numberOfIterations=20,
                                                     convergenceMinimumValue=1e-3,
                                                     convergenceWindowSize=5,
                                                     lineSearchLowerLimit = 0,
                                                     lineSearchUpperLimit=5.0,
                                                     lineSearchEpsilon=0.01,
                                                     lineSearchMaximumIterations = 20,
                                                     maximumStepSizeInPhysicalUnits=0.0)
registration.SetOptimizerScalesFromPhysicalShift( centralRegionRadius = 100,
                                                  smallParameterVariation=0.01
                                                  )
registration.SetInitialTransform(tx)
registration.SetInterpolator(sitk.sitkLinear)

registration.SetShrinkFactorsPerLevel([3,2,1])
registration.SetSmoothingSigmasPerLevel([3,2,1])

registration.AddCommand( sitk.sitkIterationEvent, lambda: observer(registration) )
registration.AddCommand( sitk.sitkMultiResolutionIterationEvent, lambda: observer2(registration) )

outTx = registration.Execute(fixImg, movImg)

print("-------")
print(outTx)
print("Optimizer stop condition: {0}".format(registration.GetOptimizerStopConditionDescription()))
print(" Number of iterations: {0}".format(registration.GetOptimizerIteration()))
print(" Final Metric value: {0}".format(registration.GetMetricValue()))

sitk.WriteTransform(outTx,  outputDirPath+'/BSpline'+'.tfm')
resampler = sitk.ResampleImageFilter()
resampler.SetReferenceImage(fixImg);
# resampler.SetInterpolator(sitk.sitkLinear)
resampler.SetInterpolator(sitk.sitkBSplineResampler)
resampler.SetDefaultPixelValue(100)
resampler.SetTransform(outTx)

out = resampler.Execute(movImg)
simg1 = sitk.Cast(sitk.RescaleIntensity(fixImg), sitk.sitkUInt8)
simg2 = sitk.Cast(sitk.RescaleIntensity(out), sitk.sitkUInt8)
cimg = sitk.Compose(simg1, simg2, simg1 // 2. + simg2 // 2.)
sitk.Show(cimg, "BSpline Mehod Registration")

outFileName = 'DIC_Composed_BSpline.nrrd'
writer = itk.ImageFileWriter[ itk.Image[itk.ctype('signed short'), 3]].New()
writer.SetFileName(outputDirPath + '/' + outFileName)
writer.UseCompressionOn()
writer.SetInput(cimg)

print('Writing: ' + outputDirPath + '/' + outFileName)
writer.Update()