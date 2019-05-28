import itk
import os

label = 'PATIENT_DICOM'

InputImageType  = itk.Image.SS2

FixedImageType = InputImageType
MovingImageType = InputImageType
OutPutImageType = itk.Image.UC2
TransformType = itk.TranslationTransform[itk.D, 2]

fixedImageReader = itk.ImageFileReader[FixedImageType].New()
movingImageReader = itk.ImageFileReader[MovingImageType].New()

fixedImageReader.SetFileName('C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/3Dircadb1.1/'+label+'/image_13')
movingImageReader.SetFileName('C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/3Dircadb1.3/'+label+'/image_38')

fixedImageReader.Update()
movingImageReader.Update()

fixedImage = fixedImageReader.GetOutput()
movingImage = movingImageReader.GetOutput()

registration = itk.ImageRegistrationMethod[fixedImage, movingImage].New()
imageMetric = itk.MattesMutualInformationImageToImageMetric[FixedImageType, MovingImageType].New()
transform = TransformType.New()
optimizer = itk.RegularStepGradientDescentOptimizer.New()
interpolator = itk.LinearInterpolateImageFunction[FixedImageType, itk.D].New()

imageMetric.SetNumberOfHistogramBins( 20 )
imageMetric.SetNumberOfSpatialSamples( 10000 )

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

writer = itk.ImageFileWriter[OutPutImageType].New()


newpath = 'C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/02'
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

print('===END===')