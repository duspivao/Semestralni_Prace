#!/usr/bin/env python
import os
import itk
import sys
import datetime
import SimpleITK as sitk
import traceback

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
    methods = {
        1 : 'Mutual Information',
        2 : 'B-Spline',
        3 : 'DemonsFilter',
        4 : 'FastSymmetricForcesDemonsRegistrationFilter',
        5 : 'DisplacementFieldTransform',
        6 : '---',
        0 : 'ALL'
    }

    while True:
        print("Choose registrion method:")

        for key in methods.keys():
            print("[" + str(key) + "] - " + methods.get(key))
        # print("[1] - Mutual Information")
        # print("[2] - B-Spline")
        # print("[3] - DemonsFilter")
        # print("[4] - FastSymmetricForcesDemonsRegistrationFilter")
        # print("[5] - FastSymmetricForcesDemonsRegistrationFilter")
        # print("[6] - DisplacementFieldTransform")
        # print("[0] - ALL with comparation")

        try:
            used_method_no = int(input("Enter a number of method:"))
        except ValueError:
            print("Write number of method!")

        else:
           print ('Method - '+methods.get(used_method_no))
           return(used_method_no)


def inputMetrics():
    metrics = {
        1: 'MeanSquares',
        2: 'Demons',
        3: 'Correlation',
        4: 'ANTSNeighborhoodCorrelation',
        5: 'JointHistogramMutualInformation',
        6: 'MattesMutualInformation',
        0: 'ALL'
    }

    while True:
        print("Choose metrics:")

        for key in metrics.keys():
            print("[" + str(key) + "] - " + metrics.get(key))
        # print("[1] - Mutual Information")
        # print("[2] - B-Spline")
        # print("[3] - DemonsFilter")
        # print("[4] - FastSymmetricForcesDemonsRegistrationFilter")
        # print("[5] - FastSymmetricForcesDemonsRegistrationFilter")
        # print("[6] - DisplacementFieldTransform")
        # print("[0] - ALL with comparation")

        try:
            used_method_no = int(input("Enter a number of metric:"))
        except ValueError:
            print("Write number of metric!")

        else:
            print ('Metric - ' + metrics.get(used_method_no))
            return (used_method_no)

def inputOptimizer():
    optimizer = {
        1: 'Exhaustive',
        2: 'Powell',
        3: 'Gradient Descent',
        4: 'Gradient Descent Line Search',
        5: 'Regular Step Gradient Descent',
        6: 'L-BFGS-B (Limited memory)',
        0: 'ALL'
    }

    while True:
        print("Choose metrics:")

        for key in optimizer.keys():
            print("[" + str(key) + "] - " + optimizer.get(key))
        # print("[1] - Mutual Information")
        # print("[2] - B-Spline")
        # print("[3] - DemonsFilter")
        # print("[4] - FastSymmetricForcesDemonsRegistrationFilter")
        # print("[5] - FastSymmetricForcesDemonsRegistrationFilter")
        # print("[6] - DisplacementFieldTransform")
        # print("[0] - ALL with comparation")

        try:
            used_method_no = int(input("Enter a number of metric:"))
        except ValueError:
            print("Write number of metric!")

        else:
            print ('Metric - ' + optimizer.get(used_method_no))
            return (used_method_no)

print("====Image registrion tool for DICOM files====")
# inputs
fixed = inputFolder('fixed')
moving = inputFolder('moving')
methodNo = inputMethods()
metricNo = inputMetrics()
optimizer = inputOptimizer()




print('====END====')