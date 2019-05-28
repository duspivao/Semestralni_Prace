#!/usr/bin/env python

from __future__ import print_function

import SimpleITK as sitk
import os
import datetime
import itk
import sys


########SETUP PARAMETER AND INPUTS FOR REGISTRATION#####
# Input direction for fixed image
from SimpleITK import ImageRegistrationMethod

label = 'DEMONS_TEST'
inputFixDirName = 'C:/ZCU/3Dircadb1/3Dircadb1.1/'+label

# Input dircection for moving image
label = 'DEMONS_TEST'
inputMovDirName = 'C:/ZCU/3Dircadb1/3Dircadb1.7/'+label


# Output direction
# Subfolder with timestamp will be created
outputDirPath = 'C:/ZCU/Results/'
st = datetime.datetime.now().strftime("%d_%m_%y_%H%M")
outputDirPath = outputDirPath+st
if not os.path.exists(outputDirPath):
    os.makedirs(outputDirPath)

# Parameters of registration
numberOfBins = 10
samplingPercentage = 0.20

# Function for read DICOM Images from DIR, and save in nrrd image file
# This function also save image to 3D in format nrrd for next transform
def readDICOMImage(dir, outPutDir, identifier):
    PixelType = itk.ctype('signed short')
    Dimension = 3

    ImageType = itk.Image[PixelType, Dimension]


    namesGenerator = itk.GDCMSeriesFileNames.New()
    namesGenerator.SetUseSeriesDetails(False)
    namesGenerator.SetGlobalWarningDisplay(False)
    namesGenerator.SetDirectory(dir)

    seriesUID = namesGenerator.GetSeriesUIDs()

    if len(seriesUID) < 1:
        print('ERROR: No DICOMS in folder' + dir)
        sys.exit(1)
    if len(seriesUID) > 1:
        print('ERROR: In folder are more series')
        sys.exit(1)
    print('DICOMs red OK from: ' + dir)



    # SHOULD BE just one
    for uid in seriesUID:
        seriesIdentifier = uid

        print('Reading: ' + seriesIdentifier)
        fileNames = namesGenerator.GetFileNames(seriesIdentifier)

        reader = itk.ImageSeriesReader[ImageType].New()
        dicomIO = itk.GDCMImageIO.New()
        reader.SetImageIO(dicomIO)
        reader.SetFileNames(fileNames)

        outFileName = 'DIC_' + identifier + '.nrrd'
        writer = itk.ImageFileWriter[ImageType].New()
        writer.SetFileName(outPutDir+'/'+outFileName)
        writer.UseCompressionOn()
        writer.SetInput(reader.GetOutput())

        print('Writing: ' + outPutDir+'/'+outFileName)
        writer.Update()

        return sitk.ReadImage(outPutDir+'/'+outFileName, sitk.sitkFloat32)


fixImg = readDICOMImage(inputFixDirName,outputDirPath,'FIX')
movImg = readDICOMImage(inputMovDirName,outputDirPath,'MOC')

fixed = fixImg
moving = movImg

def smooth_and_resample(image, shrink_factor, smoothing_sigma):
    """
    Args:
        image: The image we want to resample.
        shrink_factor: A number greater than one, such that the new image's size is original_size/shrink_factor.
        smoothing_sigma: Sigma for Gaussian smoothing, this is in physical (image spacing) units, not pixels.
    Return:
        Image which is a result of smoothing the input and then resampling it using the given sigma and shrink factor.
    """
    smoothed_image = sitk.SmoothingRecursiveGaussian(image, smoothing_sigma)

    original_spacing = image.GetSpacing()
    original_size = image.GetSize()
    new_size = [int(sz / float(shrink_factor) + 0.5) for sz in original_size]
    new_spacing = [((original_sz - 1) * original_spc) / (new_sz - 1)
                   for original_sz, original_spc, new_sz in zip(original_size, original_spacing, new_size)]
    return sitk.Resample(smoothed_image, new_size, sitk.Transform(),
                         sitk.sitkLinear, image.GetOrigin(),
                         new_spacing, image.GetDirection(), 0.0,
                         image.GetPixelID())


def multiscale_demons(registration_algorithm,
                      fixed_image, moving_image, initial_transform=None,
                      shrink_factors=None, smoothing_sigmas=None):
    """
    Run the given registration algorithm in a multiscale fashion. The original scale should not be given as input as the
    original images are implicitly incorporated as the base of the pyramid.
    Args:
        registration_algorithm: Any registration algorithm that has an Execute(fixed_image, moving_image, displacement_field_image)
                                method.
        fixed_image: Resulting transformation maps points from this image's spatial domain to the moving image spatial domain.
        moving_image: Resulting transformation maps points from the fixed_image's spatial domain to this image's spatial domain.
        initial_transform: Any SimpleITK transform, used to initialize the displacement field.
        shrink_factors: Shrink factors relative to the original image's size.
        smoothing_sigmas: Amount of smoothing which is done prior to resmapling the image using the given shrink factor. These
                          are in physical (image spacing) units.
    Returns:
        SimpleITK.DisplacementFieldTransform
    """
    # Create image pyramid.
    fixed_images = [fixed_image]
    moving_images = [moving_image]
    if shrink_factors:
        for shrink_factor, smoothing_sigma in reversed(list(zip(shrink_factors, smoothing_sigmas))):
            fixed_images.append(smooth_and_resample(fixed_images[0], shrink_factor, smoothing_sigma))
            moving_images.append(smooth_and_resample(moving_images[0], shrink_factor, smoothing_sigma))

    # Create initial displacement field at lowest resolution.
    # Currently, the pixel type is required to be sitkVectorFloat64 because of a constraint imposed by the Demons filters.
    if initial_transform:
        initial_displacement_field = sitk.TransformToDisplacementField(initial_transform,
                                                                       sitk.sitkVectorFloat64,
                                                                       fixed_images[-1].GetSize(),
                                                                       fixed_images[-1].GetOrigin(),
                                                                       fixed_images[-1].GetSpacing(),
                                                                       fixed_images[-1].GetDirection())
    else:
        initial_displacement_field = sitk.Image(fixed_images[-1].GetWidth(),
                                                fixed_images[-1].GetHeight(),
                                                fixed_images[-1].GetDepth(),
                                                sitk.sitkVectorFloat64)
        initial_displacement_field.CopyInformation(fixed_images[-1])

    # Run the registration.
    initial_displacement_field = registration_algorithm.Execute(fixed_images[-1],
                                                                moving_images[-1],
                                                                initial_displacement_field)
    # Start at the top of the pyramid and work our way down.
    for f_image, m_image in reversed(list(zip(fixed_images[0:-1], moving_images[0:-1]))):
        initial_displacement_field = sitk.Resample(initial_displacement_field, f_image)
        initial_displacement_field = registration_algorithm.Execute(f_image, m_image, initial_displacement_field)
    return sitk.DisplacementFieldTransform(initial_displacement_field)

# Define a simple callback which allows us to monitor the Demons filter's progress.
def iteration_callback(filter):
    print('\r{0}: {1:.2f}'.format(filter.GetElapsedIterations(), filter.GetMetric()), end='')



# Select a Demons filter and configure it.
demons_filter =  sitk.FastSymmetricForcesDemonsRegistrationFilter()
demons_filter.SetNumberOfIterations(20)
# Regularization (update field - viscous, total field - elastic).
demons_filter.SetSmoothDisplacementField(False)
demons_filter.SetStandardDeviations(2.0)

# Add our simple callback to the registration filter.
demons_filter.AddCommand(sitk.sitkIterationEvent, lambda: iteration_callback(demons_filter))

# Run the registration.
tx = multiscale_demons(registration_algorithm=demons_filter,
                       fixed_image = fixed,
                       moving_image = moving,
                       # shrink_factors = [1,1,1],
                       # smoothing_sigmas = [1,1,1])
                       )
# # Compare the initial and final TREs.
# initial_errors_mean, initial_errors_std, _, initial_errors_max, initial_errors = ru.registration_errors(sitk.Euler3DTransform(), points[fixed_image_index], points[moving_image_index])
# final_errors_mean, final_errors_std, _, final_errors_max, final_errors = ru.registration_errors(tx, points[fixed_image_index], points[moving_image_index])
#
# plt.hist(initial_errors, bins=20, alpha=0.5, label='before registration', color='blue')
# plt.hist(final_errors, bins=20, alpha=0.5, label='after registration', color='green')
# plt.legend()
# plt.title('TRE histogram');
# print('\nInitial alignment errors in millimeters, mean(std): {:.2f}({:.2f}), max: {:.2f}'.format(initial_errors_mean, initial_errors_std, initial_errors_max))
# print('Final alignment errors in millimeters, mean(std): {:.2f}({:.2f}), max: {:.2f}'.format(final_errors_mean, final_errors_std, final_errors_max))
resampler = sitk.ResampleImageFilter()
resampler.SetReferenceImage(fixed);
resampler.SetInterpolator(sitk.sitkLinear)
resampler.SetDefaultPixelValue(100)
resampler.SetTransform(tx)

out = resampler.Execute(moving)
simg1 = sitk.Cast(sitk.RescaleIntensity(fixed), sitk.sitkUInt8)
simg2 = sitk.Cast(sitk.RescaleIntensity(out), sitk.sitkUInt8)
cimg = sitk.Compose(simg1, simg2, simg1//2.+simg2//2.)
sitk.Show( cimg, "ImageRegistration4 Composition" )
print('===END==')