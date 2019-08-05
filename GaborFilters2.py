import SimpleITK as sitk


outputDirPath = 'C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Filters_'

reader = sitk.ImageFileReader()
writer = sitk.ImageFileWriter()

reader.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Reg_8_GaborliversSmall.nrrd')
imageR = reader.Execute()

caster = sitk.CastImageFilter()
caster.SetOutputPixelType(sitk.sitkUInt8)

gaborFilter = sitk.GaborImageSource()
gaborFilter.SetSpacing([1,1,1])
gaborFilter.SetSigma([50.,75.,75])
gaborFilter.SetSize([64,64,64])
gaborFilter.SetFrequency(0.001)

for theta in range(0,180,45):
    transform = sitk.Euler3DTransform()
    transform.SetTranslation([0,0,0])
    transform.SetRotation(theta,theta,theta)
    transform.SetCenter([0,0,0])
    resampler = sitk.ResampleImageFilter()
    resampler.SetTransform(transform)
    resampler.SetInterpolator(sitk.sitkGaussian )

    convolution = sitk.ConvolutionImageFilter()
    result = convolution.Execute(imageR, resampler.Execute(gaborFilter.Execute()))