#!/usr/bin/env python

from __future__ import print_function

import datetime

import SimpleITK as sitk
import sys
import os
import itk


label = 'PATIENT_DICOM'
#
# InputImageType  = itk.Image.SS2
#
# FixedImageType = InputImageType
# MovingImageType = InputImageType
# OutPutImageType = itk.Image.UC2
# TransformType = itk.TranslationTransform[itk.D, 2]
#
# fixedImageReader = itk.ImageFileReader[FixedImageType].New()
# movingImageReader = itk.ImageFileReader[MovingImageType].New()
#
# fixedImageReader.SetFileName('C:/ZCU/3Dircadb1/3Dircadb1.1/'+label+'/image_13')
# movingImageReader.SetFileName('C:/ZCU/3Dircadb1/3Dircadb1.3/'+label+'/image_38')
#
# fixedImageReader.Update()
# movingImageReader.Update()
#
# fixedImage = fixedImageReader.GetOutput()
# movingImage = movingImageReader.GetOutput()
#


def command_iteration(method) :
    print("{0:3} = {1:10.5f}".format(method.GetOptimizerIteration(),
                                     method.GetMetricValue()))

fixed = sitk.ReadImage('C:/ZCU/3Dircadb1/3Dircadb1.1/'+label+'/image_13', sitk.sitkFloat32)

moving = sitk.ReadImage('C:/ZCU/3Dircadb1/3Dircadb1.3/'+label+'/image_38', sitk.sitkFloat32)

transformDomainMeshSize=[8]*moving.GetDimension()
tx = sitk.BSplineTransformInitializer(fixed,
                                      transformDomainMeshSize )

print("Initial Parameters:");
print(tx.GetParameters())

R = sitk.ImageRegistrationMethod()
R.SetMetricAsCorrelation()

R.SetOptimizerAsLBFGSB(gradientConvergenceTolerance=1e-5,
                       numberOfIterations=10,
                       maximumNumberOfCorrections=5,
                       maximumNumberOfFunctionEvaluations=1000,
                       costFunctionConvergenceFactor=1e+9)
R.SetInitialTransform(tx, True)
R.SetInterpolator(sitk.sitkLinear)

R.AddCommand( sitk.sitkIterationEvent, lambda: command_iteration(R) )

outTx = R.Execute(fixed, moving)

print("-------")
print(outTx)
print("Optimizer stop condition: {0}".format(R.GetOptimizerStopConditionDescription()))
print(" Iteration: {0}".format(R.GetOptimizerIteration()))
print(" Metric value: {0}".format(R.GetMetricValue()))

newpath = 'C:/ZCU/Results/'
st = datetime.datetime.now().strftime("%d_%m_%y_%H%M")
newpath = newpath+st

sitk.WriteTransform(outTx,  newpath)

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