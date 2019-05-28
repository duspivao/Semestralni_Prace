#!/usr/bin/env python

from __future__ import print_function

import SimpleITK as sitk
import os
import datetime
import itk

savedTransform = 'C:/ZCU/Results/27_04_19_1603.tfm'
# LOOOKS good

read_result = sitk.ReadTransform(savedTransform)

argv = ['','C:/ZCU/Results/DIC_L01.nrrd','C:/ZCU/Results/DIC_L02.nrrd','.tfm']

fixed = sitk.ReadImage(argv[1], sitk.sitkFloat32)
moving = sitk.ReadImage(argv[2], sitk.sitkFloat32)


#######################################################################################################################
registration_method = sitk.ImageRegistrationMethod()

transform_to_displacment_field_filter = sitk.TransformToDisplacementFieldFilter()
transform_to_displacment_field_filter.SetReferenceImage(fixed)
initial_transform = sitk.DisplacementFieldTransform(transform_to_displacment_field_filter.Execute(sitk.Transform()))

initial_transform.SetSmoothingGaussianOnUpdate(varianceForUpdateField=0.0, varianceForTotalField=2.0)

registration_method.SetInitialTransform(initial_transform)

registration_method.SetMetricAsDemons(10)  # intensities are equal if the difference is less than 10HU

# Multi-resolution framework.
registration_method.SetShrinkFactorsPerLevel(shrinkFactors=[4, 2, 1])
registration_method.SetSmoothingSigmasPerLevel(smoothingSigmas=[8, 4, 0])

registration_method.SetInterpolator(sitk.sitkLinear)
# If you have time, run this code as is, otherwise switch to the gradient descent optimizer
# registration_method.SetOptimizerAsConjugateGradientLineSearch(learningRate=1.0, numberOfIterations=20, convergenceMinimumValue=1e-6, convergenceWindowSize=10)
registration_method.SetOptimizerAsGradientDescent(learningRate=1.0, numberOfIterations=20, convergenceMinimumValue=1e-6,
                                                  convergenceWindowSize=10)
registration_method.SetOptimizerScalesFromPhysicalShift()

# # If corresponding points in the fixed and moving image are given then we display the similarity metric
# # and the TRE during the registration.
# if fixed_points and moving_points:
#     registration_method.AddCommand(sitk.sitkStartEvent, rc.metric_and_reference_start_plot)
#     registration_method.AddCommand(sitk.sitkEndEvent, rc.metric_and_reference_end_plot)
#     registration_method.AddCommand(sitk.sitkIterationEvent,
#                                    lambda: rc.metric_and_reference_plot_values(registration_method, fixed_points,
#                                                                                moving_points))

outTx = registration_method.Execute(fixed, moving)
# demons = sitk.DemonsRegistrationFilter()
# demons.Execute(fixed,moving)
#
# print("-------")
# print(outTx)
# print("Optimizer stop condition: {0}".format(registration.GetOptimizerStopConditionDescription()))
# print(" Number of iterations: {0}".format(registration.GetOptimizerIteration()))
# print(" Final Metric value: {0}".format(registration.GetMetricValue()))
outputDirPath = 'C:/ZCU/Results/'
st = datetime.datetime.now().strftime("%d_%m_%y_%H%M")
outputDirPath = outputDirPath+st
sitk.WriteTransform(outTx,  outputDirPath+'/Demons'+'.tfm')
resampler = sitk.ResampleImageFilter()
resampler.SetReferenceImage(fixed);
# resampler.SetInterpolator(sitk.sitkLinear)
resampler.SetInterpolator(sitk.sitkBSplineResampler)
resampler.SetDefaultPixelValue(100)
resampler.SetTransform(outTx)

out = resampler.Execute(moving)
simg1 = sitk.Cast(sitk.RescaleIntensity(fixed), sitk.sitkUInt8)
simg2 = sitk.Cast(sitk.RescaleIntensity(out), sitk.sitkUInt8)
cimg = sitk.Compose(simg1, simg2, simg1 // 2. + simg2 // 2.)
sitk.Show(cimg, "BSpline Mehod Registration")

outFileName = 'DIC_Composed_BSpline.nrrd'
writer = itk.ImageFileWriter[ itk.Image[itk.ctype('signed short'), 3]].New()
writer.SetFileName(outputDirPath + '/' + outFileName)
writer.UseCompressionOn()
writer.SetInput(cimg)

print('Writing: ' + outputDirPath + '/' + outFileName)
writer.Update()