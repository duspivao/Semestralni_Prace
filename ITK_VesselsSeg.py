import itk
sigma = 1
alpha = 5
alpha2 = 2
# Hessian3DToVesselnessMeasureImageFilter


PixelType = itk.ctype('unsigned short')
Dimension = 3
ImageType = itk.Image[PixelType, Dimension]

readerType = itk.ImageFileReader[ImageType]
reader = readerType.New()

reader.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Reg_8_GaborliversSmall.nrrd')
image = reader.GetOutput()

# Smoothing
SmoothFilterType =  itk.SmoothingRecursiveGaussianImageFilter[ImageType, ImageType]
smoothingFilter = SmoothFilterType.New()
smoothingFilter.SetInput(image)
smoothingFilter.SetSigmaArray([3,2,2])
smoothedImg = smoothingFilter.GetOutput()


# Because this method finds bright structures we have to invert intesity
InvertIntesityType = itk.InvertIntensityImageFilter[itk.Image[itk.ctype('unsigned short'), 3],itk.Image[itk.ctype('unsigned short'), 3]]
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
writer.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/HessianFilter_XXXX.nrrd')
writer.Update()

