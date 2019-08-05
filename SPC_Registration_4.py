#!/usr/bin/env python
import os
import datetime
import SimpleITK as sitk
import time as ti
import csv



"""
Results akka metric value and so on will be saved in dictionary result and at the end will be saved in CSV file

In this File is Scale vs Multiscale
"""
results = {}

"""
This program is for compare method of registration of 3D medical DICOM series.
For same metrics is compute for severel methods, so you can compare result of this 
in result CSV. It also compares some data preprocssing like bluering and so on. 
Final composed result is otherwise made of original DICOMs
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



csvData = ['Method', 'Metric value', 'Number of iteration', 'Time']
csvFile = open(abs_file_path+'results4.csv', 'w')
writerCSV = csv.writer(csvFile)
writerCSV.writerow(csvData)

def observer(method) :
    """
    Method which is observer to registration it prints iteration number and also metric value of each step
    :param method:
    :return: void
    """
    print("{0:3}: Value of metric{1:10.5f};".format(method.GetOptimizerIteration(),
                                           method.GetMetricValue()))

def writeResult(fixImg,movImg,outTx):
    """
    Procedure which saves composed registration image in nrrd format. It also writes every final transformation ito
    file
    :param fixImg: Fixed image
    :param movImg: Moving image
    :param outTx: Final transformation
    :return: void
    """

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

def mutualInformationRegistrationWithGradientDescentOptimizer(fixImg, movImg, numberOfIterations):
    start = ti.time()

    # Setting initial transformation
    initial_transform = sitk.CenteredTransformInitializer(sitk.Cast(fixImg, movImg.GetPixelID()),
                                                          movImg,
                                                          sitk.Euler3DTransform(),
                                                          sitk.CenteredTransformInitializerFilter.GEOMETRY)
    print initial_transform

    # Setting of mutual informartion method parameters
    registration_method = sitk.ImageRegistrationMethod()
    registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetMetricSamplingPercentage(0.01)

    # Interpolator set as linear
    registration_method.SetInterpolator(sitk.sitkLinear)
    registration_method.SetOptimizerAsGradientDescent(learningRate=2.0, numberOfIterations=numberOfIterations)
    registration_method.SetOptimizerScalesFromPhysicalShift()
    registration_method.SetInitialTransform(initial_transform, inPlace=False)

    final_transform_v1 = registration_method.Execute(sitk.Cast(fixImg, sitk.sitkFloat32),
                                                     sitk.Cast(movImg, sitk.sitkFloat32))

    print('Optimizer\'s stopping condition, {0}'.format(registration_method.GetOptimizerStopConditionDescription()))
    print('Final metric value: {0}'.format(registration_method.GetMetricValue()))

    print(final_transform_v1)
    end = ti.time()

    return final_transform_v1, registration_method.GetMetricValue(), end - start

def mutualInformationRegistrationConjugateGradientLineSearchOptimizer(fixImg, movImg, numberOfIterations):
    start = ti.time()

    # Setting initial transformation
    initial_transform = sitk.CenteredTransformInitializer(sitk.Cast(fixImg, movImg.GetPixelID()),
                                                          movImg,
                                                          sitk.Euler3DTransform(),
                                                          sitk.CenteredTransformInitializerFilter.GEOMETRY)
    print initial_transform

    # Setting of mutual informartion method parameters
    registration_method = sitk.ImageRegistrationMethod()
    registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetMetricSamplingPercentage(0.01)

    # Interpolator set as linear
    registration_method.SetInterpolator(sitk.sitkLinear)
    registration_method.SetOptimizerAsConjugateGradientLineSearch(learningRate=2.0,
                                                                  numberOfIterations=numberOfIterations,
                                                                  )
    registration_method.SetOptimizerScalesFromPhysicalShift()
    registration_method.SetInitialTransform(initial_transform, inPlace=False)

    final_transform_v1 = registration_method.Execute(sitk.Cast(fixImg, sitk.sitkFloat32),
                                                     sitk.Cast(movImg, sitk.sitkFloat32))

    print('Optimizer\'s stopping condition, {0}'.format(registration_method.GetOptimizerStopConditionDescription()))
    print('Final metric value: {0}'.format(registration_method.GetMetricValue()))

    print(final_transform_v1)
    end = ti.time()

    return final_transform_v1, registration_method.GetOptimizerStopConditionDescription(), end - start

def mutualInformationRegistrationWithAMOBEAOptimizer(fixImg, movImg, numberOfIterations):
    start = ti.time()

    # Setting initial transformation
    initial_transform = sitk.CenteredTransformInitializer(sitk.Cast(fixImg, movImg.GetPixelID()),
                                                          movImg,
                                                          sitk.Euler3DTransform(),
                                                          sitk.CenteredTransformInitializerFilter.GEOMETRY)
    print initial_transform

    # Setting of mutual informartion method parameters
    registration_method = sitk.ImageRegistrationMethod()
    registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetMetricSamplingPercentage(0.01)

    # Interpolator set as linear
    registration_method.SetInterpolator(sitk.sitkLinear)
    registration_method.SetOptimizerAsAmoeba(simplexDelta=5.0, numberOfIterations=numberOfIterations)
    registration_method.SetOptimizerScalesFromPhysicalShift()
    registration_method.SetInitialTransform(initial_transform, inPlace=False)

    final_transform_v1 = registration_method.Execute(sitk.Cast(fixImg, sitk.sitkFloat32),
                                                     sitk.Cast(movImg, sitk.sitkFloat32))

    print('Optimizer\'s stopping condition, {0}'.format(registration_method.GetOptimizerStopConditionDescription()))
    print('Final metric value: {0}'.format(registration_method.GetMetricValue()))

    print(final_transform_v1)
    end = ti.time()

    return final_transform_v1, registration_method.GetMetricValue(), end - start

def mutualInformationRegistrationWithLBFGSBOptimizer(fixImg, movImg, numberOfIterations):
    start = ti.time()

    # Setting initial transformation
    initial_transform = sitk.CenteredTransformInitializer(sitk.Cast(fixImg, movImg.GetPixelID()),
                                                          movImg,
                                                          sitk.Euler3DTransform(),
                                                          sitk.CenteredTransformInitializerFilter.GEOMETRY)
    print initial_transform

    # Setting of mutual informartion method parameters
    registration_method = sitk.ImageRegistrationMethod()
    registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetMetricSamplingPercentage(0.01)

    # Interpolator set as linear
    registration_method.SetInterpolator(sitk.sitkLinear)
    registration_method.SetOptimizerAsLBFGSB(gradientConvergenceTolerance = 1e-5,
                                             # numberOfIterations=int(numberOfIterations),
                                             maximumNumberOfCorrections = 5,
                                             maximumNumberOfFunctionEvaluations = 2000)
    registration_method.SetOptimizerScalesFromPhysicalShift()
    registration_method.SetInitialTransform(initial_transform, inPlace=False)

    final_transform_v1 = registration_method.Execute(sitk.Cast(fixImg, sitk.sitkFloat32),
                                                     sitk.Cast(movImg, sitk.sitkFloat32))

    print('Optimizer\'s stopping condition, {0}'.format(registration_method.GetOptimizerStopConditionDescription()))
    print('Final metric value: {0}'.format(registration_method.GetMetricValue()))

    print(final_transform_v1)
    end = ti.time()

    return final_transform_v1, registration_method.GetMetricValue(), end - start

def mutualInformationRegistrationWithPowellOptimizer(fixImg, movImg, numberOfIterations):
    start = ti.time()

    # Setting initial transformation
    initial_transform = sitk.CenteredTransformInitializer(sitk.Cast(fixImg, movImg.GetPixelID()),
                                                          movImg,
                                                          sitk.Euler3DTransform(),
                                                          sitk.CenteredTransformInitializerFilter.GEOMETRY)
    print initial_transform

    # Setting of mutual informartion method parameters
    registration_method = sitk.ImageRegistrationMethod()
    registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetMetricSamplingPercentage(0.01)

    # Interpolator set as linear
    registration_method.SetInterpolator(sitk.sitkLinear)
    registration_method.SetOptimizerAsPowell()
    registration_method.SetOptimizerScalesFromPhysicalShift()
    registration_method.SetInitialTransform(initial_transform, inPlace=False)

    final_transform_v1 = registration_method.Execute(sitk.Cast(fixImg, sitk.sitkFloat32),
                                                     sitk.Cast(movImg, sitk.sitkFloat32))

    print('Optimizer\'s stopping condition, {0}'.format(registration_method.GetOptimizerStopConditionDescription()))
    print('Final metric value: {0}'.format(registration_method.GetMetricValue()))

    print(final_transform_v1)
    end = ti.time()

    return final_transform_v1, registration_method.GetMetricValue(), end - start

movImg = readDICOMSerieToImage(mov,'MRI',abs_file_path,0 ,0)
fixImg = readDICOMSerieToImage(fix,'CT',abs_file_path,0 ,0)



tempDict = {}

print 'MI Gradient Descent...100'
MITrans, MiVal, time = mutualInformationRegistrationWithGradientDescentOptimizer(fixImg=fixImg, movImg=movImg,numberOfIterations=100)
tempDict['MI'] = MiVal
print 'Metric '+str(MiVal)+' Time '+str(time)+ ' sec'
writerCSV.writerow(['MI_Gradient_Descent', str(MiVal), '100', str(time)])


print 'MI Gradient Descent...500'
MITrans, MiVal2, time = mutualInformationRegistrationWithGradientDescentOptimizer(fixImg=fixImg, movImg=movImg,numberOfIterations=100)
tempDict['MI'] = MiVal2
print 'Metric '+str(MiVal2)+' Time '+str(time)+ ' sec'
writerCSV.writerow(['MI_Gradient_Descent', str(MiVal2), '500', str(time)])


print 'MI Conjugate GradientLine Search Optimizer 100'
MITransGauss, MiVal3, time = mutualInformationRegistrationWithGradientDescentOptimizer(fixImg=fixImg, movImg=movImg,numberOfIterations=100)
tempDict['original'] = MiVal3
print 'Metric '+str(MiVal3)+' Time '+str(time)+ ' sec'
writerCSV.writerow(['MI_Conjugate_Gradient_Line_Search', str(MiVal3), '100', str(time)])


print 'MI Conjugate GradientLine Search Optimizer 500'
MITransGauss, MiVal4, time = mutualInformationRegistrationWithGradientDescentOptimizer(fixImg=fixImg, movImg=movImg,numberOfIterations=100)
tempDict['original'] = MiVal4
print 'Metric '+str(MiVal4)+' Time '+str(time)+ ' sec'
writerCSV.writerow(['MI_Conjugate_Gradient_Line_Search', str(MiVal4), '500', str(time)])

print 'MI Amobea Optimizer 100'
MITransGauss, MiVal5, time = mutualInformationRegistrationWithAMOBEAOptimizer(fixImg=fixImg, movImg=movImg,numberOfIterations=100)
tempDict['original'] = MiVal5
print 'Metric '+str(MiVal5)+' Time '+str(time)+ ' sec'
writerCSV.writerow(['MI_Amobea', str(MiVal5), '100', str(time)])

print 'MI Amobea Optimizer 500'
MITransGauss, MiVal6, time = mutualInformationRegistrationWithAMOBEAOptimizer(fixImg=fixImg, movImg=movImg,numberOfIterations=500)
tempDict['original'] = MiVal6
print 'Metric '+str(MiVal6)+' Time '+str(time)+ ' sec'
writerCSV.writerow(['MI_Amobea', str(MiVal6), '500', str(time)])

print 'MI LBFGSB Optimizer 100'
MITransGauss, MiVal7, time = mutualInformationRegistrationWithLBFGSBOptimizer(fixImg=fixImg, movImg=movImg,numberOfIterations=100)
tempDict['original'] = MiVal7
print 'Metric '+str(MiVal7)+' Time '+str(time)+ ' sec'
writerCSV.writerow(['MI_LBFGSB', str(MiVal7), '100', str(time)])

print 'MI LBFGSB Optimizer 500'
MITransGauss, MiVal8, time = mutualInformationRegistrationWithLBFGSBOptimizer(fixImg=fixImg, movImg=movImg,numberOfIterations=500)
tempDict['original'] = MiVal8
print 'Metric '+str(MiVal8)+' Time '+str(time)+ ' sec'
writerCSV.writerow(['MI_LBFGSB', str(MiVal8), '500', str(time)])




""""""""""""""
# print 'MI Powell Optimizer 100'
# MITransGauss = mutualInformationRegistrationWithPowellOptimizer(fixImg=fixImg, movImg=movImg,numberOfIterations=100)
# tempDict['original'] = metricVal
# print 'Metric '+str(metricVal)+' Time '+str(time)+ ' sec'
# writerCSV.writerow(['MI_Powell', str(metricVal), '100', str(time)])
#
# print 'MI Powell Optimizer 500'
# MITransGauss = mutualInformationRegistrationWithPowellOptimizer(fixImg=fixImg, movImg=movImg,numberOfIterations=500)
# tempDict['original'] = metricVal
# print 'Metric '+str(metricVal)+' Time '+str(time)+ ' sec'
# writerCSV.writerow(['MI_Powell', str(metricVal), '500', str(time)])

# # SimpleITK supports several interpolation options, we go with the simplest that gives reasonable results.
# resample.SetInterpolator(sitk.sitkLinear)
# resample.SetTransform(final_transform_v1)
# sitk.WriteImage(resample.Execute(movImg), outputDirPath+ '/' +'res' + '.mha')
# sitk.WriteTransform(final_transform_v1, outputDirPath+ 'transform' + '.tfm')
#
# writer.SetFileName(outputDirPath + '/' + '03.nrrd')
# writer.Execute(resample.Execute(movImg))
#
# simg1 = sitk.Cast(sitk.RescaleIntensity(fixImg), sitk.sitkUInt8)
# simg2 = sitk.Cast(sitk.RescaleIntensity(resample.Execute(movImg)), sitk.sitkUInt8)
# cimg = sitk.Compose(simg1, simg2, simg1 // 4. + simg2 // 4.)
# # sitk.Show(cimg, "RESULT")
#
# outFileName = 'DIC_RESULT.nrrd'
#
#
#
#
# writer.SetFileName(outputDirPath + '/' + outFileName)
# writer.Execute(cimg)
csvFile.close()

print '===END==='