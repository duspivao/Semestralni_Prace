#!/usr/bin/env python
import os
import datetime
import SimpleITK as sitk
import time

"""
Results akka metric value and so on will be saved in dictionary result and at the end will be saved in CSV file
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

def mutualInformationRegistrationWithGradientDescentOptimizer(fixImg, movImg):

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
    registration_method.SetOptimizerAsGradientDescentLineSearch(learningRate=2.0, numberOfIterations=500)
    registration_method.SetOptimizerScalesFromPhysicalShift()
    registration_method.SetInitialTransform(initial_transform, inPlace=False)

    final_transform_v1 = registration_method.Execute(sitk.Cast(fixImg, sitk.sitkFloat32),
                                                     sitk.Cast(movImg, sitk.sitkFloat32))

    print('Optimizer\'s stopping condition, {0}'.format(registration_method.GetOptimizerStopConditionDescription()))
    print('Final metric value: {0}'.format(registration_method.GetMetricValue()))

    print(final_transform_v1)

    return final_transform_v1


movImg = readDICOMSerieToImage(mov,'MRI',abs_file_path,0 ,0)
fixImg = readDICOMSerieToImage(fix,'CT',abs_file_path,0 ,0)




# # Smoothing
# fixImgSmooth = sitk.CurvatureFlow(image1=fixImg,
#                                   timeStep=0.25,
#                                   numberOfIterations=20)
#
# movImgSmooth = sitk.CurvatureFlow(image1=movImg,
#                                   timeStep=0.25,
#                                   numberOfIterations=20)
# # Gaussian filter
# gaussianFilter = sitk.SmoothingRecursiveGaussianImageFilter()
# gaussianFilter.SetSigma()
# fixImgSmooth = gaussianFilter.Execute(fixImgSmooth)
# movImgSmooth = gaussianFilter.Execute(movImgSmooth)

writerP = sitk.ImageFileWriter()

# Gaussian filter 2
start = time.time()
gaussianFilter = sitk.AdditiveGaussianNoiseImageFilter()

fixImgSmoothGauss = gaussianFilter.Execute(fixImg)
movImgSmoothGauss = gaussianFilter.Execute(movImg)
end = time.time()

writerP.SetFileName(outputDirPath + '/' + 'Gauss_smooth_01.nrrd')
writerP.Execute(fixImg)

writerP.SetFileName(outputDirPath + '/' + 'Gauss_smooth_02.nrrd')
writerP.Execute(movImg)
print 'Gaussian filtering done'
print 'Time'+str(end-start)+'sec'

# Median Filter
start = time.time()
medianFilter = sitk.MedianImageFilter()
medianFilter.SetRadius(11)
fixImgSmoothGauss = medianFilter.Execute(fixImg)
movImgSmoothGauss = medianFilter.Execute(movImg)
end = time.time()

writerP.SetFileName(outputDirPath + '/' + 'Median11_smooth_01.nrrd')
writerP.Execute(fixImgSmoothGauss)

writerP.SetFileName(outputDirPath + '/' + 'Median11_smooth_02.nrrd')
writerP.Execute(movImgSmoothGauss)
print 'Median filtering done'
print 'Time'+str(end-start)+'sec'


start = time.time()
medianFilter.SetRadius(5)
fixImgSmoothGauss5 = medianFilter.Execute(fixImg)
movImgSmoothGauss5 = medianFilter.Execute(movImg)
end = time.time()
writerP.SetFileName(outputDirPath + '/' + 'Median5_smooth_01.nrrd')
writerP.Execute(fixImgSmoothGauss5)

writerP.SetFileName(outputDirPath + '/' + 'Median5_smooth_02.nrrd')
writerP.Execute(movImgSmoothGauss5)
print 'Median with 5 neighborhoods filtering done'
print 'Time'+str(end-start)+'sec'


start = time.time()
bilateralFilter = sitk.BilateralImageFilter()
fixImgBilFil = bilateralFilter.Execute(fixImg)
movImgBilFil = bilateralFilter.Execute(movImg)
end = time.time()
writerP.SetFileName(outputDirPath + '/' + 'Bill_smooth_01.nrrd')
writerP.Execute(fixImgSmoothGauss5)

writerP.SetFileName(outputDirPath + '/' + 'Bill_smooth_02.nrrd')
writerP.Execute(movImgSmoothGauss5)
print 'Bilateral filtering done'
print 'Time'+str(end-start)+'sec'


"""-----------------------------------------------------------------------------------------"""


# writer = sitk.ImageFileWriter()
#
# writer.SetFileName(outputDirPath + '/' + '01.nrrd')
# writer.Execute(fixImg)
# writer.SetFileName(outputDirPath + '/' + '02.nrrd')
# writer.Execute(fixImgSmooth)
#
# resample = sitk.ResampleImageFilter()
# resample.SetReferenceImage(fixImg)

tempDict = {}

print 'MI Original registration...'
MITrans = mutualInformationRegistrationWithGradientDescentOptimizer(fixImg=fixImg, movImg=movImg)
tempDict['original'] = MITrans.GetMetricValue()

# MITransSmooth = mutualInformationRegistrationWithGradientDescentOptimizer(fixImg=fixImgSmooth,movImg=movImgSmooth)
# tempDict['smooth'] = MITrans.GetMetricValue()
print 'MI Gaussian filter used registration...'
MITransGauss = mutualInformationRegistrationWithGradientDescentOptimizer(fixImg=fixImgSmoothGauss, movImg=movImgSmoothGauss)
tempDict['Gaussian filter'] = MITrans.GetMetricValue()

print 'MI Median registration...'
MITransMedian = mutualInformationRegistrationWithGradientDescentOptimizer(fixImg=fixImgSmoothGauss, movImg=movImgSmoothGauss)
tempDict['Median filter'] = MITrans.GetMetricValue()

print 'MI Median 5 neighborhood registration...'
MITransMedian5 = mutualInformationRegistrationWithGradientDescentOptimizer(fixImg=fixImgSmoothGauss5, movImg=movImgSmoothGauss5)
tempDict['Median filter 5 pixels'] = MITrans.GetMetricValue()

print 'MI bilateral registration...'
MITransBil = mutualInformationRegistrationWithGradientDescentOptimizer(fixImg=fixImgBilFil, movImg=movImgBilFil)
tempDict['Bilateral filter'] = MITrans.GetMetricValue()

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


print '===END==='