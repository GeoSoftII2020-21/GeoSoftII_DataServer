'''packages'''

from ftplib import FTP
from datetime import datetime
import xarray  as xr
import os.path
import numpy as np


'''dask cluster'''

from dask.distributed import Client, LocalCluster
cluster = None
client = None
firstRun = True


'''exceptions'''

class FileNotFoundError(Exception):
  def __init__(self, message):
    self.message = message
    
class DirectoryNotFoundError(Exception):
  def __init__(self, message):
    self.message = message

class TimeframeError(Exception):
  def __init__(self, message):
    self.message = message
    
class NotNetCDFError(Exception):
  def __init__(self, message):
    self.message = message
    
class FilenameError(Exception):
  def __init__(self, message):
    self.message = message
    
class TimeframeLengthError(Exception):
  def __init__(self, message):
    self.message = message

class TimeframeValueError(Exception):
  def __init__(self, message):
    self.message = message
    
class ParameterTypeError(Exception):
  def __init__(self, message):
    self.message = message


'''functions'''

def download_file(year, directory):
    '''
    Downloads the sst data file for the given year

    Parameters:
        year (int): year of the sst data
        directory (str): path of future file
    '''
    
    start = datetime.now()
    ftp = FTP('ftp.cdc.noaa.gov')
    ftp.login()
    ftp.cwd('/Projects/Datasets/noaa.oisst.v2.highres/')

    files = ftp.nlst()
    counter = 0

    for file in files:
        if file == 'sst.day.mean.' + str(year) + '.nc':
            print("Downloading..." + file)
            ftp.retrbinary("RETR " + file, open(directory + file, 'wb').write)
            ftp.close()
            end = datetime.now()
            diff = end - start
            print('File downloaded in ' + str(diff.seconds) + 's')
            break
        else: counter += 1

        if counter == len(files):
            raise FileNotFoundError('No matching file found')

def deleteNetcdf(path):
    '''
    Deletes the NetCDF-file with the given path

    Parameters:
        path (str): Path to the file
    '''
    if path[len(path)-3:len(path)] == ".nc":
        if os.path.exists(path):
            os.remove(path)
            print("File deleted: " + path)
        else:
            raise FileNotFoundError('No matching file found')
    else:
        raise NotNetCDFError('Path does not belong to a netCDF-file')

def generate_sst_datacube (yearBegin, yearEnd, directory, name):
    '''
    The main function to download the sst-data, merge it and safe the datacube

    Parameters:
        yearBegin (int): First year to download
        yearEnd (int): Last year to download
        directory (str): Path to the directory
        name (str): Name of new File
    '''
    
    '''check parameters'''
    if yearBegin > yearEnd or yearBegin == yearEnd:
        raise TimeframeError("Ending year must be bigger than beginning year")
    '''should catch most invalid filenames'''
    invalidCharacters = ['<', '>', ':',  '/',  '|', '*', '?', '"', '\\']
    invalidNames = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
    if len(name) < 1: raise FilenameError("Name is not a permitted filename")
    for x in invalidCharacters:
        if x in name: raise FilenameError("Name is not a permitted filename")
    for x in invalidNames:
        if x.lower() == name.lower(): raise FilenameError("Name is not a permitted filename")
    if (os.path.exists(directory) == False): raise DirectoryNotFoundError('No matching directory found')
    '''set up dask cluster, open "http://127.0.0.1:1234/status" in browser to view dashboard'''
    global cluster
    global client
    global firstRun
    if firstRun:
        cluster = LocalCluster(dashboard_address=':1234')
        client = Client(cluster)
        firstRun = False
    '''download sst data for the wanted years'''
    i = yearBegin
    files = []
    ds_merge = []
    while i <= yearEnd:
        download_file(i, directory)
        files.append(os.path.join(directory,"sst.day.mean." + str(i) + ".nc"))
        i = i + 1
    '''merge sst data'''
    for f in files:
        x = xr.open_dataset(os.path.join(directory, f))
        ds_merge.append(x)
    datacube = xr.open_mfdataset(files, parallel=True, chunks={"time": "auto"})
    '''save datacube'''
    print("Start saving")
    datacube.to_netcdf(directory + name + ".nc", compute = True)
    print("Done saving")
    datacube.close()
    '''delete yearly datasets'''
    for f in ds_merge:
        f.close()
    for f in files:
        deleteNetcdf(f)

def get_time_sub_datacube (path, timeframe):
    '''
    Generates a subset along the time dimension of the sst datacube and returns it

    Parameters:
        path (str): Path of the sst-datacube
        timeframe ([str]): Tuple with values for start and end dates, e.g. ['1981-10-01','1981-11-01']
        
    Returns:
        ds (bytes): sub dataset
    '''
    data = xr.open_dataset(path)
    
    if len(timeframe) != 2:
        raise TimeframeLengthError("Parameter timeframe is an array with two values: [start date, end date]. Please specify an array with exactly two values.")

    try:
        x = isinstance(np.datetime64(timeframe[0]),np.datetime64)
        x = isinstance(np.datetime64(timeframe[1]),np.datetime64)

    except ValueError:
        raise ParameterTypeError("Values of parameter timeframe must be strings of the format 'year-month-day'. For example '1981-01-01'. Please specify values that follow this.")

    if (type(timeframe[0]) != str or type(timeframe[1]) != str
            or len(timeframe[0]) != 10 or len(timeframe[1]) != 10):
        raise ParameterTypeError("Values of parameter timeframe must be strings of the format 'year-month-day'. For example '1981-01-01'. Please specify values that follow this.")
    elif (timeframe[0] > timeframe[1]
            or np.datetime_as_string(data["time"][0], unit='D') > timeframe[0]
            or np.datetime_as_string(data["time"][0], unit='D') > timeframe[1]
            or timeframe[1] > np.datetime_as_string(data["time"][-1], unit='D')
            or timeframe[0] > np.datetime_as_string(data["time"][-1], unit='D')):
        raise TimeframeValueError("Timeframe values are out of bounds. Please check the range of the dataset.")
    
    data = data.sel(time=slice(timeframe[0], timeframe[1]))
    data_sub = data.to_netcdf(compute=True, encoding = {"sst": {'missing_value': np.nan}})
    return data_sub