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
csvFile = open(abs_file_path+'results6.csv', 'w')
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
    registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=100)
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetMetricSamplingPercentage(0.01)

    # Interpolator set as linear
    registration_method.SetInterpolator(sitk.sitkLinear)
    registration_method.SetOptimizerAsGradientDescent(learningRate=1.0, numberOfIterations=numberOfIterations)
    registration_method.SetOptimizerScalesFromPhysicalShift()
    registration_method.SetInitialTransform(initial_transform, inPlace=False)

    final_transform_v1 = registration_method.Execute(sitk.Cast(fixImg, sitk.sitkFloat32),
                                                     sitk.Cast(movImg, sitk.sitkFloat32))

    print('Optimizer\'s stopping condition, {0}'.format(registration_method.GetOptimizerStopConditionDescription()))
    print('Final metric value: {0}'.format(registration_method.GetMetricValue()))

    print(final_transform_v1)
    end = ti.time()

    return final_transform_v1, registration_method.GetMetricValue(), end - start

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

def MiSingleScale(fixImg, movImg, numberOfIterations):
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

def BSplineMultiScale(fixImg, movImg, numberOfIterations):
    start = ti.time()

    transformDomainMeshSize = [2] * fixImg.GetDimension()

    R = sitk.ImageRegistrationMethod()
    R.SetMetricAsCorrelation()
    R.SetOptimizerAsLBFGSB(gradientConvergenceTolerance=1e-5,
                           # numberOfIterations=100,
                           maximumNumberOfCorrections=5,
                           maximumNumberOfFunctionEvaluations=1000,
                           costFunctionConvergenceFactor=1e+4)
    # R.SetOptimizerAsGradientDescentLineSearch(5.0,
    #                                           100,
    #                                           convergenceMinimumValue=1e-4,
    #                                           convergenceWindowSize=5)
    R.SetInterpolator(sitk.sitkLinear)
    R.SetInitialTransformAsBSpline(sitk.BSplineTransformInitializer(movImg,
                                          transformDomainMeshSize),
                                   inPlace=True,
                                   scaleFactors=[1, 2, 5])
    R.SetShrinkFactorsPerLevel([4, 2, 1])
    R.SetSmoothingSigmasPerLevel([4, 2, 1])


    final_transform_v1 =  R.Execute(fixImg, movImg)

    print('Optimizer\'s stopping condition, {0}'.format(R.GetOptimizerStopConditionDescription()))
    print('Final metric value: {0}'.format(R.GetMetricValue()))
    print(final_transform_v1)
    end = ti.time()
    return final_transform_v1, R.GetOptimizerStopConditionDescription(), end - start

def BSplineSingleScale(fixImg, movImg, numberOfIterations):
    start = ti.time()

    transformDomainMeshSize = [2] * movImg.GetDimension()
    tx = sitk.BSplineTransformInitializer(fixImg,
                                          transformDomainMeshSize)

    print("Initial Parameters:");
    print(tx.GetParameters())

    R = sitk.ImageRegistrationMethod()
    R.SetMetricAsCorrelation()

    R.SetOptimizerAsLBFGSB(gradientConvergenceTolerance=1e-5,
                           numberOfIterations=100,
                           maximumNumberOfCorrections=5,
                           maximumNumberOfFunctionEvaluations=1000,
                           costFunctionConvergenceFactor=1e+4)

    R.SetInitialTransform(tx, True)
    R.SetInterpolator(sitk.sitkLinear)

    outTx = R.Execute(fixImg, movImg)
    end = ti.time()
    return outTx, R.GetMetricValue(), end - start

def AffineTrans(fixImg, movImg, numberOfIterations):
    start = ti.time()
    initialTx = sitk.CenteredTransformInitializer(fixImg, movImg, sitk.AffineTransform(fixImg.GetDimension()))

    R = sitk.ImageRegistrationMethod()
    R.SetShrinkFactorsPerLevel([4, 2, 1])
    R.SetSmoothingSigmasPerLevel([2, 1, 1])
    R.SetMetricAsJointHistogramMutualInformation(70)
    R.MetricUseFixedImageGradientFilterOff()

    R.SetOptimizerAsLBFGSB(gradientConvergenceTolerance=1e-5,
                           # numberOfIterations=100,
                           maximumNumberOfCorrections=5,
                           maximumNumberOfFunctionEvaluations=100,
                           costFunctionConvergenceFactor=1e+4)
    # R.SetOptimizerAsGradientDescent(learningRate=1.0,
    #                                 numberOfIterations=numberOfIterations,
    #                                 estimateLearningRate=R.EachIteration)
    R.SetOptimizerScalesFromPhysicalShift()

    R.SetInitialTransform(initialTx, inPlace=True)

    R.SetInterpolator(sitk.sitkLinear)

    # R.AddCommand(sitk.sitkIterationEvent, lambda: command_iteration(R))
    # R.AddCommand(sitk.sitkMultiResolutionIterationEvent, lambda: command_multiresolution_iteration(R))

    outTx = R.Execute(fixImg, movImg)
    end = ti.time()
    return outTx, R.GetMetricValue(), end - start

movImg = readDICOMSerieToImage(mov,'MRI',abs_file_path,0 ,0)
fixImg = readDICOMSerieToImage(fix,'CT',abs_file_path,0 ,0)

initTrans, ini50, iniTime = mutualInformationRegistrationWithGradientDescentOptimizer(fixImg=fixImg, movImg=movImg, numberOfIterations=500)
initResampler = sitk.ResampleImageFilter()
initResampler.SetReferenceImage(fixImg);
initResampler.SetInterpolator(sitk.sitkLinear)
initResampler.SetDefaultPixelValue(100)
initResampler.SetTransform(initTrans)

movImgTransformed = initResampler.Execute(movImg)



tempDict = {}
print 'Affine Single scale'
AffineTrans, si100, time = AffineTrans(fixImg=fixImg, movImg=movImgTransformed,numberOfIterations=100)
tempDict['Affine'] = si100
print 'Metric '+str(si100)+' Time '+str(time)+ ' sec'

# print 'BSpline Single scale'
# BSplineTrans, si100, time = BSplineSingleScale(fixImg=fixImg, movImg=movImgTransformed,numberOfIterations=100)
# tempDict['BSpline'] = si100
# print 'Metric '+str(si100)+' Time '+str(time)+ ' sec'
# writerCSV.writerow(['MI_BSpline_Single', str(si100), '100', str(time)])
# print 'BSpline Multi-scale'
# BSplineTrans, mu100, time = BSplineMultiScale(fixImg=fixImg, movImg=movImgTransformed,numberOfIterations=100)
# tempDict['BSplineMulti'] = mu100
# print 'Metric '+str(mu100)+' Time '+str(time)+ ' sec'
# writerCSV.writerow(['MI_BSpline_Single', str(mu100), '100', str(time)])


resampler = sitk.ResampleImageFilter()
resampler.SetReferenceImage(fixImg)
resampler.SetInterpolator(sitk.sitkLinear)
resampler.SetDefaultPixelValue(100)
resampler.SetTransform(AffineTrans)

out = resampler.Execute(movImg)
simg1 = sitk.Cast(sitk.RescaleIntensity(fixImg), sitk.sitkUInt8)
simg2 = sitk.Cast(sitk.RescaleIntensity(out), sitk.sitkUInt8)
cimg = sitk.Compose(simg1, simg2, simg1//2.+simg2//2.)
# sitk.Show( cimg, "ImageRegistration1 Composition" )
outFileName = 'Affine.nrrd'
writer2 = sitk.ImageFileWriter()
writer2.SetFileName(outputDirPath + '/' + outFileName)

writer2.Execute(cimg)

outFileName = 'AfterInitialization.nrrd'

writer2.SetFileName(outputDirPath + '/' + outFileName)

writer2.Execute(movImgTransformed)


csvFile.close()

print '===END==='