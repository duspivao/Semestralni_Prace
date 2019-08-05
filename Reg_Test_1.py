import datetime
from skimage.filters import frangi, hessian
import SimpleITK as sitk
import os
import itk
import frangi
import matplotlib.pyplot as plt

mov = 'C:/ZCU/3Dircadb1/3Dircadb1.1/PATIENT_DICOM'
mask = 'C:/ZCU/3Dircadb1/3Dircadb1.1/MASKS_DICOM/liver'

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
rel_path = "RegistrationTests/"
st = datetime.datetime.now().strftime("%d_%m_%y_%H%M")
outputDirPath = rel_path+'test'
if not os.path.exists(outputDirPath):
    os.makedirs(outputDirPath)
abs_file_path = os.path.join(script_dir, outputDirPath+'/')

def readDICOMSerieToImage(folder, *argv):
    """
    load DICOM serie from set folder and optionally save the image. This function also casts image to Int16, because MRI
    can be uInt16
    Args:
        folder - absolute path to resource DICOM folder
        *argv
            [0] - identifier = string that will be used as part of name in result image written by this function
            [1] - resultFolder = string - absolute path where should be saved 3D image in nrrd
            [2] - showImage = int 1/0 1=show image using sitk.Show; 0=don't show nothing
            [3] - save image = int 1/0 1=save image as nrrd
    """
    print("Reading DICOMs from directory:", folder)
    reader = sitk.ImageSeriesReader()

    dicom_names = reader.GetGDCMSeriesFileNames(folder)
    reader.SetFileNames(dicom_names)


    caster = sitk.CastImageFilter()
    caster.SetOutputPixelType(sitk.sitkFloat32)
    image = caster.Execute(reader.Execute())

    size = image.GetSize()
    print("Image size:", size[0], size[1], size[2])


    if len(argv) >= 2:
        identifier = argv[0]
        resultFolder = argv[1]

        nameOfResImgWithPath = resultFolder+identifier+'.nrrd'
        print("Writing image:", nameOfResImgWithPath)
        if len(argv) >= 4:
            if argv[3] == 0:
                return image
            else:
                sitk.WriteImage(image, nameOfResImgWithPath)

        if len(argv) > 2:
            if argv[2] == 1:
                sitk.Show(sitk.ReadImage('C:/Users/duso/PycharmProjects/Semestralni_Prace/Old_tests/Results3/26_07_19_1111/MRI.nrrd'), 'test')
        return image

image = readDICOMSerieToImage(mov,'livers',abs_file_path,0 ,0)

nImg = sitk.GetArrayFromImage(image)

mask = readDICOMSerieToImage(mask,'MRI',abs_file_path,0 ,0)
nMask = sitk.GetArrayFromImage(mask)
temp = nMask*nImg


onlyLiversImage = itk.GetImageFromArray(temp)

PixelType = itk.ctype('signed short')
Dimension = 3

ImageType = itk.Image[PixelType, Dimension]



result = frangi.frangi(temp, scale_range=(1, 10), scale_step=2, alpha=0.5, beta=0.5, frangi_c=500, black_vessels=True)
outFileName = 'FrangiFilter.mha'
writer2 = sitk.ImageFileWriter()
writer2.SetFileName(outputDirPath + '/' + outFileName)

writer2.Execute(sitk.GetImageFromArray(result))


# frangis = itk.FrangiTubularnessImageFilter[
#     ImageType,
#     ImageType].New()
# frangis.SetInput(onlyLiversImage)
# res = frangis.GetOutput()


# medianFilter = itk.FrangiTubularnessImageFilter[ImageType, ImageType].New()
# medianFilter.SetInput(onlyLiversImage)
# medianFilter.SetRadius(2)
# medianFilter.GetOutput()



# fig, ax = plt.subplots(ncols=3)
#
# ax[0].imshow(image, cmap=plt.cm.gray)
# ax[0].set_title('Original image')
#
# ax[1].imshow(frangi(image), cmap=plt.cm.gray)
# ax[1].set_title('Frangi filter result')
#
# ax[2].imshow(hessian(image), cmap=plt.cm.gray)
# ax[2].set_title('Hybrid Hessian filter result')
#
# for a in ax:
#     a.axis('off')
#
# plt.tight_layout()
# plt.show()