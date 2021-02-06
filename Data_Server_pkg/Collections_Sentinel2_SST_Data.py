#@author Adrian Spork https://github.com/A-Spork
#@author Tatjana Melina Walter https://github.com/jana2308walter
#@author Maximilian Busch https://github.com/mabu1994
#@author digilog11 https://github.com/digilog11

import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
import getpass
import numpy as np
import xarray as xr
import rasterio as rio
import os
import pandas as pd
import shutil
import stat
from rasterio.enums import Resampling
from datetime import datetime
from zipfile import ZipFile
from ftplib import FTP 

from Sentinel2_Data import *
from datacube_sst import *


'''Dask Cluster'''
from dask.distributed import Client, LocalCluster
'''Python 3.9.1 Workaround'''
# # import multiprocessing.popen_spawn_posix#nonwindows#
# import multiprocessing.popen_spawn_win32#windows#
# from distributed import Client#
# Client()#
'''Server'''
#cluster = LocalCluster()
#client = Client(cluster)
#client


def create_collection(collection, params):
    '''
    Executes the SST - or the Sentinel - Dataprocess
    
    Parameters:
        collection (str): The collection which is needed, SST or Sentinel2
        params ([]): The params for executing the main - method
   '''
        
    if collection == "SST":
        yearBegin = params[0]
        yearEnd = params[1]
        global directorySST 
        directorySST = params[2]
        global name
        name = params[3]
        generate_sst_datacube(yearBegin, yearEnd, directorySST, name)

        
    
    elif collection == "Sentinel2":
        resolution = 100
        global directorySentinel
        directorySentinel = params[0]
        collectionDate = params[1]
        clouds = params[2]
        username = params[3]
        password = params[4]
        nameSentinel = params[5]
        aoi = 'POLYGON((7.52834379254901 52.01238155392252,7.71417925515199 52.01183230436206,7.705255583805303 51.9153349236737,7.521204845259327 51.90983021961716,7.52834379254901 52.01238155392252,7.52834379254901 52.01238155392252))'
        mainSentinel(resolution, directorySentinel, collectionDate, aoi, clouds, username, password, nameSentinel)
    
    else:
        raise NameError("No Collection named like this")




def load_collection(collection, start, end): 
    '''
    Executes the SST - or the Sentinel - Dataprocess
    Parameters:
        collection (str): The collection which is needed, SST or Sentinel2
        start (datetime64[ns]): startdate of the requested Data
        end (datetime64[ns]): enddate of the requested Data
    Returns:
        datacube (xArray.Dataset): requested datacube
    '''

    if collection == "SST":
        if os.path.exists(directorySST+ nameSST+".nc"):
            SST = xr.open_dataset(directorySST+ nameSST+".nc")
            timeframe = []
            timeframe.append(start)
            timeframe.append(end)
            SST_sel = get_time_sub_datacube(SST, timeframe)
            return SST_sel
        else:
            raise FileNotFoundError("Directory empty")
    elif collection == "Sentinel2":
        if os.path.exists(directorySentinel + nameSentinel + ".nc"):
            Sentinel = xr.open_dataset(directorySentinel + nameSentinel + ".nc")
            timeframe = []
            timeframe.append(start)
            timeframe.append(end)
            Sentinel_sel = get_time_sub_datacube(Sentinel, timeframe)
            return Sentinel_sel
        else:
            raise FileNotFoundError("Directory empty")
    else:
        raise NameError("No Collection named like this")




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
directorySST = "C:/Users/adria/Desktop/SSTData/"
global nameSST 
nameSST = 'SST_datacube'
SST_start = 2013
SST_end = 2018
paramsSST = [SST_start, SST_end, directorySST, nameSST]

'''Setup'''
# create_collection("Sentinel2", paramsSentinel)
# create_collection("SST", paramsSST)




'''
User Example
'''
# Sentinel = load_collection("Sentinel2",'2020-06-01', '2020-06-13')
# print(Sentinel)
# SST = load_collection("SST",'2013-06-01', '2018-06-03')
# print(SST)

