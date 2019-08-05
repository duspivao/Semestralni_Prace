#!/usr/bin/env python

from __future__ import print_function

import SimpleITK as sitk
import os
import datetime


savedTransform = 'C:/ZCU/Results/27_04_19_1603.tfm'
# LOOOKS good

read_result = sitk.ReadTransform(savedTransform)

argv = ['','C:/ZCU/Results/1_1.nrrd','C:/ZCU/Results/1_7.nrrd','.tfm']

fixed = sitk.ReadImage(argv[1], sitk.sitkFloat32)
moving = sitk.ReadImage(argv[2], sitk.sitkFloat32)

resampler = sitk.ResampleImageFilter()
resampler.SetReferenceImage(fixed);
resampler.SetInterpolator(sitk.sitkLinear)
resampler.SetDefaultPixelValue(100)
resampler.SetTransform(read_result)

out = resampler.Execute(moving)
simg1 = sitk.Cast(sitk.RescaleIntensity(fixed), sitk.sitkUInt8)
simg2 = sitk.Cast(sitk.RescaleIntensity(out), sitk.sitkUInt8)
cimg = sitk.Compose(simg1, simg2, simg1//2.+simg2//2.)
sitk.Show( cimg, "ImageRegistration4 Composition" )
