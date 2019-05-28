import itk
import os


label = 'PATIENT_DICOM'
#
# InputImageType  = itk.Image.SS2
#
# FixedImageType = InputImageType
# MovingImageType = InputImageType
# OutPutImageType = itk.Image.UC2
# TransformType = itk.TranslationTransform[itk.D, 2]
#
# fixedImageReader = itk.ImageFileReader[FixedImageType].New()
# movingImageReader = itk.ImageFileReader[MovingImageType].New()
#
# fixedImageReader.SetFileName('C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/3Dircadb1.1/'+label+'/image_13')
# movingImageReader.SetFileName('C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/3Dircadb1.3/'+label+'/image_38')
#
# fixedImageReader.Update()
# movingImageReader.Update()
#
# fixedImage = fixedImageReader.GetOutput()
# movingImage = movingImageReader.GetOutput()


PixelType = itk.ctype('float')
fixedImage = itk.imread('C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/3Dircadb1.1/'+label+'/image_13',PixelType)
movingImage = itk.imread('C:/Users/duso/OneDrive - AIMTEC a. s/Documents/ZDO/SEM/3Dircadb1.1/'+label+'/image_38',PixelType)

Dimension = fixedImage.GetImageDimension()
FixedImageType = itk.Image[PixelType, Dimension]
MovingImageType = itk.Image[PixelType, Dimension]



TransformType = itk.TranslationTransform[itk.D, 2]
initialTransform = TransformType.New()


optimizer = itk.RegularStepGradientDescentOptimizerv4.New(
        LearningRate=4,
        MinimumStepLength=0.001,
        RelaxationFactor=0.5,
        NumberOfIterations=200)

metric = itk.MeanSquaresImageToImageMetricv4[
    FixedImageType, MovingImageType].New()

registration = itk.ImageRegistrationMethodv4.New(FixedImage=fixedImage,
        MovingImage=movingImage,
        Metric=metric,
        Optimizer=optimizer,
        InitialTransform=initialTransform)

movingInitialTransform = TransformType.New()
initialParameters = movingInitialTransform.GetParameters()
initialParameters[0] = 0
initialParameters[1] = 0
movingInitialTransform.SetParameters(initialParameters)
registration.SetMovingInitialTransform(movingInitialTransform)

identityTransform = TransformType.New()
identityTransform.SetIdentity()
registration.SetFixedInitialTransform(identityTransform)

registration.SetNumberOfLevels(1)
registration.SetSmoothingSigmasPerLevel([0])
registration.SetShrinkFactorsPerLevel([1])

registration.Update()

transform = registration.GetTransform()
finalParameters = transform.GetParameters()
translationAlongX = finalParameters.GetElement(0)
translationAlongY = finalParameters.GetElement(1)

numberOfIterations = optimizer.GetCurrentIteration()

bestValue = optimizer.GetValue()

print("Result = ")
print(" Translation X = " + str(translationAlongX))
print(" Translation Y = " + str(translationAlongY))
print(" Iterations    = " + str(numberOfIterations))
print(" Metric value  = " + str(bestValue))

CompositeTransformType = itk.CompositeTransform[itk.D, Dimension]
outputCompositeTransform = CompositeTransformType.New()
outputCompositeTransform.AddTransform(movingInitialTransform)
outputCompositeTransform.AddTransform(registration.GetModifiableTransform())

resampler = itk.ResampleImageFilter.New(Input=movingImage,
        Transform=outputCompositeTransform,
        UseReferenceImage=True,
        ReferenceImage=fixedImage)
resampler.SetDefaultPixelValue(100)

OutputPixelType = itk.ctype('unsigned char')
OutputImageType = itk.Image[OutputPixelType, Dimension]

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

resampler.SetTransform(identityTransform)
writer.SetFileName(differenceImageBeforeFile)
writer.Update()