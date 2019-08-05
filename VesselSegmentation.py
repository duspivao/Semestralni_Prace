import SimpleITK as sitk
import cv2
import numpy as np
from skimage import morphology
from skimage import filters
import itk

def RegionGrow(image,**kwargs):
    seeds = None
    lower = 10
    upper = 100
    mean = None
    tolerance = None
    for key, value in kwargs:
        if key == 'seeds':
            seeds = value
        elif key == 'upper':
            upper = value
        elif key == 'lower':
            lower = value
        elif key == 'tolerance':
            tolerance = value
        elif key == 'mean':
            mean = value

    if seeds == None:
        seeds, mean = getSeeds(image)

    if tolerance != None and mean != None:
        lower = mean - tolerance
        upper = mean + tolerance

    regionGrow = sitk.ConnectedThreshold(image,
                                         seedList=seeds,
                                         lower=lower,
                                         upper=upper)
    return regionGrow

def GaborFilters(image):
    return 0

def FrangiFilters(imageR):
    # outputDirPath = 'C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Filters_'
    #
    # reader = sitk.ImageFileReader()
    # writer = sitk.ImageFileWriter()
    #
    # reader.SetFileName(
    #     'C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Reg_8_GaborliversSmall.nrrd')
    # imageR = reader.Execute()

    caster = sitk.CastImageFilter()
    caster.SetOutputPixelType(sitk.sitkUInt8)
    imgAll = sitk.GetArrayFromImage(caster.Execute(imageR))

    mask = np.zeros(imgAll.shape)
    mask[imgAll > 0] = 1

    xSize = imgAll.shape[0]
    ySize = imgAll.shape[1]
    zSize = imgAll.shape[2]

    scales = np.arange(1.0, 10.0, 1.0)

    filteredX = np.zeros(imgAll.shape)
    for x in range(xSize):
        img = imgAll[x, :, :]
        filteredX[x, :, :] = filters.frangi(img, scale_range=(1.0, 10.0), scale_step=2)

    # writer.SetFileName(outputDirPath + 'VysledekX.nrrd')
    # writer.Execute(sitk.GetImageFromArray(filteredX))

    filteredY = np.zeros(imgAll.shape)
    for y in range(ySize):
        img = imgAll[:, y, :]
        filteredY[:, y, :] = filters.frangi(img, scale_range=(1.0, 10.0), scale_step=2)

    # writer.SetFileName(outputDirPath + 'VysledekY.nrrd')
    # writer.Execute(sitk.GetImageFromArray(filteredY))

    filteredZ = np.zeros(imgAll.shape)
    for z in range(zSize):
        img = imgAll[:, :, z]
        filteredZ[:, :, z] = filters.frangi(img, scale_range=(1.0, 10.0), scale_step=2)

    # writer.SetFileName(outputDirPath + 'VysledekZ.nrrd')
    # writer.Execute(sitk.GetImageFromArray(filteredZ))

    result = (filteredX + filteredY + filteredZ) * mask

    resultImg = sitk.RescaleIntensity(sitk.GetImageFromArray(result))
    # writer.SetFileName(outputDirPath + 'Vysledek.nrrd')
    # writer.Execute(resultImg)

    erode = sitk.GrayscaleErodeImageFilter()
    dilate = sitk.GrayscaleDilateImageFilter()
    erode.SetKernelRadius((1, 1, 1))
    dilate.SetKernelRadius((3, 3, 3))

    res = erode.Execute(dilate.Execute(resultImg))
    # writer.SetFileName(outputDirPath + 'afterMorphology.nrrd')
    # writer.Execute(sitk.RescaleIntensity(res))

    otsuFilter = sitk.OtsuThresholdImageFilter()
    otsuFilter.SetOutsideValue(1)
    otsuFilter.SetInsideValue(0)
    resThresholded = otsuFilter.Execute(res)
    # writer.SetFileName(outputDirPath + 'afterMorphologyThresh.nrrd')
    # writer.Execute(sitk.RescaleIntensity(resThresholded))

    return sitk.RescaleIntensity(resThresholded), filteredX, filteredY, filteredZ, sitk.RescaleIntensity(sitk.GetImageFromArray(result)), sitk.RescaleIntensity(res)

def GetVesselsFromITK(imageSITK, **kwargs):
    imageArray = sitk.GetArrayFromImage(imageSITK)
    image = itk.GetImageFromArray(imageArray)
    sigma = 1
    alpha = 1
    alpha2 = 2
    PixelType = itk.ctype('unsigned short')
    Dimension = 3
    ImageType = itk.Image[PixelType, Dimension]
    GaussSigmas = [3, 2, 2]

    # Smoothing
    SmoothFilterType = itk.SmoothingRecursiveGaussianImageFilter[ImageType, ImageType]
    smoothingFilter = SmoothFilterType.New()
    smoothingFilter.SetInput(image)
    smoothingFilter.SetSigmaArray(GaussSigmas)
    smoothedImg = smoothingFilter.GetOutput()

    # Because this method finds bright structures we have to invert intesity
    InvertIntesityType = itk.InvertIntensityImageFilter[
        itk.Image[itk.ctype('unsigned short'), 3], itk.Image[itk.ctype('unsigned short'), 3]]
    invertI = InvertIntesityType.New()
    invertI.SetInput(smoothedImg)
    invertI.SetMaximum(255)
    imageInverter = invertI.GetOutput()

    HessianFilterType = itk.HessianRecursiveGaussianImageFilter[imageInverter]
    hessianFilter = HessianFilterType.New()
    hessianFilter.SetInput(imageInverter)
    hessianFilter.SetSigma(sigma)
    hesFilteredImage = hessianFilter.GetOutput()

    VesselnessMeasureFilterType = itk.Hessian3DToVesselnessMeasureImageFilter[itk.ctype('float')]
    vesselnessFilter = VesselnessMeasureFilterType.New()
    vesselnessFilter.SetInput(hesFilteredImage)
    vesselnessFilter.SetAlpha1(alpha)
    vesselnessFilter.SetAlpha2(alpha2)
    vesselsImage = vesselnessFilter.GetOutput()

    writerType = itk.ImageFileWriter[vesselsImage]
    writer = writerType.New()
    writer.SetInput(vesselsImage)
    writer.SetFileName(
        'C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/HessianFilter_XXXX.nrrd')
    writer.Update()

def TresholdBySeedsMean(image,**kwargs):
    magicConst = 30
    mean = None
    for key, value in kwargs:
        if key == 'tolerance':
            magicConst = value
        elif key == 'mean':
            mean = value
    if mean == None:
        _, mean = getSeeds(image)

    caster = sitk.CastImageFilter()
    caster.SetOutputPixelType(sitk.sitkUInt8)

    imageUint8 = caster.Execute(image)

    thresholdFilter = sitk.ThresholdImageFilter()
    thresholdFilter.SetLower(mean-magicConst)
    thresholdFilter.SetUpper(mean+magicConst)
    thresholdFilter.SetOutsideValue(0)
    thresholdedImage = thresholdFilter.Execute(imageUint8)

    # morphological operation dilate and erode
    erode = sitk.GrayscaleErodeImageFilter()
    dilate = sitk.GrayscaleDilateImageFilter()
    erode.SetKernelRadius((3, 3, 3))
    dilate.SetKernelRadius((2, 2, 2))

    res = erode.Execute(dilate.Execute(thresholdedImage))
    # res = dilate.Execute(erode.Execute(thresholdedImage))

    numpyImage = sitk.GetArrayFromImage(thresholdedImage)
    binarized = np.where(numpyImage > 0, 1, 0)
    res2 = morphology.remove_small_objects(binarized.astype(bool), min_size=20, connectivity=2).astype(int)

    return res, res2

def getSeeds(image):
    imageArray = sitk.GetArrayFromImage(image)
    detph = imageArray.shape[0]
    seeds = []
    meanVal = 0
    countPixels = 0
    magicConst = 5

    for d in range(detph / magicConst, detph - detph / magicConst, magicConst):
        oneSlice = imageArray[d][:][:]
        oneSliceDenoised = oneSlice.copy()

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(5, 5))
        cl1 = clahe.apply(oneSliceDenoised)
        cv2.fastNlMeansDenoising(cl1, oneSliceDenoised, h=40)

        blobDetector = cv2.SimpleBlobDetector()
        keyPoints = blobDetector.detect(oneSliceDenoised)
        # im_with_keypoints = cv2.drawKeypoints(oneSlice, keyPoints, np.array([]), (255, 255, 255),
        #                                       cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        # plt.imshow(im_with_keypoints, cmap='gray')
        # plt.show()

        if len(keyPoints) > 0:
            tempPoint = []
            for point in keyPoints:
                p = (int(point.pt[0]), int(point.pt[1]))
                seeds.append(p)
                tempPoint.append(p)
                print p

            segCon = sitk.ConnectedThreshold(sitk.Cast(sitk.GetImageFromArray(oneSliceDenoised), sitk.sitkUInt32),
                                             seedList=tempPoint,
                                             lower=1, upper=110)
            # compute mean value of blobs with grow region
            segConArr = sitk.GetArrayFromImage(segCon)
            meanVal += np.sum(oneSlice * segConArr)
            countPixels += np.sum(segConArr)

    meanValRes = meanVal/countPixels
    return seeds, meanValRes

# def ThresholdingOtsuVesselSegmentation(image, **kwargs):
#
#     caster = sitk.CastImageFilter()
#     caster.SetOutputPixelType(sitk.sitkUInt8)
#
#     imageUint8 = caster.Execute(image)
#
#     gaussFilter = sitk.SmoothingRecursiveGaussianImageFilter()
#     bluered = gaussFilter.Execute(imageUint8)
#     writer = sitk.ImageFileWriter()
#     writer.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/FInal_Registration_Folder/Results/test.nrrd')
#     writer.Execute(bluered)
#
#     # only livers image array
#     liversOnlyArray = sitk.GetArrayFromImage(bluered) > 0
#     writer.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/FInal_Registration_Folder/Results/testX.nrrd')
#     writer.Execute(sitk.GetImageFromArray(liversOnlyArray))
#
#
#     # define image filter using otsu
#     otsuThresholdFilter = sitk.OtsuThresholdImageFilter()
#     otsuThresholdFilter.SetInsideValue(1)
#     otsuThresholdFilter.SetOutsideValue(0)
#     thresholdedImage = otsuThresholdFilter.Execute(sitk.GetImageFromArray(liversOnlyArray))
#
#     thresholdedImageRescaled = sitk.RescaleIntensity(thresholdedImage)
#
#     writer.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/FInal_Registration_Folder/Results/test2.nrrd')
#     writer.Execute(thresholdedImageRescaled)
#
#     thresholdedImageArr = sitk.GetArrayFromImage(thresholdedImage) * liversOnlyArray
#
#     finalThresholdedImage = gaussFilter.Execute(sitk.GetImageFromArray(thresholdedImageArr))
#     writer.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/FInal_Registration_Folder/Results/test3.nrrd')
#     writer.Execute(finalThresholdedImage)
#     return finalThresholdedImage