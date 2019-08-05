import numpy as np
import time
import itk

start = time.time()
# PixelType = itk.ctype('unsigned short')

# ImageType = itk.Image[PixelType, Dimension]


Dimension = 3
RealType = itk.ctype('float')
RealImageType = itk.Image[RealType, Dimension]
LabelImageType = itk.Image[itk.ctype('unsigned short'), Dimension]

readerType = itk.ImageFileReader[RealImageType]
reader = readerType.New()

reader.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Reg_8_GaborliversSmall.nrrd')
reader.Update()

#
image = reader.GetOutput()
#
origin = np.zeros(3)
spacing = np.ones(3)
size = np.ones(3,np.int)*64
mean = np.zeros(3)
sigma = np.zeros(3)

for i in range(len(mean)):
    mean[i] =  origin[i] + 0.5 * spacing[i] * (1.0*size[i])-1.0
sigma[0] = 50.0
sigma[1] = 75.0
sigma[2] = 75.0

GaborImageType = itk.GaborImageSource[RealImageType]
gaborFilter = GaborImageType.New()
gaborFilter.SetSpacing(spacing)
gaborFilter.SetOrigin(origin)
gaborFilter.SetSize(size)
gaborFilter.SetFrequency( 0.001 )
gaborFilter.SetCalculateImaginaryPart( True )
gaborFilter.SetSigma(sigma)
gaborFilter.SetMean(mean)
#
#
GaussianInterpolatorType = itk.LinearInterpolateImageFunction[RealImageType,itk.ctype('double')]
gaussInterpolator = GaussianInterpolatorType.New()
gaussInterpolator.SetInputImage(reader.GetOutput())
#
# sigma = np.zeros(Dimension)
# for i in range(len(sigma)):
#     sigma[i] = 0.8
#
# alpha = 1.0
#
# gaussInterpolator.SetParameters(sigma, alpha)
#
for theta in range(0, 180, 45):
    TransformType = itk.CenteredEuler3DTransform[itk.ctype('double')]
    transform = TransformType.New()
    transform.SetRotation(0.0,0.0,theta)
    transform.SetTranslation([0,0,0])
    # center = np.zeros(3,np.float)
    # for c in range(len(center)):
    #     center[c] = gaborFilter.GetOutput().GetOrigin()[c]+gaborFilter.GetOutput().GetSpacing()[c]
    #
    # transform.SetCenter(center)

    ResamplerType = itk.ResampleImageFilter[RealImageType, RealImageType]
    resampler = ResamplerType.New()
    resampler.SetTransform( transform )
    resampler.SetInterpolator( gaussInterpolator )
    gabor = gaborFilter.GetOutput()
    resampler.SetInput( gabor )
    # resampler.SetOutputSpacing( gabor.GetSpacing() )
    # resampler.SetOrigin (resampler.GetOutput().GetOrigin())
    # resampler.SetSize()

    # CasterType = itk.CastImageFilter[image,itk.Image[itk.ctype('float'), Dimension]]
    # caster = CasterType.New()
    # caster.SetInput(image)

    ConvolutionFilterType = itk.ConvolutionImageFilter[itk.Image[itk.ctype('float'), Dimension], itk.Image[itk.ctype('float'), Dimension]]
    conv = ConvolutionFilterType.New()
    conv.SetInput( image )

    # caster2 = CasterType.New()
    # caster2.SetInput(resampler.GetOutput())
    conv.SetKernelImage( resampler.GetOutput() )

    conv.Update()














#
#
# outputDirPath = 'C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Reg_8_Gabor'
#
#
#
# reader = sitk.ImageFileReader()
# writer = sitk.ImageFileWriter()
#
# reader.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Reg_8_GaborliversSmall.nrrd')
# imageR = reader.Execute()
#
# caster = sitk.CastImageFilter()
# caster.SetOutputPixelType(sitk.sitkUInt8)
# image = caster.Execute(imageR)
#
# size = 64
# filter = sitk.GaborImageSource()
# filter.SetOutputPixelType(sitk.sitkUInt8)
#
# filters = []
# for i in range(0,5,1):
#     filter.SetSize([size]*3)
#     filter.SetSigma([size*.2*(1+i)]*3)
#     filter.SetMean([size*(0.5+i/10)]*3)
#     filter.SetFrequency(.1+(i/10))
#     filter.SetOutputPixelType(sitk.sitkUInt8)
#     g = filter.Execute()
#     filters.append(g)
#     writer.SetFileName(outputDirPath + 'f'+str(i)+'.nrrd')
#     writer.Execute(g)
# print 'all fitleres prepared'
#
# ide = 1
# for kern in filters:
#     print 'convolving no '+str(ide)
#     print kern.GetDimension()
#     print image.GetDimension()
#
#     conv = sitk.ConvolutionImageFilter()
#     conv.NormalizeOn()
#     res = conv.Execute(image, kern)
#     writer.SetFileName(outputDirPath + 'g'+str(ide)+'.nrrd')
#     writer.Execute(res)
#     ide += 1
# #
#
# # writer.SetFileName(outputDirPath+'g1.nrrd')
# stop = time.time()
#
# print stop-start