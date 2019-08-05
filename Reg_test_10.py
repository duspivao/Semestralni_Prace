import SimpleITK as sitk
import numpy as np
import itk
from scipy import ndimage
import time
import scipy.signal as sps



"""Porovnani sitk convoluce a scipzy pro gabioy"""
reader = sitk.ImageFileReader()
reader.SetFileName('C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/CT.nrrd')
imageR = reader.Execute()

outputDirPath = 'C:/Users/duso/PycharmProjects/Semestralni_Prace/Registration/Frangis/RegistrationTests/test/Reg_10_Gabor'

writer = sitk.ImageFileWriter()
#
# rotation = itk.Versor
# angleInRadians = 60 * np.pi / 180.0



gab = sitk.GaborImageSource()



print gab.GetFrequency ()
print gab.GetMean ()
print gab.GetOrigin ()
print gab.GetSigma ()
print gab.GetSpacing ()
print gab.GetDirection()
# rotation2 = sitk.VersorTransform((0,0,1), np.pi)
# gab.SetDirection(rotation2.GetMatrix())
# gab.SetFrequency(1)
# gab.SetMean ()
# gab.SetOrigin ()
# gab.SetSigma ()
# gab.SetSpacing ()


gab.SetSize([64,64,64])
writer.SetFileName(outputDirPath+'a.nrrd')
writer.Execute( gab.Execute() )
#
#
# # gab.SetFrequency(0.2)
rotation2 = sitk.VersorTransform((0.3,.3,0.3), np.pi)
gab.SetDirection(rotation2.GetMatrix())
writer.SetFileName(outputDirPath+'b.nrrd')
writer.Execute( gab.Execute() )
#print gab.GetFrequency ()
print gab.GetMean ()
print gab.GetOrigin ()
print gab.GetSigma ()
print gab.GetSpacing ()
print gab.GetDirection()
#
# # gab.SetFrequency(.8)
gab2 = sitk.GaborImageSource()
rotation3 = sitk.VersorTransform((0.1,0.1,0.1), np.pi*0.5)
gab2.SetDirection(rotation3.GetMatrix())
writer.SetFileName(outputDirPath+'c.nrrd')
writer.Execute( gab2.Execute() )

print gab2.GetFrequency ()
print gab2.GetMean ()
print gab2.GetOrigin ()
print gab2.GetSigma ()
print gab2.GetSpacing ()
print gab2.GetDirection()

g = gab2.Execute()
sT = time.time()
iArr = sitk.GetArrayFromImage(imageR)
gArr = sitk.GetArrayFromImage(g)
reConv = sps.convolve(iArr,gArr)
writer.SetFileName(outputDirPath+'_sps.nrrd')
writer.Execute( sitk.GetImageFromArray(reConv) )
# np.convolve(iArr, gArr)
# ndimage.convolve(iArr, gArr, mode='reflect')
sP = time.time()
print sP-sT

sT = time.time()
reConvFFT = sps.fftconvolve(iArr,gArr)
writer.SetFileName(outputDirPath+'_spsFFT.nrrd')
writer.Execute( sitk.GetImageFromArray(reConvFFT) )
sP = time.time()
print sP-sT

sT = time.time()
conv = sitk.ConvolutionImageFilter()
convRes = conv.Execute(imageR,g)
writer.SetFileName(outputDirPath+'_conv.nrrd')
writer.Execute( convRes )
sP = time.time()
print sP-sT


sT = time.time()
convFFT = sitk.FFTConvolutionImageFilter()
convFFTRes = convFFT.Execute(imageR,g)
writer.SetFileName(outputDirPath+'_convFFT.nrrd')
writer.Execute( convFFTRes )
sP = time.time()
print sP-sT


