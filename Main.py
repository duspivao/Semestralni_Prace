import DataPreparation
import VesselSegmentation
import types


test0 = 'test/Reg_8_GaborliversSmall.nrrd'
test = 'test/4-150cc OMNIPAQUE-36663'
# testImage = DataPreparation.readDICOMSerieToImage(folder=test, saveImageToNrrd=False)
testImage = DataPreparation.readNrrdToImage(folder=test0,saveImageToNrrd=False)
DataPreparation.saveImageAsNrrd(VesselSegmentation.ThresholdingVesselSegmentation(testImage),'test')

print '====END==='