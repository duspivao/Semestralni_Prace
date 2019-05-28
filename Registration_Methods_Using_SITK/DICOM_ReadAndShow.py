import SimpleITK as sitk
import itk

label = 'LABELLED_DICOM'
inputFixDirName = 'C:/ZCU/3Dircadb1/3Dircadb1.1/'+label

reader = sitk.ImageSeriesReader()
dicom_names = reader.GetGDCMSeriesFileNames( inputFixDirName )
print(dicom_names[0])
reader.SetFileNames(dicom_names)
image = reader.Execute()
sitk.Show(image, "DeformableRegistration1 Composition")