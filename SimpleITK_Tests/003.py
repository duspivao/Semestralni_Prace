#!/usr/bin/env python

from __future__ import print_function

import itk
import os
import datetime


label = 'PATIENT_DICOM'
inputFile = 'C:/ZCU/3Dircadb1/3Dircadb1.7/'+label

newpath = 'C:/ZCU/Results/'
st = datetime.datetime.now().strftime("%d_%m_%y_%H%M")
newpath = newpath+st

outputFile = newpath

PixelType = itk.ctype('signed short')
Dimension = 3

ImageType = itk.Image[PixelType, Dimension]


print( "Reading Dicom directory:", inputFile)
reader = itk.ImageSeriesReader[ImageType].new()

dicom_names = reader.GetGDCMSeriesFileNames( inputFile)
reader.SetFileNames(dicom_names)

image = reader.Execute()