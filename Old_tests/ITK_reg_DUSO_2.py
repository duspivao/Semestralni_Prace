import itk
import os
# import matplotlib.pyplot as plt
import numpy as np
import datetime
import time
import scipy.misc

###MUTUAL INFORMATION METRIC and TranslationTransform

def diceMetrics(img1, img2):
    max, min = img1.max(), img1.min()
    img1 = (img1 - min) / (max-min)
    # img1 = (img1 - np.min(img1))/np.ptp(img1).astype(int)

    # img2 = (img2 - np.min(img2)) / np.ptp(img2).astype(int)

    max2, min2 = img2.max(), img2.min()
    img2 = (img2 - min2) / (max2 - min2)
    img2 = (img2 <> 0)*1
    dif = np.absolute(img1-img2)
    suma = dif.sum()*1.

    sumaTog = (img1.sum()+img2.sum())/2.
    # x,y = img1.shape
    # imTogether = np.zeros((x,y))
    # for i in range(0,x,1):
    #     for j in range(0,y,1):
    #         imTogether[i,j] = np.logical_and(img1[i,j],img2[i,j])
    #
    # sumaTog = imTogether.sum()*1.
    if sumaTog == 0.0:
        return -1
    return suma/sumaTog

ts = time.time()
actualTime =  datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M%S')
label = 'PATIENT_DICOM'
labelLiver = 'MASKS_DICOM/liver'
labelBones = 'MASKS_DICOM/bone'
labelRightLung = 'MASKS_DICOM/rightlung'
labelLeftLung = 'MASKS_DICOM/leftlung'

no1 = '145'
no2 = '126'


newpath = 'C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/Results/'+actualTime+'pataSadaTransMS'
if not os.path.exists(newpath):
    os.makedirs(newpath)

InputImageType  = itk.Image.SS2

FixedImageType = InputImageType
MovingImageType = InputImageType
OutPutImageType = itk.Image.SS2
TransformType = itk.TranslationTransform[itk.D, 2]

fixedImageReader = itk.ImageFileReader[FixedImageType].New()
movingImageReader = itk.ImageFileReader[MovingImageType].New()

fixedLiverReader = itk.ImageFileReader[FixedImageType].New()
movingLiverReader = itk.ImageFileReader[MovingImageType].New()

fixedRLungReader = itk.ImageFileReader[FixedImageType].New()
movingRLungReader = itk.ImageFileReader[MovingImageType].New()

fixedBonesReader = itk.ImageFileReader[FixedImageType].New()
movingBonesReader = itk.ImageFileReader[MovingImageType].New()
# fixedLiverReader = itk.ImageFileReader[FixedImageType].New()
# movingLiverReader = itk.ImageFileReader[MovingImageType].New()


fixedImageReader.SetFileName('C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/3Dircadb1.7/'+label+'/image_'+no1)
movingImageReader.SetFileName('C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/3Dircadb1.1/'+label+'/image_'+no2)

fixedLiverReader.SetFileName('C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/3Dircadb1.7/'+labelLiver+'/image_'+no1)
movingLiverReader.SetFileName('C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/3Dircadb1.1/'+labelLiver+'/image_'+no2)

fixedRLungReader.SetFileName('C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/3Dircadb1.7/'+labelRightLung+'/image_'+no1)
movingRLungReader.SetFileName('C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/3Dircadb1.1/'+labelRightLung+'/image_'+no2)

fixedBonesReader.SetFileName('C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/3Dircadb1.7/'+labelBones+'/image_'+no1)
movingBonesReader.SetFileName('C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/3Dircadb1.1/'+labelBones+'/image_'+no2)

fixedImageReader.Update()
movingImageReader.Update()

fixedLiverReader.Update()
movingLiverReader.Update()

fixedRLungReader.Update()
movingRLungReader.Update()

fixedBonesReader.Update()
movingBonesReader.Update()

fixedImage = fixedImageReader.GetOutput()
movingImage = movingImageReader.GetOutput()

fixedLiver = fixedLiverReader.GetOutput()
movingLiver = movingLiverReader.GetOutput()

fixedRLung = fixedRLungReader.GetOutput()
movingRLung = movingRLungReader.GetOutput()

fixedBones = fixedBonesReader.GetOutput()
movingBones = movingBonesReader.GetOutput()



w1 = itk.ImageFileWriter[itk.Image.UC2].New()

filter = itk.RescaleIntensityImageFilter[InputImageType, itk.Image.UC2].New()
filter.SetOutputMinimum( 0 )
filter.SetOutputMaximum(255)

filter.SetInput( fixedImage )
w1.SetInput( filter.GetOutput() )
w1.SetFileName(newpath+'/fixed.png')
w1.Update()

filter.SetInput( movingImage )
w1.SetInput( filter.GetOutput() )
w1.SetFileName(newpath+'/moving.png')
w1.Update()

filter.SetInput( fixedLiver )
w1.SetInput( filter.GetOutput() )
w1.SetFileName(newpath+'/liverFixed.png')
w1.Update()

filter.SetInput( movingLiver )
w1.SetInput( filter.GetOutput() )
w1.SetFileName(newpath+'/liverMoving.png')
w1.Update()

filter.SetInput( fixedRLung )
w1.SetInput( filter.GetOutput() )
w1.SetFileName(newpath+'/rLungFixed.png')
w1.Update()

filter.SetInput( movingRLung )
w1.SetInput( filter.GetOutput() )
w1.SetFileName(newpath+'/rLungMoving.png')
w1.Update()

registration = itk.ImageRegistrationMethod[fixedImage, movingImage].New()


imageMetric = itk.MattesMutualInformationImageToImageMetric[FixedImageType, MovingImageType].New()
imageMetric.SetNumberOfHistogramBins( 20 )
imageMetric.SetNumberOfSpatialSamples( 10000 )

transform = TransformType.New()
optimizer = itk.RegularStepGradientDescentOptimizer.New()
interpolator = itk.LinearInterpolateImageFunction[FixedImageType, itk.D].New()

registration.SetOptimizer(    optimizer    )
registration.SetTransform(    transform    )
registration.SetInterpolator( interpolator )
registration.SetMetric(       imageMetric  )


registration.SetFixedImage(  fixedImage  )
registration.SetMovingImage( movingImage )

registration.SetFixedImageRegion( fixedImage.GetBufferedRegion() )

transform.SetIdentity()
initialParameters = transform.GetParameters()
registration.SetInitialTransformParameters( initialParameters )


def iterationUpdate():
    currentParameter = transform.GetParameters()
    print "M: %f   P: %f %f " % (optimizer.GetValue(), currentParameter.GetElement(0), currentParameter.GetElement(1) )

iterationCommand = itk.PyCommand.New()
iterationCommand.SetCommandCallable(iterationUpdate)
optimizer.AddObserver(itk.IterationEvent(), iterationCommand)

optimizer.SetMaximumStepLength(  4.00 )
optimizer.SetMinimumStepLength(  0.01 )
optimizer.SetNumberOfIterations( 200  )

print "Starting registration"
#STARTING REG PROCESS#
registration.Update()

finalParameters = registration.GetLastTransformParameters()
print "Final Registration Parameters "
print "Translation X =  %f" % (finalParameters.GetElement(0),)
print "Translation Y =  %f" % (finalParameters.GetElement(1),)


resampler = itk.ResampleImageFilter[MovingImageType, FixedImageType].New()
resampler.SetTransform( transform    )
resampler.SetInput(     movingImage  )

region = fixedImage.GetLargestPossibleRegion()

resampler.SetSize( region.GetSize() )


resampler.SetOutputSpacing( fixedImage.GetSpacing() )
resampler.SetOutputOrigin(  fixedImage.GetOrigin()  )
resampler.SetOutputDirection(  fixedImage.GetDirection()  )
resampler.SetDefaultPixelValue( 100 )

outputCast = itk.RescaleIntensityImageFilter[FixedImageType, OutPutImageType].New()
outputCast.SetInput(resampler.GetOutput())



####################DICE METRICS FOR LIVERS#############

rLiver = itk.ResampleImageFilter[MovingImageType, FixedImageType].New()
rLiver.SetTransform( transform    )
rLiver.SetInput(     movingLiver  )

region = fixedLiver.GetLargestPossibleRegion()

rLiver.SetSize( region.GetSize() )


rLiver.SetOutputSpacing( fixedLiver.GetSpacing() )
rLiver.SetOutputOrigin(  fixedLiver.GetOrigin()  )
rLiver.SetOutputDirection(  fixedLiver.GetDirection()  )
rLiver.SetDefaultPixelValue( 0 )

rLiver.SetInput(movingLiver)

outputCastLiver = itk.RescaleIntensityImageFilter[InputImageType, OutPutImageType].New()
outputCastLiver.SetInput(rLiver.GetOutput())

movingLiverTArr = itk.GetArrayFromImage(outputCastLiver.GetOutput())
fixedLiverArr =  itk.GetArrayFromImage(fixedLiver)
# diceMetrics(fixedLiverArr,movingLiverTArr)
scipy.misc.imsave(newpath+'/liverMovingT.png', np.array(movingLiverTArr,dtype=np.float32))

print('Liver metrics:'+str(diceMetrics(fixedLiverArr,movingLiverTArr)))

###########################################################

####################DICE METRICS FOR R LUNG#############

rLung = itk.ResampleImageFilter[MovingImageType, FixedImageType].New()
rLung.SetTransform( transform    )
rLung.SetInput(     movingRLung  )

region = fixedRLung.GetLargestPossibleRegion()

rLung.SetSize( region.GetSize() )


rLung.SetOutputSpacing( fixedRLung.GetSpacing() )
rLung.SetOutputOrigin(  fixedRLung.GetOrigin()  )
rLung.SetOutputDirection(  fixedRLung.GetDirection()  )
rLung.SetDefaultPixelValue( 0 )

rLung.SetInput(movingRLung)

outputCastLRLung = itk.RescaleIntensityImageFilter[InputImageType, OutPutImageType].New()
outputCastLRLung.SetInput(rLung.GetOutput())

movingRLungArr = itk.GetArrayFromImage(outputCastLRLung.GetOutput())
fixedRLungArr =  itk.GetArrayFromImage(fixedRLung)
# diceMetrics(fixedLiverArr,movingLiverTArr)
# scipy.misc.imsave(newpath+'/liverMovingT.png', np.array(movingRLungArr,dtype=np.float32))

print('Right Lung metrics:'+str(diceMetrics(fixedRLungArr,np.array(movingRLungArr,dtype=np.int16))))

###########################################################

####################DICE METRICS BONES#############

rBones = itk.ResampleImageFilter[MovingImageType, FixedImageType].New()
rBones.SetTransform( transform    )
rBones.SetInput(     movingBones  )

region = fixedBones.GetLargestPossibleRegion()

rBones.SetSize( region.GetSize() )


rBones.SetOutputSpacing( fixedBones.GetSpacing() )
rBones.SetOutputOrigin(  fixedBones.GetOrigin()  )
rBones.SetOutputDirection(  fixedBones.GetDirection()  )
rBones.SetDefaultPixelValue( 0 )

rBones.SetInput(movingBones)

outputCastBones = itk.RescaleIntensityImageFilter[InputImageType, OutPutImageType].New()
outputCastBones.SetInput(rBones.GetOutput())

movingBonesArr = itk.GetArrayFromImage(outputCastBones.GetOutput())
fixedBonesArr =  itk.GetArrayFromImage(fixedBones)
# diceMetrics(fixedLiverArr,movingLiverTArr)
# scipy.misc.imsave(newpath+'/liverMovingT.png', np.array(movingRLungArr,dtype=np.float32))

print('Bones metrics:'+str(diceMetrics(fixedBonesArr,np.array(movingBonesArr,dtype=np.int16))))

###########################################################




writer = itk.ImageFileWriter[OutPutImageType].New()


outputImageFile = newpath+'/res.png'
writer.SetFileName( newpath+'/result.png' )
array = itk.GetArrayFromImage(outputCast.GetOutput())
# plt.imshow(np.array(array,dtype=np.float32),  cmap='gray')
# plt.waitforbuttonpress(1000)
scipy.misc.imsave(newpath+'/result.png', np.array(array,dtype=np.float32))

caster = itk.CastImageFilter[FixedImageType, OutPutImageType].New(Input=resampler)
array = itk.GetArrayFromImage(caster)
# plt.imshow(np.array(array,dtype=np.float32),  cmap='gray')
# plt.waitforbuttonpress(1000)
scipy.misc.imsave(newpath+'/result2.png', np.array(array,dtype=np.float32))



OutputPixelType = itk.ctype('unsigned char')
OutputImageType = itk.Image[OutputPixelType, 2]

caster = itk.CastImageFilter[FixedImageType,
        OutputImageType].New(Input=resampler)


differenceImageAfterFile = newpath+'/difAfter.png'
differenceImageBeforeFile= newpath+'/difBefore.png'
joinedImagesFile         = newpath+'/joined.png'

writer = itk.ImageFileWriter.New(Input=caster, FileName=outputImageFile)
writer.SetFileName(outputImageFile)
writer.Update()

difference = itk.SubtractImageFilter.New(Input1=fixedImage,
        Input2=resampler)

intensityRescaler = itk.RescaleIntensityImageFilter[FixedImageType,
        OutputImageType].New(
            Input=difference,
            OutputMinimum=itk.NumericTraits[OutputPixelType].min(),
            OutputMaximum=itk.NumericTraits[OutputPixelType].max())

resampler.SetDefaultPixelValue(1)
writer.SetInput(intensityRescaler.GetOutput())
writer.SetFileName(differenceImageAfterFile)
writer.Update()


joinedImages = itk.AddImageFilter.New(fixedImage, resampler)
intensityRescaler = itk.RescaleIntensityImageFilter[FixedImageType,
        OutputImageType].New(
            Input=joinedImages,
            OutputMinimum=itk.NumericTraits[OutputPixelType].min(),
            OutputMaximum=itk.NumericTraits[OutputPixelType].max())
resampler.SetDefaultPixelValue(1)
writer.SetInput(intensityRescaler.GetOutput())
writer.SetFileName(joinedImagesFile)
writer.Update()

resampler.SetTransform(TransformType.New())
writer.SetFileName(differenceImageBeforeFile)
writer.Update()
#


print('===END===')