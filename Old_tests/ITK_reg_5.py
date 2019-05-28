import itk
import os

label = 'PATIENT_DICOM'

InputImageType  = itk.Image.SS2

FixedImageType = InputImageType
MovingImageType = InputImageType
OutPutImageType = itk.Image.UC2
TransformType = itk.CenteredRigid2DTransform

fixedImageReader = itk.ImageFileReader[FixedImageType].New()
movingImageReader = itk.ImageFileReader[MovingImageType].New()

fixedImageReader.SetFileName('C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/3Dircadb1.1/'+label+'/image_13')
movingImageReader.SetFileName('C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/3Dircadb1.3/'+label+'/image_38')

fixedImageReader.Update()
movingImageReader.Update()

fixedImage = fixedImageReader.GetOutput()
movingImage = movingImageReader.GetOutput()

registration = itk.ImageRegistrationMethod[fixedImage, movingImage].New()
imageMetric = itk.MeanSquaresImageToImageMetric[FixedImageType, MovingImageType].New()
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

#####INITIAL PARAMETERS#####
transform.SetAngle(0.0)

#Center of fixed image
fixedSpacing = fixedImage.GetSpacing()
fixedOrigin  = fixedImage.GetOrigin()

transform.SetIdentity()
initialParameters = transform.GetParameters()
registration.SetInitialTransformParameters( initialParameters )
fixedSize    = fixedImage.GetLargestPossibleRegion().GetSize()

centerFixed  = ( fixedOrigin.GetElement(0) + fixedSpacing.GetElement(0) * fixedSize.GetElement(0) / 2.0, fixedOrigin.GetElement(1) + fixedSpacing.GetElement(1) * fixedSize.GetElement(1) / 2.0 )

#Center of moving image
movingSpacing= movingImage.GetSpacing()
movingOrigin = movingImage.GetOrigin()
movingSize   = movingImage.GetLargestPossibleRegion().GetSize()

centerMoving = ( movingOrigin.GetElement(0) + movingSpacing.GetElement(0) * movingSize.GetElement(0) / 2.0, movingOrigin.GetElement(1) + movingSpacing.GetElement(1) * movingSize.GetElement(1) / 2.0  )

#transform center
center       = transform.GetCenter()
center.SetElement( 0, centerFixed[0] )
center.SetElement( 1, centerFixed[1] )


# transform translation
translation  = transform.GetTranslation()
translation.SetElement( 0, centerMoving[0] - centerFixed[0] )
translation.SetElement( 1, centerMoving[1] - centerFixed[1] )

initialParameters = transform.GetParameters()

print "Initial Parameters: "
print "Angle: %f" % (initialParameters.GetElement(0), )
print "Center: %f, %f" % ( initialParameters.GetElement(1), initialParameters.GetElement(2) )
print "Translation: %f, %f" % (initialParameters.GetElement(3), initialParameters.GetElement(4))



registration.SetInitialTransformParameters( initialParameters )
##########Define optimizer parameters
translationScale = 1.0 / 1000.0
optimizerScales  = itk.Array[itk.D](transform.GetNumberOfParameters())
optimizerScales.SetElement(0, 1.0)
optimizerScales.SetElement(1, translationScale)
optimizerScales.SetElement(2, translationScale)
optimizerScales.SetElement(3, translationScale)
optimizerScales.SetElement(4, translationScale)

optimizer.SetScales( optimizerScales )
optimizer.SetMaximumStepLength( 0.1 )
optimizer.SetMinimumStepLength( 0.001 )
optimizer.SetNumberOfIterations( 200 )

def iterationUpdate():
    currentParameter = transform.GetParameters()
    print "M: %f   P: %f %f %f %f %f  " % (optimizer.GetValue(), currentParameter.GetElement(0), currentParameter.GetElement(1), currentParameter.GetElement(2), currentParameter.GetElement(3), currentParameter.GetElement(4) )

iterationCommand = itk.PyCommand.New()
iterationCommand.SetCommandCallable(iterationUpdate)
optimizer.AddObserver(itk.IterationEvent(), iterationCommand)

optimizer.SetMaximumStepLength(  4.00 )
optimizer.SetMinimumStepLength(  0.01 )

optimizer.SetNumberOfIterations( 200  )
print "Starting registration"
#STARTING REG PROCESS#
registration.Update()

bestValue = optimizer.GetValue()
numberOfIterations = optimizer.GetCurrentIteration()

finalParameters = registration.GetLastTransformParameters()
print "Final Registration Parameters "
print "Angle in radians  = %f" % finalParameters.GetElement(0)
print "Rotation Center X = %f" % finalParameters.GetElement(1)
print "Rotation Center Y = %f" % finalParameters.GetElement(2)
print "Translation in  X = %f" % finalParameters.GetElement(3)
print "Translation in  Y = %f" % finalParameters.GetElement(4)
print(" Iterations    = " + str(numberOfIterations))
print(" Metric value  = " + str(bestValue))
print finalParameters

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

writer = itk.ImageFileWriter[OutPutImageType].New()


newpath = 'C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/03'
if not os.path.exists(newpath):
    os.makedirs(newpath)

writer.SetFileName( newpath+'/result.png' )
writer.SetInput( outputCast.GetOutput() )
writer.Update()

filter = itk.RescaleIntensityImageFilter[FixedImageType, OutPutImageType].New()
filter.SetOutputMinimum( 0 )
filter.SetOutputMaximum(255)
filter.SetInput(fixedImage )

writer.SetFileName( newpath+'/fixed.png' )
writer.SetInput( filter.GetOutput() )
writer.Update()

filter = itk.RescaleIntensityImageFilter[MovingImageType, OutPutImageType].New()
filter.SetOutputMinimum( 0 )
filter.SetOutputMaximum(255)
filter.SetInput(movingImage )

writer.SetFileName( newpath+'/moving.png' )
writer.SetInput( filter.GetOutput() )
writer.Update()


OutputPixelType = itk.ctype('unsigned char')
OutputImageType = itk.Image[OutputPixelType, 2]

caster = itk.CastImageFilter[FixedImageType,
        OutputImageType].New(Input=resampler)

newpath = 'C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/X_01'
if not os.path.exists(newpath):
    os.makedirs(newpath)
outputImageFile = 'C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/X_01/res.png'
differenceImageAfterFile = 'C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/X_01/difAfter.png'
differenceImageBeforeFile = 'C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/X_01/difBefore.png'

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



print('===END===')