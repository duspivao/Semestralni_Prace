#!/usr/bin/env python

from __future__ import print_function

import SimpleITK as sitk
import sys
import os
import datetime


newpath = 'C:/ZCU/Results/MI'
st = datetime.datetime.now().strftime("%d_%m_%y_%H%M")
newpath = newpath+st
# label = 'MASKS_DICOM/bones'
if not os.path.exists(newpath):
    os.makedirs(newpath)

sys.argv = ['','C:/ZCU/Results/liver02.nrrd','C:/ZCU/Results/liver01.nrrd',newpath+'.tfm']


if len ( sys.argv ) < 4:
    print( "Usage: {0} <fixedImageFilter> <movingImageFile> <outputTransformFile> <numberOfBins> <samplingPercentage>".format(sys.argv[0]))
    sys.exit ( 1 )

def command_iteration(method) :
    print("{0:3} = {1:10.5f} : {2}".format(method.GetOptimizerIteration(),
                                           method.GetMetricValue(),
                                           method.GetOptimizerPosition()))


fixed = sitk.ReadImage(sys.argv[1], sitk.sitkFloat32)
moving = sitk.ReadImage(sys.argv[2], sitk.sitkFloat32)


numberOfBins = 10
samplingPercentage = 0.20

if len ( sys.argv ) > 4:
    numberOfBins = int(sys.argv[4])
if len ( sys.argv ) > 5:
    samplingPercentage = float(sys.argv[5])



registration = sitk.ImageRegistrationMethod()
registration.SetMetricAsMattesMutualInformation(numberOfBins)
registration.SetMetricSamplingPercentage(samplingPercentage,sitk.sitkWallClock)
registration.SetMetricSamplingStrategy(registration.registrationANDOM)
registration.SetOptimizerAsregistrationegularStepGradientDescent(1.0,.001,200)
registration.SetInitialTransform(sitk.TranslationTransform(fixed.GetDimension()))
registration.SetInterpolator(sitk.sitkLinear)

registration.AddCommand( sitk.sitkIterationEvent, lambda: command_iteration(R) )

outTx = registration.Execute(fixed, moving)


print("-------")

print("Optimizer stop condition: {0}".format(registration.GetOptimizerStopConditionDescription()))
print(" Iteration: {0}".format(registration.GetOptimizerIteration()))
print(" Metric value: {0}".format(registration.GetMetricValue()))
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
    sitk.Show( cimg, "ImageRegistration4 Composition" )

print("---------")