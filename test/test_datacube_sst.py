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

from datacube_sst import *

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
      
'''tests function get_time_sub_datacube'''

os.getcwd()
ds = xr.open_dataset("./GeoSoftII_DataServer/test/sst.day.mean.1984-03-4days.nc")

'''test that result was sliced correctly'''   

def test_get_time_sub_datacube():
    start = '1984-03-01'
    end = '1984-03-03'
    sub = get_time_sub_datacube(ds, [start, end])
    if start != np.datetime_as_string(sub["time"][0], unit='D') or end != np.datetime_as_string(sub["time"][-1], unit='D'):
        assert False
    
'''test that parameter timeframe has right length'''

def test_TimeframeTooLong():
    with pytest.raises(TimeframeLengthError): 
        get_time_sub_datacube(ds, ['1984-03-01', '1984-03-01', '1984-03-01'])
            
def test_TimeframeTooShort():
    with pytest.raises(TimeframeLengthError): 
        get_time_sub_datacube(ds, ['1984-03-01'])
            
'''test that dates within parameter timeframe are inside bounds'''

def test_TimeframeOutsideBottomRangeFirstP():
    with pytest.raises(TimeframeValueError): 
        get_time_sub_datacube(ds, ['1984-02-01','1984-03-01'])
            
def test_TimeframeOutsideTopRangeFirstP():
    with pytest.raises(TimeframeValueError): 
        get_time_sub_datacube(ds, ['1984-04-01','1984-03-01'])
            
def test_TimeframeOutsideBottomRangeSecondP():
    with pytest.raises(TimeframeValueError): 
        get_time_sub_datacube(ds, ['1984-03-01','1984-02-01'])
            
def test_TimeframeOutsideTopRangeSecondP():
    with pytest.raises(TimeframeValueError): 
        get_time_sub_datacube(ds, ['1984-03-01','1984-04-01'])
            
def test_StartDateBiggerThanEndDate():
    with pytest.raises(TimeframeValueError): 
        get_time_sub_datacube(ds, ['1984-03-04','1984-03-01'])
            
'''test that dates within parameter timeframe are real dates'''
                          
def test_InvalidDateFirstP():
    with pytest.raises(ParameterTypeError):
        get_time_sub_datacube(ds, ['1984-03-00','1984-03-02'])
            
def test_InvalidDateSecondP():
    with pytest.raises(ParameterTypeError):
        get_time_sub_datacube(ds, ['1984-03-01','1984-03-40'])
            
'''test that dates within parameter timeframe are valid datetimes'''
    
def test_InvalidDatetimeSyntaxFirstP_1():
    with pytest.raises(ParameterTypeError):
        get_time_sub_datacube(ds, ['1984.03.01','1984-03-02'])
            
def test_InvalidDatetimeSyntaxSecondP_1():
    with pytest.raises(ParameterTypeError):
        get_time_sub_datacube(ds, ['1984-03-01','1984.03.02'])
            
def test_InvalidDatetimeSyntaxFirstP_2():
    with pytest.raises(ParameterTypeError):
        get_time_sub_datacube(ds, ['1984-0301','1984-03-02'])
            
def test_InvalidDatetimeSyntaxSecondP_2():
    with pytest.raises(ParameterTypeError):
        get_time_sub_datacube(ds, ['1984-03-01','1984-0302'])
            
def test_InvalidDatetimeSyntaxFirstP_3():
    with pytest.raises(ParameterTypeError):
        get_time_sub_datacube(ds, ['01-03-1984','1984-03-02'])
            
def test_InvalidDatetimeSyntaxSecondP_3():
    with pytest.raises(ParameterTypeError):
        get_time_sub_datacube(ds, ['1984-03-01','02-03-1984'])

def test_InvalidDatetimeSyntaxFirstP_4():
    with pytest.raises(ParameterTypeError):
        get_time_sub_datacube(ds, ['1984-03','02-03-1984'])
        
def test_InvalidDatetimeSyntaxSecondP_4():
    with pytest.raises(ParameterTypeError):
        get_time_sub_datacube(ds, ['1984-03-01','1984-03'])
