import itk



label = 'PATIENT_DICOM'

InputImageType  = itk.Image.SS2

FixedImageType = InputImageType
MovingImageType = InputImageType
OutPutImageType = itk.Image.UC2
TransformType = itk.ThinPlateSplineKernelTransform[itk.D, 2]

######READING IMAGES#####
fixedImageReader = itk.ImageFileReader[FixedImageType].New()
movingImageReader = itk.ImageFileReader[MovingImageType].New()

fixedImageReader.SetFileName('C:/ZCU/3Dircadb1/3Dircadb1.1/'+label+'/image_13')
movingImageReader.SetFileName('C:/ZCU/3Dircadb1/3Dircadb1.3/'+label+'/image_38')

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
