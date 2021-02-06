import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from ftplib import FTP
from datetime import datetime
import xarray  as xr
import numpy as np
import os.path
import pytest

from datacube_sst import FileNotFoundError, DirectoryNotFoundError, TimeframeError, NotNetCDFError, FilenameError
from datacube_sst import download_file, deleteNetcdf, generate_sst_datacube

'''directory where testfiles will be downloaded'''
fileDirectory = "./"

'''tests function download_file'''
      
def test_downloadNoDataForYear():
    with pytest.raises(FileNotFoundError):
        download_file(1980, fileDirectory)
        
def test_downloadNoDataForYear_2():
    with pytest.raises(FileNotFoundError):
        download_file(2022, fileDirectory)
    
def test_downloadFile_1():
    download_file(1981, fileDirectory)
    filePath = fileDirectory + "sst.day.mean.1981.nc"
    if os.path.isfile(filePath) and os.path.getsize(filePath) == 160580480: assert True

def test_downloadOverwritesFile():
    download_file(1981, fileDirectory)
    filePath = fileDirectory + "sst.day.mean.1981.nc"
    count = 0
    for file in os.listdir(fileDirectory):
        if file == "sst.day.mean.1981.nc":
            count = count + 1
    if count == 1: assert True

'''tests function deleteNetcdf'''

def test_notNetcdf():
    filePath = fileDirectory + "sst.day.mean.1999.js"
    with pytest.raises(NotNetCDFError):
        deleteNetcdf(filePath)
        
def test_noFileToDelete():
    filePath = fileDirectory + "sst.day.mean.1979.nc"
    with pytest.raises(FileNotFoundError):
        deleteNetcdf(filePath)
        
def test_deleteFile():
    filePath = fileDirectory + "sst.day.mean.1981.nc"
    deleteNetcdf(filePath)
    if os.path.exists(filePath): assert False
  
'''tests function generate_sst_datacube'''

def test_invalidFilename():
    with pytest.raises(FilenameError):
        generate_sst_datacube(1981, 1982, fileDirectory, "sst?1981-82")
        
def test_invalidFilename_2():
    with pytest.raises(FilenameError):
        generate_sst_datacube(1981, 1982, fileDirectory, "sst<19882")
        
def test_invalidFilename_3():
    with pytest.raises(FilenameError):
        generate_sst_datacube(1981, 1982, fileDirectory, "Com9")
        
def test_invalidFilename_4():
    with pytest.raises(FilenameError):
        generate_sst_datacube(1981, 1982, fileDirectory, "")
        
def test_invalidDirectory():
    with pytest.raises(DirectoryNotFoundError):
        generate_sst_datacube(1981, 1982, "../nonExistentDirectory/noFileEver/", "sst1981-1982")

def test_invalidTimeframe():
    with pytest.raises(TimeframeError):
        generate_sst_datacube(2019,2018, fileDirectory, "sst20182019")
        
def test_invalidTimeframe_2():
    with pytest.raises(TimeframeError):
        generate_sst_datacube(2019,2019, fileDirectory, "sst2019")

def test_generate_sst_datacube():
    filePath = fileDirectory + "sst1981-1982.nc"
    generate_sst_datacube(1981, 1982, fileDirectory, "sst1981-1982")
    if os.path.isfile(filePath): assert True
    start = "1981-09-01"
    end = "1982-12-31"
    x = xr.open_dataset(filePath)
    if np.datetime_as_string(x["time"][0], unit='D') == start and np.datetime_as_string(x["time"][-1], unit='D') == end:
        assert True
