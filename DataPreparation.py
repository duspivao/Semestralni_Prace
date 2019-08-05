import os
import SimpleITK as sitk
import types
import datetime


def saveImageAsNrrd(image, identifier, **kwargs):
    """
    save image in NRRD format using SimpleITK writer.
    :param image: SimpleITK image
    :param identifier: Name of image
    :param kwargs:
        useTimeStampName [boolean] = (True) use time stamp in name of saved image
        outputFolder [string] = output folder absolute path, if not set folder of this script will be used

    :return: 0 if saved successful
    """
    writer = sitk.ImageFileWriter()
    useTimeStampName = True
    outputFolder = ''
    for key, value in kwargs.items():
        if key == 'useTimeStampName':
            if type(value) <> types.BooleanType:
                raise ValueError("Variable useTimeStampName has to be boolean")
            else:
                useTimeStampName = value
        if key == 'outputFolder':
            if type(value) <> types.StringType:
                raise ValueError("Variable outputFolder has to be string")
            else:
                outputFolder = value


    # Output direction in project folder
    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in



    if len(outputFolder) > 1:
        rel_path = outputFolder+"Results/"
    else:
        rel_path = "Results/"

    if useTimeStampName:
        st = datetime.datetime.now().strftime("%d_%m_%y_%H%M")
        outputDirPathTemp = rel_path + st
    else:
        outputDirPathTemp = rel_path

    abs_file_path = os.path.join(script_dir, outputDirPathTemp)

    if not os.path.exists(abs_file_path):
        os.makedirs(abs_file_path)
    try:
        writer.SetFileName(abs_file_path+identifier+'.nrrd')
        writer.Execute(image)
    except Exception as e:
        print(e)
        return -1

    return 0

def readDICOMSerieToImage(folder, **kwargs):
    """
    load DICOM serie from set folder and optionally save the image. This function also casts image to Int16, because MRI
    can be uInt16
    Args:
        folder - absolute path to resource DICOM folder
        *argv
            saveImageToNrrd [boolean] = (False) if true then write image to output folder or same folder as script is
            when set true
            useTimeStampName [boolean] = (True) use time stamp in name of saved image if saveImageToNrrd == TRUE
            outputFolder [string] = name of folder
            identifier [string] = (same as folder) identifier of image use as name to save if saveImageToNrrd == TRUE
    Returns image itk::simple::Image if there is any error in reading return -1
    """

    # Define default values
    saveImageToNrrd = False
    useTimeStampName = True
    outputFolder = ''
    identifier = folder

    for key, value in kwargs.items():
        if key == 'saveImageToNrrd':
            if type(value) <> types.BooleanType:
                raise ValueError("Variable saveImageToNrrd has to be boolean")
            else:
                saveImageToNrrd = value
        elif key == 'useTimeStampName':
            if type(value) <> types.BooleanType:
                raise ValueError("Variable useTimeStampName has to be boolean")
            else:
                useTimeStampName = value
        elif key == 'outputFolder':
            if type(value) <> types.StringType:
                raise ValueError("Variable outputFolder has to be boolean")
            else:
                outputFolder = value

    print("Reading DICOMs from directory:", folder)

    # Simple ITK Series Reader
    reader = sitk.ImageSeriesReader()

    dicom_names = reader.GetGDCMSeriesFileNames(folder)
    reader.SetFileNames(dicom_names)

    try:
        image = reader.Execute()
    except Exception as e:
        print(e)
        return -1

    size = image.GetSize()
    print("Image size:", size[0], size[1], size[2])

    caster = sitk.CastImageFilter()
    caster.SetOutputPixelType(sitk.sitkFloat32)

    imageToReturn = caster.Execute(image)

    if saveImageToNrrd:
        saveImageAsNrrd(imageToReturn, identifier, outputFolder=outputFolder, useTimeStampName=useTimeStampName)


    return image


def readNrrdToImage(folder, **kwargs):
    """
    load DICOM serie from set folder and optionally save the image. This function also casts image to Int16, because MRI
    can be uInt16
    Args:
        folder - absolute path to resource DICOM folder
        *argv

            saveImageToNrrd [boolean] = (False) if true then write image to output folder or same folder as script is
            when set true
            useTimeStampName [boolean] = (True) use time stamp in name of saved image if saveImageToNrrd == TRUE
            outputFolder [string] = name of folder
            identifier [string] = (same as folder) identifier of image use as name to save if saveImageToNrrd == TRUE
    Returns image itk::simple::Image if there is any error in reading return -1
    """

    # Define default values
    saveImageToNrrd = False
    useTimeStampName = True
    outputFolder = ''
    identifier = folder

    for key, value in kwargs.items():
        if key == 'saveImageToNrrd':
            if type(value) <> types.BooleanType:
                raise ValueError("Variable saveImageToNrrd has to be boolean")
            else:
                saveImageToNrrd = value
        elif key == 'useTimeStampName':
            if type(value) <> types.BooleanType:
                raise ValueError("Variable useTimeStampName has to be boolean")
            else:
                useTimeStampName = value
        elif key == 'outputFolder':
            if type(value) <> types.StringType:
                raise ValueError("Variable outputFolder has to be boolean")
            else:
                outputFolder = value

    print("Reading DICOMs from directory:", folder)

    # Simple ITK Series Reader
    reader = sitk.ImageFileReader()

    if folder[len(folder)-5:] != '.nrrd':
        raise ValueError("Path is not nrrd image.")

    reader.SetFileName(folder)

    try:
        image = reader.Execute()
    except Exception as e:
        print(e)
        return -1

    size = image.GetSize()
    print("Image size:", size[0], size[1], size[2])

    caster = sitk.CastImageFilter()
    caster.SetOutputPixelType(sitk.sitkFloat32)

    imageToReturn = caster.Execute(image)

    if saveImageToNrrd:
        saveImageAsNrrd(imageToReturn, identifier, outputFolder=outputFolder, useTimeStampName=useTimeStampName)

    return imageToReturn