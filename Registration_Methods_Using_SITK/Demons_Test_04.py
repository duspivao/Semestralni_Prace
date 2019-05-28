#!/usr/bin/env python

from __future__ import print_function

import SimpleITK as sitk
import os
import datetime
import itk
import sys

numberOfBins = 20
samplingPercentage = 0.20


def observer(method) :
    print("{0:3}: Value of metric{1:10.5f}; Optimizer position \t#: ".format(method.GetOptimizerIteration(),
                                           method.GetMetricValue(),
                                           method.GetOptimizerPosition()))
def mutualInformationInatialization(fixImg,movImg,outputDirPath):
    initReg = sitk.ImageRegistrationMethod()
    initReg.SetMetricAsMattesMutualInformation(numberOfBins)
    initReg.SetMetricSamplingPercentage(samplingPercentage, sitk.sitkWallClock)
    initReg.SetMetricSamplingStrategy(initReg.RANDOM)
    initReg.SetOptimizerAsRegularStepGradientDescent(1.0, .001, 150)
    initReg.SetInitialTransform(sitk.TranslationTransform(fixImg.GetDimension()))
    initReg.SetInterpolator(sitk.sitkLinear)

    initReg.AddCommand(sitk.sitkIterationEvent, lambda: observer(initReg))
    initTrans = initReg.Execute(fixImg, movImg)
    sitk.WriteTransform(initTrans, outputDirPath + '/MIInitial.tfm')
    print('Initial transform writen into:'+ outputDirPath + '/MIInitial.tfm')
    return initTrans
def GradDescInitialiyation(fixImg,movImg,outputDirPath):
    initReg = sitk.ImageRegistrationMethod()
    initReg.SetMetricAsMeanSquares()
    initReg.SetOptimizerAsRegularStepGradientDescent(learningRate=1.0,
                                                  minStep=0.01,
                                                  numberOfIterations=100,
                                                  relaxationFactor=0.5)
    initReg.SetInitialTransform(sitk.TranslationTransform(fixImg.GetDimension()) )
    initReg.SetInterpolator(sitk.sitkLinear)

    initTrans = initReg.Execute(fixImg, movImg)
    sitk.WriteTransform(initTrans, outputDirPath + '/MIInitial.tfm')
    print('Initial transform writen into:' + outputDirPath + '/MIInitial.tfm')
    return initTrans



def command_iteration(filter) :
    print("{0:3} = {1:10.5f}".format(filter.GetElapsedIterations(),
                                    filter.GetMetric()))

########SETUP PARAMETER AND INPUTS FOR REGISTRATION#####
# Input direction for fixed image
from SimpleITK import ImageRegistrationMethod

label = 'DEMONS_TEST_2'
inputFixDirName = 'C:/ZCU/3Dircadb1/3Dircadb1.1/'+label

# Input dircection for moving image
# label = 'DEMONS_TEST'
inputMovDirName = 'C:/ZCU/3Dircadb1/3Dircadb1.7/'+label


# Output direction
# Subfolder with timestamp will be created
outputDirPath = 'C:/ZCU/Results/'
st = datetime.datetime.now().strftime("%d_%m_%y_%H%M")
outputDirPath = outputDirPath+st
if not os.path.exists(outputDirPath):
    os.makedirs(outputDirPath)

# Parameters of registration


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


fixImg = readDICOMImage(inputFixDirName,outputDirPath,'FIX')
movImg = readDICOMImage(inputMovDirName,outputDirPath,'MOC')
fixed = fixImg
moving = movImg






matcher = sitk.HistogramMatchingImageFilter()
if ( fixed.GetPixelID() in ( sitk.sitkUInt8, sitk.sitkInt8 ) ):
    matcher.SetNumberOfHistogramLevels(128)
else:
    matcher.SetNumberOfHistogramLevels(1024)
matcher.SetNumberOfMatchPoints(125)
matcher.ThresholdAtMeanIntensityOn()
moving = matcher.Execute(moving,fixed)

# The fast symmetric forces Demons Registration Filter
# Note there is a whole family of Demons Registration algorithms included in SimpleITK
# demons = sitk.FastSymmetricForcesDemonsRegistrationFilter()
demons = sitk.DemonsRegistrationFilter()
# demons = sitk.DiffeomorphicDemonsRegistrationFilter()
demons.SetNumberOfIterations(200)
# Standard deviation for Gaussian smoothing of displacement field
demons.SetStandardDeviations(2.0)

demons.AddCommand( sitk.sitkIterationEvent, lambda: command_iteration(demons) )

# Alternativ for use
savedTransform = 'C:/ZCU/Results/20_05_19_0059/MIInitial.tfm'
initialTransform = sitk.ReadTransform(savedTransform)

# initialTransform = mutualInformationInatialization(fixed,moving,outputDirPath)
# initialTransform = GradDescInitialiyation(fixed,moving,outputDirPath)
toDisplacementFilter = sitk.TransformToDisplacementFieldFilter()
toDisplacementFilter.SetReferenceImage(fixed)

displacementField = toDisplacementFilter.Execute(initialTransform)
print('Initial transform used')
print("-------")
displacementField = demons.Execute(fixed, moving, displacementField)
# displacementField = demons.Execute(fixed, moving)


print("-------")
print("Number Of Iterations: {0}".format(demons.GetElapsedIterations()))
print(" RMS: {0}".format(demons.GetRMSChange()))

outTx = sitk.DisplacementFieldTransform(displacementField)

sitk.WriteTransform(outTx, outputDirPath+'/DemonsWithMIInitial.tfm')
print('===TRANS WRITTEN==')
if (not "SITK_NOSHOW" in os.environ):

    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(fixed);
    resampler.SetInterpolator(sitk.sitkLinear)
    resampler.SetDefaultPixelValue(100)
    resampler.SetTransform(outTx)

    out = resampler.Execute(moving)
    simg1 = sitk.Cast(sitk.RescaleIntensity(fixed), sitk.sitkUInt8)
    simg2 = sitk.Cast(sitk.RescaleIntensity(out), sitk.sitkUInt8)
    cimg = sitk.Compose(simg1, simg2, simg1//2.+simg2//2.)
    writer = sitk.ImageFileWriter()
    writer.SetFileName(outputDirPath+'RESULT.nrrd')
    writer.Execute(cimg)
    sitk.Show( cimg, "DeformableRegistration1 Composition" )
print('===END==')