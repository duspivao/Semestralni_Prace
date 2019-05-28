#!/usr/bin/env python

from __future__ import print_function

import SimpleITK as sitk
import sys
import os
import datetime


newpath = 'C:/ZCU/Results/BSpline3_'
st = datetime.datetime.now().strftime("%d_%m_%y_%H%M")
newpath = newpath+st
# label = 'MASKS_DICOM/bones'
if not os.path.exists(newpath):
    os.makedirs(newpath)

# sys.argv = ['','C:/ZCU/Results/liver01.nrrd','C:/ZCU/Results/liver02.nrrd',newpath+'.tfm']

# sys.argv = ['','C:/ZCU/Results/part01.nrrd','C:/ZCU/Results/part02.nrrd',newpath+'.tfm']
sys.argv = ['','C:/ZCU/Results/partDIC01.nrrd','C:/ZCU/Results/partDIC02.nrrd',newpath+'.tfm']
def command_iteration(method, bspline_transform) :

    if method.GetOptimizerIteration() == 0:
        # The BSpline is resized before the first optimizer
        # iteration is completed per level. Print the transform object
        # to show the adapted BSpline transform.
        print(bspline_transform)


    print("{0:3} = {1:10.5f}".format(method.GetOptimizerIteration(),
                                     method.GetMetricValue()))



def command_multi_iteration(method) :
    # The sitkMultiResolutionIterationEvent occurs before the
    # resolution of the transform. This event is used here to print
    # the status of the optimizer from the previous registration level.
    if R.GetCurrentLevel() > 0:
        print("Optimizer stop condition: {0}".format(R.GetOptimizerStopConditionDescription()))
        print(" Iteration: {0}".format(R.GetOptimizerIteration()))
        print(" Metric value: {0}".format(R.GetMetricValue()))

    print("--------- Resolution Changing ---------")


if len ( sys.argv ) < 4:
    print( "Usage: {0} <fixedImageFilter> <movingImageFile> <outputTransformFile>".format(sys.argv[0]))
    sys.exit ( 1 )


fixed = sitk.ReadImage(sys.argv[1], sitk.sitkFloat32)

moving = sitk.ReadImage(sys.argv[2], sitk.sitkFloat32)

transformDomainMeshSize=[2]*fixed.GetDimension()
tx = sitk.BSplineTransformInitializer(fixed,
                                      transformDomainMeshSize )

print("Initial Number of Parameters: {0}".format(tx.GetNumberOfParameters()))

R = sitk.ImageRegistrationMethod()
R.SetMetricAsJointHistogramMutualInformation()

R.SetOptimizerAsGradientDescentLineSearch(3.0,
                                          100,
                                          convergenceMinimumValue=1e-3,
                                          convergenceWindowSize=5)

R.SetInterpolator(sitk.sitkLinear)

R.SetInitialTransformAsBSpline(tx,
                               inPlace=True,
                               scaleFactors=[1,2,5])
R.SetShrinkFactorsPerLevel([4,2,1])
R.SetSmoothingSigmasPerLevel([4,2,1])

R.AddCommand( sitk.sitkIterationEvent, lambda: command_iteration(R, tx) )
R.AddCommand( sitk.sitkMultiResolutionIterationEvent, lambda: command_multi_iteration(R) )

outTx = R.Execute(fixed, moving)

print("-------")
print(tx)
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
    sitk.Show( cimg, "Image Registration Composition" )