#!/usr/bin/env python

from __future__ import print_function

import SimpleITK as sitk
import os
import datetime


# label = 'PATIENT_DICOM'
label = 'TEMP'
inputFile = 'C:/ZCU/DATA_FOR_TEST/TCGA-LIHC/TCGA-BC-A10X/11-22-1992-MRI ABD WWO CONT-49239/11-LIVER-GAD-ENHANCEMENTT1F-68307'

newpath = 'C:/ZCU/Results/'
st = datetime.datetime.now().strftime("%d_%m_%y_%H%M")
newpath = newpath+st

outputFile = newpath

print( "Reading Dicom directory:", inputFile)
reader = sitk.ImageSeriesReader()

dicom_names = reader.GetGDCMSeriesFileNames( inputFile)
reader.SetFileNames(dicom_names)

image = reader.Execute()

size = image.GetSize()
print( "Image size:", size[0], size[1], size[2] )
#
# print( "Writing image:", outputFile)
#
# # sitk.WriteImage( image, outputFile )

if ( not "SITK_NOSHOW" in os.environ ):
    sitk.Show( image, "Dicom Series" )