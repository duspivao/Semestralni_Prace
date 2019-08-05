import itk
import io3d
import numpy as np
import matplotlib.pyplot as plt

# label = '/LABELLED_DICOM'
#
#
# FixedImage=itk.imread("C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/01.png")
#
# itk.imwrite(FixedImage, "C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/output.png")
InputImageType  = itk.Image.SS2
OutputImageType = itk.Image.UC2

reader = itk.ImageFileReader[InputImageType].New()
writer = itk.ImageFileWriter[OutputImageType].New()

filter = itk.RescaleIntensityImageFilter[InputImageType, OutputImageType].New()
filter.SetOutputMinimum( 0 )
filter.SetOutputMaximum(255)

filter.SetInput( reader.GetOutput() )
writer.SetInput( filter.GetOutput() )
reader.SetFileName( 'C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/3Dircadb1.1/LABELLED_DICOM/image_13' )
writer.SetFileName( 'C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/xxx.png' )

writer.Update()