import SimpleITK as sitk
import cv2
import numpy as np
import time
import matplotlib.pyplot as plt

start = time.time()

outputDirPath = 'C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Thresh_'

reader = sitk.ImageFileReader()
writer = sitk.ImageFileWriter()

reader.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Reg_8_GaborliversSmall.nrrd')
imageR = reader.Execute()

caster = sitk.CastImageFilter()
caster.SetOutputPixelType(sitk.sitkUInt8)
image3d = caster.Execute(imageR)

imageArray = sitk.GetArrayFromImage(image3d)
detph = imageArray.shape[0]
seeds = []
meanVal = 0
countPixels = 0
magicConst = 5
for d in range(detph/magicConst, detph - detph/magicConst, magicConst):
    oneSlice = imageArray[d][:][:]
    oneSliceDenoised = oneSlice.copy()
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(5, 5))

    cl1 = clahe.apply(oneSliceDenoised)
    cv2.fastNlMeansDenoising(cl1,oneSliceDenoised, h=40)

    blobDetector = cv2.SimpleBlobDetector()
    keyPoints = blobDetector.detect(oneSliceDenoised)
    # im_with_keypoints = cv2.drawKeypoints(oneSlice, keyPoints, np.array([]), (255, 255, 255),
    #                                       cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    # plt.imshow(im_with_keypoints, cmap='gray')
    # plt.show()
    plt.imshow(oneSliceDenoised, cmap='gray')
    plt.show()
    if len(keyPoints)>0:
        tempPoint = []
        for point in keyPoints:
            p = (int(point.pt[0]),int(point.pt[1]))
            seeds.append(p)
            tempPoint.append(p)
            print p

        segCon = sitk.ConnectedThreshold(sitk.Cast(sitk.GetImageFromArray(oneSliceDenoised),sitk.sitkUInt32), seedList=tempPoint,
                                          lower=1, upper=110)
        # compute mean value of blobs with grow region
        segConArr = sitk.GetArrayFromImage(segCon)
        meanVal += np.sum(oneSlice*segConArr)
        countPixels += np.sum(segConArr)

        plt.imshow(sitk.GetArrayFromImage(segCon), cmap='gray')
        plt.show()
print seeds
print meanVal/countPixels