#!/usr/bin/env python
import os
import itk
import sys
import datetime

label = 'LABELLED_DICOM'
dirName = 'C:/ZCU/3Dircadb1/3Dircadb1.7/'+label

newpath = 'C:/ZCU/Results/'
# st = datetime.datetime.now().strftime("%d_%m_%y_%H%M")
st=''
outPutDir = newpath+st


if not os.path.exists(outPutDir):
    os.makedirs(outPutDir)
# outPutDir = 'C:/ZCU'
PixelType = itk.ctype('signed short')
Dimension = 3

ImageType = itk.Image[PixelType, Dimension]

namesGenerator = itk.GDCMSeriesFileNames.New()
namesGenerator.SetUseSeriesDetails(True)
# namesGenerator.AddSeriesRestriction("00001|0021")
namesGenerator.SetGlobalWarningDisplay(False)
namesGenerator.SetDirectory(dirName)

seriesUID = namesGenerator.GetSeriesUIDs()

if len(seriesUID) < 1:
    print('No DICOMs in: ' + dirName)
    sys.exit(1)

print('The directory: ' + dirName)
print('Contains the following DICOM Series: ')
for uid in seriesUID:
    print(uid)

seriesFound = False
for uid in seriesUID:
    seriesIdentifier = uid

    print('Reading: ' + seriesIdentifier)
    fileNames = namesGenerator.GetFileNames(seriesIdentifier)

    reader = itk.ImageSeriesReader[ImageType].New()
    dicomIO = itk.GDCMImageIO.New()
    reader.SetImageIO(dicomIO)
    reader.SetFileNames(fileNames)
    test = reader.GetOutput()
    writer = itk.ImageFileWriter[ImageType].New()
    seriesIdentifier = 'test'
    # outFileName = os.path.join(outPutDir, seriesIdentifier + '')

    outFileName = 'DIC_L02.nrrd'
    writer.SetFileName(outPutDir+'/'+outFileName)
    writer.UseCompressionOn()
    writer.SetInput(reader.GetOutput())
    print('Writing: ' + outPutDir+'/'+outFileName)
    writer.Update()

    if seriesFound:
        break

