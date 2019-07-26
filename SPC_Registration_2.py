#!/usr/bin/env python
import os
import datetime
import SimpleITK as sitk


"""
This program is for compare method of registration of 3D medical DICOM series.
For same metrics is compute for severel methods, so you can compare result of this 
in result CSV.
"""



"""
Set of testing data. One of the inputs is MRI images and other one is CT images. These inputs have different resolution
and the series has different number of 
"""
mov = 'C:/ZCU/DATA_FOR_TEST/TCGA-LIHC/TCGA-BC-A10X/11-22-1992-MRI ABD WWO CONT-49239/10-LIVER-GAD-ENHANCEMENTT1F-78300'
fix = 'C:/ZCU/DATA_FOR_TEST/TCGA-LIHC/TCGA-BC-A10X/03-29-1993-CT ABDOMEN  WCONTRAST-43286/4-150cc OMNIPAQUE-36663'


""""
Set output directory in same folder as this python file is. Make subfolder with time stamp in name.
"""
script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
rel_path = "Results_Comaparation_Methods/"
st = datetime.datetime.now().strftime("%d_%m_%y_%H%M")

# Just for test removed timestamp folders tempora
# outputDirPath = rel_path+st
outputDirPath = rel_path+'test'
if not os.path.exists(outputDirPath):
    os.makedirs(outputDirPath)
abs_file_path = os.path.join(script_dir, outputDirPath+'/')


def observer(method) :
    # print("{0:3}: Value of metric{1:10.5f}; Optimizer position \t#: ".format(method.GetOptimizerIteration(),
    #                                        method.GetMetricValue(),
    #                                        method.GetOptimizerPosition()))
    print("{0:3}: Value of metric{1:10.5f};".format(method.GetOptimizerIteration(),
                                           method.GetMetricValue()))

def writeResult(fixImg,movImg,outTx):

    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(fixImg);
    resampler.SetInterpolator(sitk.sitkLinear)
    resampler.SetDefaultPixelValue(100)
    resampler.SetTransform(outTx)

    out = resampler.Execute(movImg)
    simg1 = sitk.Cast(sitk.RescaleIntensity(fixImg), sitk.sitkUInt8)
    simg2 = sitk.Cast(sitk.RescaleIntensity(out), sitk.sitkUInt8)
    cimg = sitk.Compose(simg1, simg2, simg1 // 2. + simg2 // 2.)

    # sitk.Show(cimg, "RESULT")

    outFileName = 'DIC_RESULT.nrrd'
    writer = sitk.ImageFileWriter()

    # writer = itk.ImageFileWriter[itk.Image[itk.ctype('signed short'), 3]].New()
    writer.SetFileName(outputDirPath + '/' + outFileName)


    print('Writing: ' + outputDirPath + '/' + outFileName)
    writer.Execute(cimg)
    writer.SetFileName(outputDirPath + '/' + 'test.nrrd')
    writer.Execute(out)
    writer.SetFileName(outputDirPath + '/' + 'test2.nrrd')
    writer.Execute(fixImg)
    writer.SetFileName(outputDirPath + '/' + 'test3.nrrd')
    writer.Execute(movImg)


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

movImg = readDICOMSerieToImage(mov,'MRI',abs_file_path,0 ,0)
fixImg = readDICOMSerieToImage(fix,'CT',abs_file_path,0 ,0)

# Smoothing
fixImgSmooth = sitk.CurvatureFlow(image1=fixImg,
                                  timeStep=0.25,
                                  numberOfIterations=20)
movImgSmooth = sitk.CurvatureFlow(image1=movImg,
                                  timeStep=0.25,
                                  numberOfIterations=20)

resample = sitk.ResampleImageFilter()
resample.SetReferenceImage(fixImg)

initial_transform = sitk.CenteredTransformInitializer(sitk.Cast(fixImg,movImg.GetPixelID()),
                                                      movImg,
                                                      sitk.Euler3DTransform(),
                                                      sitk.CenteredTransformInitializerFilter.GEOMETRY)
print initial_transform

registration_method = sitk.ImageRegistrationMethod()

registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
# registration_method.SetMetricAsDemons(intensityDifferenceThreshold=0.001)
# registration_method.SetMetricAsJointHistogramMutualInformation()
registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
registration_method.SetMetricSamplingPercentage(0.01)

registration_method.SetInterpolator(sitk.sitkLinear)

# registration_method.SetOptimizerAsGradientDescent(learningRate=2.0, numberOfIterations=500)
registration_method.SetOptimizerAsGradientDescentLineSearch(learningRate=2.0, numberOfIterations=500)
# Scale the step size differently for each parameter, this is critical!!!
registration_method.SetOptimizerScalesFromPhysicalShift()

registration_method.SetInitialTransform(initial_transform, inPlace=False)

# registration_method.AddCommand(sitk.sitkStartEvent, registration_callbacks.metric_start_plot)
# registration_method.AddCommand(sitk.sitkEndEvent, registration_callbacks.metric_end_plot)
# registration_method.AddCommand(sitk.sitkIterationEvent,
#                                lambda: registration_callbacks.metric_plot_values(registration_method))

final_transform_v1 = registration_method.Execute(sitk.Cast(fixImg, sitk.sitkFloat32),
                                                 sitk.Cast(movImg, sitk.sitkFloat32))

print('Optimizer\'s stopping condition, {0}'.format(registration_method.GetOptimizerStopConditionDescription()))
print('Final metric value: {0}'.format(registration_method.GetMetricValue()))

print(final_transform_v1)

# SimpleITK supports several interpolation options, we go with the simplest that gives reasonable results.
# resample.SetInterpolator(sitk.sitkLinear)
# resample.SetTransform(transform)
#
writer = sitk.ImageFileWriter()


writer.SetFileName(outputDirPath + '/' + '01.nrrd')
writer.Execute(fixImg)
writer.SetFileName(outputDirPath + '/' + '02.nrrd')
writer.Execute(fixImgSmooth)

resample = sitk.ResampleImageFilter()
resample.SetReferenceImage(fixImg)

# SimpleITK supports several interpolation options, we go with the simplest that gives reasonable results.
resample.SetInterpolator(sitk.sitkLinear)
resample.SetTransform(final_transform_v1)
sitk.WriteImage(resample.Execute(movImg), outputDirPath+ '/' +'res' + '.mha')
sitk.WriteTransform(final_transform_v1, outputDirPath+ 'transform' + '.tfm')

writer.SetFileName(outputDirPath + '/' + '03.nrrd')
writer.Execute(resample.Execute(movImg))

simg1 = sitk.Cast(sitk.RescaleIntensity(fixImg), sitk.sitkUInt8)
simg2 = sitk.Cast(sitk.RescaleIntensity(resample.Execute(movImg)), sitk.sitkUInt8)
cimg = sitk.Compose(simg1, simg2, simg1 // 4. + simg2 // 4.)
# sitk.Show(cimg, "RESULT")

outFileName = 'DIC_RESULT.nrrd'

writer.SetFileName(outputDirPath + '/' + outFileName)
writer.Execute(cimg)
# print movImg.GetDimension()
# print fixImg.GetDimension()
# print movImg.GetPixelIDTypeAsString()
# print fixImg.GetPixelIDTypeAsString()
#
#
# registration_method = sitk.ImageRegistrationMethod()
# registration_method.SetOptimizerAsGradientDescentLineSearch(learningRate=1.0,
#                                                             numberOfIterations=100)
# registration_method.SetMetricAsMeanSquares()
# registration_method.SetInitialTransform(sitk.TranslationTransform(fixImg.GetDimension()))
# registration_method.AddCommand(sitk.sitkIterationEvent, lambda: observer(registration_method))
# final_transform = registration_method.Execute(fixImg, movImg)
#
# # initial_transform = sitk.CenteredTransformInitializer(movImg,
# #                                                       fixImg,
# #                                                       sitk.Euler3DTransform(),
# #                                                       sitk.CenteredTransformInitializerFilter.GEOMETRY)
# #
# # numberOfBins = 10
# # # registration_method.SetMetricAsMattesMutualInformation(numberOfBins)
# # registration_method.SetMetricAsMeanSquares()
# #
# #
# # # registration_method = sitk.ImageRegistrationMethod()
# # # Similarity metric settings.
# # # registration_method.SetMetricAsJointHistogramMutualInformation (numberOfHistogramBins=50,
# # #                                                                 varianceForJointPDFSmoothing=1.5)
# #
# # # registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
# # # registration_method.SetMetricAsMeanSquares()
# # registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
# # registration_method.SetMetricSamplingPercentage(0.1)
# # registration_method.SetInterpolator(sitk.sitkLinear)
# # # Optimizer settings.
# # registration_method.SetOptimizerAsGradientDescent(learningRate = 1.0,
# #                                                      numberOfIterations = 10,
# #                                                      maximumStepSizeInPhysicalUnits = 0.0 )
# #
# # # registration_method.SetOptimizerScalesFromPhysicalShift()
# #
# # # Setup for the multi-resolution framework.
# # #registration_method.SetShrinkFactorsPerLevel(shrinkFactors = [4,2,1])
# # #registration_method.SetSmoothingSigmasPerLevel(smoothingSigmas=[2,1,0])
# # #registration_method.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()
# #
# # registration_method.SetInitialTransform(sitk.TranslationTransform(fixImg.GetDimension()))
# #
# # # Don't optimize in-place, we would possibly like to run this cell multiple times
# # # registration_method.SetInitialTransform(initial_transform, inPlace=False)
# # # Connect all of the observers so that we can perform plotting during registration.
# #
# # # registration_method.AddCommand(sitk.sitkStartEvent, rgui.start_plot)
# # # registration_method.AddCommand(sitk.sitkEndEvent, rgui.end_plot)
# # # registration_method.AddCommand(sitk.sitkMultiResolutionIterationEvent, rgui.update_multires_iterations)
# # # registration_method.AddCommand(sitk.sitkIterationEvent, lambda: rgui.plot_values(registration_method))
# # final_transform = registration_method.Execute(fixImg, movImg)
# #
# #
# # Always check the reason optimization terminated.
# print('Final metric value: {0}'.format(registration_method.GetMetricValue()))
# print('Optimizer\'s stopping condition, {0}'.format(registration_method.GetOptimizerStopConditionDescription()))
#
# # writeResult(fixImg=fixImg,movImg=movImg,outTx=final_transform)
#
# # moving_resampled = sitk.Resample(movImg, fixImg, final_transform, sitk.sitkLinear, 0.0, movImg.GetPixelID())
# # sitk.WriteImage(moving_resampled, os.path.join(abs_file_path, 'RIRE_training_001_mr_T1_resampled.mha'))
# # sitk.WriteTransform(final_transform, os.path.join(abs_file_path, 'RIRE_training_001_CT_2_mr_T1.tfm'))
#
# resampler = sitk.ResampleImageFilter()
# resampler.SetReferenceImage(fixImg)
# resampler.SetInterpolator(sitk.sitkLinear)
# resampler.SetDefaultPixelValue(100)
# resampler.SetTransform(final_transform)
#
# out = resampler.Execute(movImg)
# simg1 = sitk.Cast(sitk.RescaleIntensity(fixImg), sitk.sitkUInt8)
# simg2 = sitk.Cast(sitk.RescaleIntensity(out), sitk.sitkUInt8)
# cimg = sitk.Compose(simg1, simg2, simg1 // 2. + simg2 // 2.)
# # sitk.Show(cimg, "RESULT")
#
# outFileName = 'DIC_RESULT.nrrd'
#
# writer = sitk.ImageFileWriter()
#
# # writer = itk.ImageFileWriter[itk.Image[itk.ctype('signed short'), 3]].New()
# writer.SetFileName(outputDirPath + '/' + outFileName)
#
# print('Writing: ' + outputDirPath + '/' + outFileName)
# writer.Execute(cimg)
print '===END==='