import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from Collections_Sentinel2_SST_Data import *
from datacube_sst import *
from Sentinel2_Data import *
import pytest

'''Params Sentinel'''
global directorySentinel 
directorySentinel = "C:/Users/adria/Desktop/SentinelData/"
global nameSentinel 
nameSentinel = "Sentinel_datacube"
timeframeSentinel = ('2020-06-01T00:00:00Z', '2020-06-15T23:59:59Z')
cloud = (0, 30)
username = ""
password = ""
paramsSentinel = [directorySentinel, timeframeSentinel, cloud, username, password, nameSentinel]

'''Params SST'''
global directorySST 
directorySST = "/Users/master/Documents/Tests_wrapper"
global nameSST 
nameSST = 'SST_datacube'
SST_start = 2013
SST_end = 2018
paramsSST = [SST_start, SST_end, directorySST, nameSST]

def test_createSST1():
    with pytest.raises(NameError):
        create_collection("test", paramsSST)
        
def test_createSST2():
    paramsSST[2] = "/Users/master/Documents/Tests_wrapper1"
    with pytest.raises(DirectoryNotFoundError):
        create_collection("SST", paramsSST)
    paramsSST[2] = directorySST

def test_createSST3():
    paramsSST[3] = "sst?1981-82"
    with pytest.raises(FilenameError):
        create_collection("SST", paramsSST)
    paramsSST[3] = "SST_datacube"
    
def test_createSST4():
    paramsSST[3] = "sst<19882"
    with pytest.raises(FilenameError):
        create_collection("SST", paramsSST)
    paramsSST[3] = "SST_datacube"
    
def test_createSST5():
    paramsSST[3] = "Com9"
    with pytest.raises(FilenameError):
        create_collection("SST", paramsSST)
    paramsSST[3] = "SST_datacube"

def test_createSST6():
    paramsSST[3] = ""
    with pytest.raises(FilenameError):
        create_collection("SST", paramsSST)
    paramsSST[3] = "SST_datacube"
    
def test_createSST7():
    paramsSST[0] = 2019
    paramsSST[1] = 2018
    with pytest.raises(TimeframeError):
        create_collection("SST", paramsSST)
    paramsSST[0] = 2013
    paramsSST[1] = 2018 
    
def test_createSST8():
    paramsSST[0] = 2019
    paramsSST[1] = 2019
    with pytest.raises(TimeframeError):
        create_collection("SST", paramsSST)
    paramsSST[0] = 2013
    paramsSST[1] = 2018 
    
def test_createSentinel1():
    with pytest.raises(NameError):
        create_collection("test", paramsSentinel)

def test_load_collection1():
    with pytest.raises(NameError):
        load_collection("test",'2013-06-01', '2018-06-03')

def test_load_collection2():
    with pytest.raises(FileNotFoundError):
        load_collection("SST",'2017-09-03', '2019-08-02')
        
def test_load_collection3():
    with pytest.raises(FileNotFoundError):
        load_collection("Sentinel2", '2015-09-04', '2017-08-02')