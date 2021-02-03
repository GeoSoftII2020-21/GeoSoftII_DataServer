#%%pytest

import os , sys, inspect, pytest, shutil, xarray as xr
import xarray  as xr
from Sentinel2_Data import *
from shutil import copyfile

'''direcrtory where testfiles will be downloaded'''
directory = "F:/Data_Sentinel/WorkDir/"


'''Parameter'''
aoi = 'POLYGON((7.52834379254901 52.01238155392252,7.71417925515199 52.01183230436206,7.705255583805303 51.9153349236737,7.521204845259327 51.90983021961716,7.52834379254901 52.01238155392252,7.52834379254901 52.01238155392252))'
collectionDate = ('20200601', '20200615')
clouds = (0, 30)
plName = 'Sentinel-2'
prLevel = 'Level-2A'
username = "geosoft2"
password = "Geosoft2"
resolution = 70
name = "datacube_2020-06-01_Merged_R100"

global nir
global ds_1
global ds_2



def test_downloadingData():
    downloadingData(aoi, collectionDate, plName, prLevel, clouds, username, password, directory)
    filePath1 = directory + "S2A_MSIL2A_20200613T103031_N0214_R108_T32UMC_20200613T111252.zip"
    filePath6 = directory + "S2B_MSIL2A_20200601T103629_N0214_R008_T32ULC_20200601T135554.zip"
    filePath7 = directory + "S2B_MSIL2A_20200601T103629_N0214_R008_T32UMC_20200601T135554.zip"
    assert  os.path.isfile(filePath1) == True and os.path.getsize(filePath1) == 1186851835
    assert  os.path.isfile(filePath6) == True and os.path.getsize(filePath6) == 1207179107
    assert  os.path.isfile(filePath7) == True and os.path.getsize(filePath7) == 1162389852

	             
def test_unzip1():
    unzip(directory)
    filePath1 = directory + "S2A_MSIL2A_20200613T103031_N0214_R108_T32UMC_20200613T111252.SAFE"
    filePath2 = directory + "S2B_MSIL2A_20200601T103629_N0214_R008_T32ULC_20200601T135554.SAFE"
    filePath3 = directory + "S2B_MSIL2A_20200601T103629_N0214_R008_T32UMC_20200601T135554.SAFE"
    assert  os.path.exists(filePath1) == True 
    assert  os.path.exists(filePath2) == True 
    assert  os.path.exists(filePath3) == True 
	

def test_unzip2():
    filePath1 = directory + "S2A_MSIL2A_20200613T103031_N0214_R108_T32UMC_20200613T111252.zip"
    filePath2 = directory + "S2B_MSIL2A_20200601T103629_N0214_R008_T32ULC_20200601T135554.zip"
    filePath3 = directory + "S2B_MSIL2A_20200601T103629_N0214_R008_T32UMC_20200601T135554.zip"
    assert os.path.exists(filePath1) == False
    assert os.path.exists(filePath2) == False
    assert os.path.exists(filePath3) == False
    
	
def test_del():
    with pytest.raises(NoPath):
        delete(directory + "hello.rtf")
	
def test_delete_ispath(capfd):
    d = open(directory + "testfile", "w")
    d.close()
    delete(directory+"testfile")
    out, err = capfd.readouterr()
    assert out == "File was deleted\n"

	    
def test_extractBands10():
    filename = "S2A_MSIL2A_20200613T103031_N0214_R108_T32UMC_20200613T111252.SAFE"
    lTwoA = os.listdir(os.path.join(directory, filename, "GRANULE"))
    bandName = os.listdir (os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R10m"))
    pathRed = os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R10m", str(bandName[3]))
    pathNIR = os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R10m", str(bandName[4]))
    bandPaths = [pathRed, pathNIR]
    
    assert extractBands(filename, 10, directory) == bandPaths;

	
def test_extractBands20():
    filename = "S2A_MSIL2A_20200613T103031_N0214_R108_T32UMC_20200613T111252.SAFE"
    lTwoA = os.listdir(os.path.join(directory, filename, "GRANULE"))
    bandName = os.listdir (os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R20m"))
    pathRed = os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R20m", str(bandName[3]))
    pathNIR = os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R20m", str(bandName[9]))
    bandPaths = [pathRed, pathNIR]
    
    assert extractBands(filename, 20, directory) == bandPaths;
    
	
def test_extractBands60():
    filename = "S2A_MSIL2A_20200613T103031_N0214_R108_T32UMC_20200613T111252.SAFE"
    lTwoA = os.listdir(os.path.join(directory, filename, "GRANULE"))
    bandName = os.listdir (os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R60m"))
    pathRed = os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R60m", str(bandName[4]))
    pathNIR = os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R60m", str(bandName[11]))
    bandPaths = [pathRed, pathNIR]
    
    assert extractBands(filename, 60, directory) == bandPaths;
  
	
def test_extractBands100():
    filename = "S2A_MSIL2A_20200613T103031_N0214_R108_T32UMC_20200613T111252.SAFE"
    lTwoA = os.listdir(os.path.join(directory, filename, "GRANULE"))
    bandName = os.listdir (os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R20m"))
    pathRed = os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R20m", str(bandName[3]))
    pathNIR = os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R20m", str(bandName[9]))
    bandPaths = [pathRed, pathNIR]
    
    assert extractBands(filename, 100, directory) == bandPaths;

	
def test_extractBands_wrongResolution():
    with pytest.raises(NoResolution):
        extractBands("S2B_MSIL2A_20200601T103629_N0214_R008_T32ULC_20200601T135554.SAFE", 70, directory)

	
def test_extractBands_wrongPath():
    with pytest.raises(NoPath):
          extractBands("S2B2_MSIL2A_20200601T103629_N0214_R008_T32ULC_20200601T135554.SAFE", 60, directory)   
	    
def test_getDate1():
    filename="S2A_MSIL2A_20200613T103031_N0214_R108_T32UMC_20200613T111252.SAFE"
    
    assert getDate(filename) =='2020-06-13'
	
def test_getDate2():
    filename="S2A_MSIL2A_20200613T103031_N0214_R108_T32UMC_20200613T111252.SAFE"
  
    assert isinstance(getDate(filename),str)
	 
def test_getTile():
    filename="S2A_MSIL2A_20200613T103031_N0214_R108_T32UMC_20200613T111252.SAFE"
    
    assert getTile(filename) == "T32UMC" 
	 
def test_getTile2():
    filename="S2A_MSIL2A_20200613T103031_N0214_R108_T32UMC_20200613T111252.SAFE"
    
    assert isinstance(getTile(filename),str)

	
def test_loadBand1():
    filename = "S2B_MSIL2A_20200601T103629_N0214_R008_T32ULC_20200601T135554.SAFE"
    with pytest.raises(NoResolution):
        bandPath = extractBands(os.path.join(directory, filename), resolution, directory)
        loadBand(bandPath, getDate(filename), getTile(filename), resolution, clouds, plName, prLevel, directory)
      
	
def test_loadBand2():
    filename = "S2B1_MSIL2A_20200601T103629_N0214_R008_T32ULC_20200601T135554.SAFE"
    with pytest.raises(NoPath):
        bandPath = extractBands(os.path.join(directory, filename), resolution, directory)
        loadBand(bandPath, getDate(filename), getTile(filename), resolution, clouds, plName, prLevel, directory) 
	
def test_buildCube1():
    with pytest.raises(NoResolution):
        buildCube(directory, 70, clouds, plName, prLevel)
	
def test_buildCube2():
    os.mkdir(directory + "onefile")
    d = open(directory + "onefile/testfile", "w")
    d.close()
    with pytest.raises(NoSafeFileError):
        buildCube(directory+"onefile", 60, clouds, plName, prLevel)
    shutil.rmtree(directory+"onefile")
	

def test_buildCube3():
    buildCube(directory, 100, clouds, plName, prLevel)
    assert  os.path.isfile(directory +"datacube_2020-06-01_T32UMC_R100.nc") == True 
    assert  os.path.isfile(directory +"datacube_2020-06-13_T32UMC_R100.nc") == True 
    assert  os.path.isfile(directory +"datacube_2020-06-01_T32ULC_R100.nc") == True 
              
	
def test_mergeSentinel1(capfd):
    os.mkdir(directory+"empty")
    with pytest.raises (FileNotFoundError):
        merge_Sentinel(directory+"empty", "Datacube_Sentinel")
    shutil.rmtree(directory+"empty")

	
def test_mergeSentinel2(capfd):
    os.mkdir(directory + "onefile")
    d = open(directory + "onefile/testfile", "w")
    d.close()
    with pytest.raises(TypeError):
        merge_Sentinel(directory + "onefile", "Datacube_Sentinel")
    shutil.rmtree(directory+"onefile")

	
def test_merge_coords_1():
    ds_2 = xr.open_dataset(os.path.join(directory,"datacube_2020-06-01_T32UMC_R100.nc"))
    ds_1 = xr.open_dataset(os.path.join(directory,"datacube_2020-06-01_T32ULC_R100.nc"))
    merge_coords(ds_1,ds_2,name,directory)
    assert os.path.exists(directory + name + ".nc")==True
	
def test_merge_coords_2():
    ds_2 = xr.open_dataset(os.path.join(directory,"datacube_2020-06-01_T32UMC_R100.nc"))
    ds_1 = xr.open_dataset(os.path.join(directory,"datacube_2020-06-01_T32ULC_R100.nc"))
    with pytest.raises(ValueError): 
        merge_coords(ds_2,ds_1,name,directory)

	
def test_safe_datacube1():
    test = xr.Dataset()
    safe_datacube(test,"test", directory)
    assert os.path.exists(directory + "test" + ".nc")==True
    delete(directory + "test" + ".nc")
	    
def test_safe_datacube2():
    with pytest.raises(AttributeError): 
        test = 0
        safe_datacube(test,"test", directory)
        assert os.path.exists(directory + "test" + ".nc")==True

	
def test_mergeSentinel1():
    os.mkdir(directory+"empty")
    with pytest.raises(FileNotFoundError):
        merge_Sentinel(directory+"empty", "Datacube_Sentinel")
    shutil.rmtree(directory+"empty")
	
def test_mergeSentinel2(capfd):
    os.mkdir(directory+"onefile/")
    d = open(directory +"onefile/testfile.nc", "w")
    d.close()
    merge_Sentinel(directory+"onefile/", "Datacube_Sentinel")
    out, err = capfd.readouterr()
    assert out == "Only one file in directory\n"
    shutil.rmtree(directory+"onefile")
    
# def test_mergeSentinel3():
#     parent_dir = os.path.dirname(directory)
#     shutil.copyfile(os.path.join(directory,"datacube_2020-06-13_T32UMC_R100.nc"), os.path.join(parent_dir,"/datacube_2020-06-13_T32UMC_R100.nc"))
#     ds_3 = xr.open_dataset(os.path.join(parent_dir,"/datacube_2020-06-13_T32UMC_R100.nc"))
#     nir = ds_3.nir
#     merge_Sentinel(directory, "datacube_merged")
#     nir_merge = xr.open_dataset(os.path.join(directory,"datacube_merged.nc")).nir.sel(time = slice("2020-06-02", "2020-06-14")).sel(lon = slice(nir.lon[0], nir.lon[1097]))
#     assert np.all((nir == nir_merge))
#     nir.close()
#     nir_merge.close()
#     ds_3.close()
#     delete(directory+ "datacube_merged.nc")
#     delete(os.path.join(parent_dir,"/datacube_2020-06-13_T32UMC_R100.nc"))


#last test works, if ran on a non C: divice, Error occures in Test, not in function
