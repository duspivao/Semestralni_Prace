#!/usr/bin/env python

from __future__ import print_function

import SimpleITK as sitk
import sys
import os
import datetime

newpath = 'C:/ZCU/Results/'
st = datetime.datetime.now().strftime("%d_%m_%y_%H%M")
newpath = newpath+st
label = 'MASKS_DICOM/bones'
if not os.path.exists(newpath):
    os.makedirs(newpath)


label = 'PATIENT_DICOM'
inputFile = 'C:/ZCU/3Dircadb1/3Dircadb1.7/'+label
inputFile2 = 'C:/ZCU/3Dircadb1/3Dircadb1.1/'+label
# sys.argv = ['','C:/ZCU/Results/23_04_19_2148/fixed.png','C:/ZCU/Results/23_04_19_2148/moving.png',newpath+'.tfm']
sys.argv = ['',inputFile,inputFile2,newpath+'.tfm']

def command_iteration(method) :
    print("{0:3} = {1:10.5f} : {2}".format(method.GetOptimizerIteration(),
                                   method.GetMetricValue(),
                                   method.GetOptimizerPosition()))

if len ( sys.argv ) < 4:
    print( "Usage: {0} <fixedImageFilter> <movingImageFile> <outputTransformFile>".format(sys.argv[0]))
    sys.exit ( 1 )


reader = sitk.ImageSeriesReader()

dicom_names = reader.GetGDCMSeriesFileNames( sys.argv[1])
reader.SetFileNames(dicom_names)

fixed = reader.Execute()
dicom_names2 = reader.GetGDCMSeriesFileNames( sys.argv[1])
reader.SetFileNames(dicom_names2)

moving = reader.Execute()

# fixed = sitk.ReadImage(sys.argv[1], sitk.sitkFloat32)

# moving = sitk.ReadImage(sys.argv[2], sitk.sitkFloat32)

R = sitk.ImageRegistrationMethod()
R.SetMetricAsMeanSquares()
R.SetOptimizerAsRegularStepGradientDescent(4.0, .01, 200 )
R.SetInitialTransform(sitk.TranslationTransform(fixed.GetDimension()))
R.SetInterpolator(sitk.sitkLinear)

R.AddCommand( sitk.sitkIterationEvent, lambda: command_iteration(R) )

outTx = R.Execute(fixed, moving)

print("-------")
print(outTx)
print("Optimizer stop condition: {0}".format(R.GetOptimizerStopConditionDescription()))
print(" Iteration: {0}".format(R.GetOptimizerIteration()))
print(" Metric value: {0}".format(R.GetMetricValue()))

sitk.WriteTransform(outTx,  sys.argv[3])

if ( not "SITK_NOSHOW" in os.environ ):

    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(fixed);
    resampler.SetInterpolator(sitk.sitkLinear)
    resampler.SetDefaultPixelValue(100)
    resampler.SetTransform(outTx)

    out = resampler.Execute(moving)
    simg1 = sitk.Cast(sitk.RescaleIntensity(fixed), sitk.sitkUInt8)
    simg2 = sitk.Cast(sitk.RescaleIntensity(out), sitk.sitkUInt8)
    cimg = sitk.Compose(simg1, simg2, simg1//2.+simg2//2.)
    sitk.Show( cimg, "ImageRegistration1 Composition" )