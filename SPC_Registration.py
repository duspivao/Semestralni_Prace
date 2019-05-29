#!/usr/bin/env python
import os
import itk
import sys
import datetime
import SimpleITK as sitk
import traceback

# Dictionaries of implemented methods, metrics etc
methods = {
    1: 'Mutual Information',
    2: 'B-Spline',
    3: 'DemonsFilter',
    4: 'FastSymmetricForcesDemonsRegistrationFilter',
    5: 'DisplacementFieldTransform',
    6: '---',
    0: 'ALL'
}
metrics = {
    1: 'MeanSquares',
    # 2: 'Demons',
    # 3: 'Correlation',
    # 4: 'ANTSNeighborhoodCorrelation',
    # 5: 'JointHistogramMutualInformation',
    6: 'MattesMutualInformation',
    0: 'ALL'
}
optimizers = {
    1: 'Exhaustive',
    2: 'Powell',
    3: 'Gradient Descent',
    4: 'Gradient Descent Line Search',
    5: 'Regular Step Gradient Descent',
    6: 'L-BFGS-B (Limited memory)',
    0: 'ALL'
}
initialTransform = {
    1: ''
}
global numberOfBins
global outTx


# Output direction in project folder
script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
rel_path = "Results/"
st = datetime.datetime.now().strftime("%d_%m_%y_%H%M")
outputDirPath = rel_path+st
if not os.path.exists(outputDirPath):
    os.makedirs(outputDirPath)
abs_file_path = os.path.join(script_dir, outputDirPath)

# Select moving / fixed  DICOMs folder
def inputFolder(movFix):
    while True:
        try:
            dir = raw_input('Select '+str(movFix)+' folder with DICOM images (whole path):')
        except SyntaxError as se:
            print('Input in wrong format!'+str(se))
        except Exception as e:
            print(e)
        else:
            PixelType = itk.ctype('signed short')
            Dimension = 3

            ImageType = itk.Image[PixelType, Dimension]

            namesGenerator = itk.GDCMSeriesFileNames.New()
            namesGenerator.SetUseSeriesDetails(False)
            namesGenerator.SetGlobalWarningDisplay(False)
            try:
                namesGenerator.SetDirectory(dir)
            except Exception as e:
                print(e)
            else:
                seriesUID = namesGenerator.GetSeriesUIDs()

                if len(seriesUID) < 1:
                    print('ERROR: No DICOMS in folder' + dir)

                elif len(seriesUID) > 1:
                    print('ERROR: In folder are more series')
                else:
                    print('DICOMs red OK from: ' + dir)
                    for uid in seriesUID:
                        seriesIdentifier = uid

                        print('Reading: ' + seriesIdentifier)
                        fileNames = namesGenerator.GetFileNames(seriesIdentifier)

                        reader = itk.ImageSeriesReader[ImageType].New()
                        dicomIO = itk.GDCMImageIO.New()
                        reader.SetImageIO(dicomIO)
                        reader.SetFileNames(fileNames)

                        outFileName = 'DIC_' + movFix + '.nrrd'
                        writer = itk.ImageFileWriter[ImageType].New()
                        writer.SetFileName(abs_file_path + '/' + outFileName)
                        writer.UseCompressionOn()
                        writer.SetInput(reader.GetOutput())

                        print('Writing: ' + abs_file_path + '/' + outFileName)
                        writer.Update()

                        return sitk.ReadImage(abs_file_path + '/' + outFileName, sitk.sitkFloat32)


def inputMethods():

    while True:
        print("Choose registrion method:")

        for key in methods.keys():
            print("[" + str(key) + "] - " + methods.get(key))

        try:
            used_method_no = int(input("Enter a number of method:"))
        except ValueError:
            print("Write number of method!")

        else:
           print ('Method - '+methods.get(used_method_no))
           return(used_method_no)


def inputMetrics():


    while True:
        print("Choose metrics:")

        for key in metrics.keys():
            print("[" + str(key) + "] - " + metrics.get(key))
        try:
            used_metric_no = int(input("Enter a number of metric:"))
        except ValueError:
            print("Write number of metric!")

        else:
            if used_metric_no == 0:
                optimizers.pop(0)
            print ('Metric - ' + metrics.get(used_metric_no))
            return (used_metric_no)

def inputOptimizer():


    while True:
        print("Choose metrics:")

        for key in optimizers.keys():
            print("[" + str(key) + "] - " + optimizers.get(key))

        try:
            used_optimizer_no = int(input("Enter a number of metric:"))
        except ValueError:
            print("Write number of metric!")

        else:
            print ('Metric - ' + optimizers.get(used_optimizer_no))
            return (used_optimizer_no)


def setMetrictsBaseOnMetricNo(metricNo, reg):
    if metricNo == 1:
        reg.SetMetricAsMeanSquares()
        return 0
    elif metricNo == 6:
        global numberOfBins
        numberOfBins = 10
        reg.SetMetricAsMattesMutualInformation(numberOfBins)
        return 0
    return -1

def setOptimizerBaseOnMetricNo(optNo, reg):
    if optNo == 5:
        reg.SetOptimizerAsRegularStepGradientDescent(learningRate = 1.0,
                                                     minStep = 0.001,
                                                     numberOfIterations = 100,
                                                     relaxationFactor = 0.5,
                                                     gradientMagnitudeTolerance = 1e-4,
                                                     maximumStepSizeInPhysicalUnits = 0.0 )
        return 0
    return -1



def observerMI(method) :
    print("{0:3}: Value of metric{1:10.5f}; Optimizer position \t#: ".format(method.GetOptimizerIteration(),
                                           method.GetMetricValue(),
                                           method.GetOptimizerPosition()))

print("====Image registrion tool for DICOM files====")
# inputs
fixImg = inputFolder('fixed')
movImg = inputFolder('moving')
methodNo = inputMethods()
metricNo = inputMetrics()
optimizerNo = inputOptimizer()


txDct = dict()
if methodNo == 1 or methodNo == 0:
    global numberOfBins
    numberOfBins = 10
    samplingPercentage = 0.20

    if metricNo == 0:
        metrics.pop(0)
        for k in metrics.keys():
            metricName = str(metrics.get(k))
            optimizersName = str(optimizers.get(optimizerNo))

            mutualInformation = sitk.ImageRegistrationMethod()
            setMetrictsBaseOnMetricNo(k, mutualInformation)
            # mutualInformation.SetMetricAsMattesMutualInformation(numberOfBins)

            mutualInformation.SetMetricSamplingPercentage(samplingPercentage)
            mutualInformation.SetMetricSamplingStrategy(mutualInformation.RANDOM)
            # mutualInformation.SetOptimizerAsRegularStepGradientDescent(1.0, .001, 200)
            setOptimizerBaseOnMetricNo(optimizerNo, mutualInformation)

            mutualInformation.SetInitialTransform(sitk.TranslationTransform(fixImg.GetDimension()))
            mutualInformation.SetInterpolator(sitk.sitkLinear)

            mutualInformation.AddCommand(sitk.sitkIterationEvent, lambda: observerMI(mutualInformation))


            global outTx
            outTx = mutualInformation.Execute(fixImg, movImg)
            sitk.WriteTransform(outTx, outputDirPath + '/MutualInformation'+'_'+ metricName +'_'+ optimizersName+'.tfm')
            txDct['MI' + metricName] = outTx

    elif optimizerNo == 0:
        optimizers.pop(0)
        for k in optimizers.keys():
            metricName = str(metrics.get(metricNo))
            optimizersName = str(optimizers.get(k))

            mutualInformation = sitk.ImageRegistrationMethod()
            setMetrictsBaseOnMetricNo(k, mutualInformation)
            # mutualInformation.SetMetricAsMattesMutualInformation(numberOfBins)

            mutualInformation.SetMetricSamplingPercentage(samplingPercentage)
            mutualInformation.SetMetricSamplingStrategy(mutualInformation.RANDOM)
            # mutualInformation.SetOptimizerAsRegularStepGradientDescent(1.0, .001, 200)
            setOptimizerBaseOnMetricNo(optimizerNo, mutualInformation)

            mutualInformation.SetInitialTransform(sitk.TranslationTransform(fixImg.GetDimension()))
            mutualInformation.SetInterpolator(sitk.sitkLinear)

            mutualInformation.AddCommand(sitk.sitkIterationEvent, lambda: observerMI(mutualInformation))

            global outTx
            outTx = mutualInformation.Execute(fixImg, movImg)
            sitk.WriteTransform(outTx, outputDirPath + '/MutualInformation'+'_'+ metricName +'_'+ optimizersName+'.tfm')
            txDct['MI' + metricName] = outTx
    else:

        mutualInformation = sitk.ImageRegistrationMethod()

        setMetrictsBaseOnMetricNo(metricNo, mutualInformation)
        # mutualInformation.SetMetricAsMattesMutualInformation(numberOfBins)

        mutualInformation.SetMetricSamplingPercentage(samplingPercentage)
        mutualInformation.SetMetricSamplingStrategy(mutualInformation.RANDOM)
        # mutualInformation.SetOptimizerAsRegularStepGradientDescent(1.0, .001, 200)
        setOptimizerBaseOnMetricNo(optimizerNo,mutualInformation)

        mutualInformation.SetInitialTransform(sitk.TranslationTransform(fixImg.GetDimension()))
        mutualInformation.SetInterpolator(sitk.sitkLinear)

        mutualInformation.AddCommand(sitk.sitkIterationEvent, lambda: observerMI(mutualInformation))

        global outTx
        outTx = mutualInformation.Execute(fixImg, movImg)
        sitk.WriteTransform(outTx, outputDirPath + '/MutualInformation' + '.tfm')



resampler = sitk.ResampleImageFilter()
resampler.SetReferenceImage(fixImg);
resampler.SetInterpolator(sitk.sitkLinear)
resampler.SetDefaultPixelValue(100)
resampler.SetTransform(outTx)

out = resampler.Execute(movImg)
simg1 = sitk.Cast(sitk.RescaleIntensity(fixImg), sitk.sitkUInt8)
simg2 = sitk.Cast(sitk.RescaleIntensity(out), sitk.sitkUInt8)
cimg = sitk.Compose(simg1, simg2, simg1 // 2. + simg2 // 2.)
sitk.Show(cimg, "RESULT")

outFileName = 'DIC_RESULT.nrrd'
writer = itk.ImageFileWriter[ itk.Image[itk.ctype('signed short'), 3]].New()
writer.SetFileName(outputDirPath + '/' + outFileName)
writer.UseCompressionOn()
writer.SetInput(cimg)

print('Writing: ' + outputDirPath + '/' + outFileName)
writer.Update()


print('====END====')