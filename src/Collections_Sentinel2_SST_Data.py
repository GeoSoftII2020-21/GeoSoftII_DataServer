


#@author Adrian Spork https://github.com/A-Spork
#@author Tatjana Melina Walter https://github.com/jana2308walter
#@author Maximilian Busch https://github.com/mabu1994
#@author digilog11 https://github.com/digilog11





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
import sys





'''Dask Cluster'''
from dask.distributed import Client, LocalCluster
'''Python 3.9.1 Workaround'''
# # import multiprocessing.popen_spawn_posix#nonwindows#
# import multiprocessing.popen_spawn_win32#windows#
# from distributed import Client#
# Client()#
'''Server'''
cluster = None
client = None



# Sentinel 2




class NoPath(Exception):
    def init(self, message):
        self.message = message
    pass

class NoResolution(Exception):
    def init(self, message):
        self.message = message
    pass

class NoSafeFileError(Exception):
    def init(self,message):
        self.message = message
    pass 

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





def downloadingData(aoi, collectionDate, plName, prLevel, clouds, username, password, directory):
    '''
    Downloads the Sentinel2 - Data with the given parameters

    Parameters:
        aoi (str): The type and the coordinates of the area of interest
        collectionDate datetime 64[ns]): The date of the data
        plName (str): The name of the platform
        prLevel (str): The name of the process
        clouds (tuple of ints): Min and max of cloudcoverpercentage
        username (str): The username of the Copernicus SciHub
        password (str): The password of the Copernicus SciHub
        directory (str): Pathlike string to the directory
    '''
    
    api = SentinelAPI(username, password, 'https://scihub.copernicus.eu/dhus')
    
    '''Choosing the data with bounding box (footprint), date, platformname, processinglevel and cloudcoverpercentage'''
    products = api.query(aoi, date = collectionDate, platformname = plName, processinglevel = prLevel, cloudcoverpercentage = clouds)

    '''Downloads the choosen files from Scihub'''
    if len(products)==0:
        raise Exception("No data for this params")
    print("Start downloading " + str(len(products)) + " product(s)", file=sys.stderr)
    api.download_all(products, directory, max_attempts = 10, checksum = True)
    print("All necassary downloads done", file=sys.stderr)





def unzipping(filename, directory):
    '''
    Unzips the file with the given filename
    Parameter:
        filename(str): Name of the .zip file
        directory (str): Pathlike string to the directory
    '''
    with ZipFile(os.path.join(directory, filename), 'r') as zipObj:
        zipObj.extractall(directory)





def unzip(directory):
    '''
    Unzips and deletes the .zip in the given directory

    Parameters:
        directory (str): Pathlike string to the directory
    '''

    for filename in os.listdir(directory):
        if filename.endswith(".zip"):
            if(filename[39:41]!="32"):
                print("CRS not supported! Only EPSG:32632 supported", file=sys.stderr)
                delete(os.path.join(directory,filename))
            else:
                unzipping(filename, directory)
                delete(os.path.join(directory, filename))
                continue
        else:
            continue





def extractBands(filename, resolution, directory):
    '''
    Extracts bandpaths from the given .SAFE file
    Parameters:
        filename (str): Sentinel .SAFE file
        resolution (int): The resolution the datacube should have
        directory (str): Pathlike string to the directory
    Returns:
        bandPaths (str[]): An array of the paths for the red and nir band
    '''

    try:
        lTwoA = os.listdir(os.path.join(directory, filename, "GRANULE"))
        if resolution == 10:
            bandName = os.listdir (os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R10m"))
            pathRed = os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R10m", str(bandName[3]))
            pathNIR = os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R10m", str(bandName[4]))
            bandPaths = [pathRed, pathNIR]

        elif resolution == 20:
            bandName = os.listdir (os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R20m"))
            pathRed = os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R20m", str(bandName[3]))
            pathNIR = os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R20m", str(bandName[9]))
            bandPaths = [pathRed, pathNIR]

        elif resolution == 60:
            bandName = os.listdir (os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R60m"))
            pathRed = os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R60m", str(bandName[4]))
            pathNIR = os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R60m", str(bandName[11]))
            bandPaths = [pathRed, pathNIR]

        elif resolution == 100:
            bandName = os.listdir (os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R20m"))
            pathRed = os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R20m", str(bandName[3]))
            pathNIR = os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R20m", str(bandName[9]))
            bandPaths = [pathRed, pathNIR]

        else:
               raise NoResolution("Invalid Resolution, try 10, 20, 60 or 100")
    except FileNotFoundError:
        raise NoPath("No file in this path")
    return bandPaths





def loadBand (bandpath, date, tile, resolution, clouds, plName, prLevel, directory):
    '''
    Opens and reads the red and nir band, saves them as NetCDF file
    Parameters:
        bandPaths (str[]): Array with the paths to the red and nir band
        date (datetime 64[ns]): The collection date ("2020-12-31")
        tile (str): Bounding box of coordinates defined by Sentinel
        resolution (int): The resolution of the dataset
        clouds (tuple of ints): Min and max of cloudcoverpercentage
        plName (str): The name of the platform
        prLevel (str): The level of the process
        directory (str): Pathlike string to the directory
    Returns:
        dataset (xArray dataset): The result dataset as xArray dataset
    '''
    
    
    b4 = rio.open(bandpath[0])
    b8 = rio.open(bandpath[1])
    red = b4.read()
    nir = b8.read()

    if resolution == 10:
        res = 1830 * 3 * 2
    elif resolution == 20:
        res = 1830 * 3
    elif resolution == 60:
        res = 1830
    elif resolution == 100:
        res = 1098
    else:
        raise NoResolution("Invalid Resolution, try 10, 20, 60 or 100")

    j = res - 1
    i = 0
    lat = [0] * res
    lon = [0] * res
    while j >= 0:
        lon[i] = b4.bounds.left + i * resolution
        lat[i] = b4.bounds.bottom + j * resolution
        i = i + 1
        j = j - 1

    time = pd.date_range(date, periods = 1)

    if resolution == 100:
        upscale_factor = (1/5)
        nir = b8.read(
                out_shape = (
                    b8.count,
                    int(b8.height * upscale_factor),
                    int(b8.width * upscale_factor)
                ),
                resampling = Resampling.bilinear
        )
        transform = b8.transform * b8.transform.scale(
            (b8.width / nir.shape[-1]),
            (b8.height / nir.shape[-2])
        )
        red = b4.read(
            out_shape = (
                b4.count,
                int(b4.height * upscale_factor),
                int(b4.width * upscale_factor)
            ),
            resampling = Resampling.bilinear
        )

        transform = b4.transform * b4.transform.scale(
            (b4.width / red.shape[-1]),
            (b4.height / red.shape[-2])
        )

    dataset = xr.Dataset(
        {
            "red": (["time","lat", "lon"], red),
            "nir": (["time","lat", "lon"], nir)
        },
        coords = dict(
            time = time,
            lat = (["lat"], lat),
            lon = (["lon"], lon),
        ),
        attrs = dict(
            platform = plName,
            processingLevel = prLevel,
            source = "https://scihub.copernicus.eu/dhus",
            resolution = str(resolution) + " x " + str(resolution) + " m"
        ),
    )

    dataset.to_netcdf(directory + "datacube_" + str(date) + "_" + str(tile) + "_R" + str(resolution) + ".nc", 'w', format = 'NETCDF4')
    b4.close()
    b8.close()
    return dataset





def getDate(filename):
    '''
    Extracts the Date out of the Sentinelfilename
    Parameters:
        filename (str): Name of the file
    Returns:
        (str): Date of the File ("2020-12-31")
    '''

    return filename[11:15] + "-" + filename[15:17] + "-" + filename[17:19]





def getTile(filename):
    '''
    Extracts the UTM-tile of the Sentinelfilename
    Parameters:
        filename (str): Name of the file
    Returns:
        (str): UTM-tile of the File ("31UMC")
    '''
    return filename[38:44]





def on_rm_error(func, path, exc_info):
    '''
    Unlinks a read-only file
    '''

    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)





def buildCube(directory, resolution, clouds, plName, prLevel):
    '''
    Builds a datacube in the given directory with coords, time as dimensions and the bands as datavariables
    Parameters:
        directory (str): Pathlike string to the directory
        resolution (int): The resolution of the dataset
        clouds (tuple of ints): Min and max of cloudcoverpercentage
        plName (str): The name of the platform
        prLevel (str): The level of the process
    '''
    
    i = 0
    for filename in os.listdir(directory):
        if filename.endswith(".SAFE"):
            i = i + 1
    if i == 0:
        raise NoSafeFileError ("In this directory is no SAFE file to build a cube")
    for filename in os.listdir(directory):
        if filename.endswith(".SAFE"):
            bandPath = extractBands(os.path.join(directory, filename), resolution, directory)
            band = loadBand(bandPath, getDate(filename), getTile(filename), resolution, clouds, plName, prLevel, directory)
            shutil.rmtree(os.path.join(directory, filename), onerror = on_rm_error)
            continue
        else:
            continue





def merge_Sentinel(directory, nameSentinel):
    '''
    Merges datacubes by coordinates and time

    Parameters:
        directory (str): Pathlike string where Data is stored
        nameSentinel (str): Filename for the datacube
    '''
    start = datetime.now()
    files = os.listdir(directory)
    for nc in files:
        if not nc.endswith(".nc"):
            raise TypeError("Wrong file in directory")
    if len(files) == 0:
        raise FileNotFoundError("Directory empty")
    elif len(files) == 1:
        print("Only one file in directory", file=sys.stderr)
        os.rename(directory + (os.listdir(directory)[0]), directory + "merged_cube.nc")
        return
    else:
        print('Start merging', file=sys.stderr)
        for file1 in files:
            for file2 in files:
                file1Date = file1[9:19]
                file1Tile = file1[20:26]
                file1Res = file1[27:31]
                file2Date = file2[9:19]
                file2Tile = file2[20:26]
                file2Res = file2[27:31]
                if file1[21:23] == "31":
                    delete(os.path.join(directory,file1))
                elif file2[21:23] == "31":
                    delete(os.path.join(directory,file2))
                elif file1Date == file2Date and file1Tile == file2Tile and file1Res == file2Res:
                    continue
                elif file1Date == file2Date and file1Tile == "T32ULC" and file2Tile == "T32UMC" and file1Res == file2Res:
                    fileLeft = xr.open_dataset(os.path.join(directory, file1))
                    fileRight = xr.open_dataset(os.path.join(directory, file2))
                    merge_coords(fileLeft, fileRight, file1[0:20] + "Merged" + file1[26:31], directory)
                    fileLeft.close()
                    fileRight.close()
                    delete(os.path.join(directory, file1))
                    delete(os.path.join(directory, file2))
    ds_merge = []
    files = []
    for f in os.listdir(directory):
        x = xr.open_dataset(os.path.join(directory, f))
        ds_merge.append(x)
        files.append(os.path.join(directory, f))
    datacube = xr.open_mfdataset(files, parallel=True, chunks={"time": "auto"})
    '''save datacube'''
    print("Start saving", file=sys.stderr)
    datacube.to_netcdf(directory + nameSentinel + ".nc", compute = True)
    print("Done saving", file=sys.stderr)
    datacube.close()
    for f in ds_merge:
        f.close()
    for f in files:
        deleteNetcdf(f)
    end = datetime.now()
    diff = end - start
    print('All cubes merged for ' + str(diff.seconds) + 's', file=sys.stderr)





def timeframe(ds, start, end):
    '''
    Slices Datacube down to given timeframe
    Parameters:
        ds (xArray Dataset): Sourcedataset
        start (str): Start of the timeframe eg '2018-07-13'
        end (str): End of the timeframe eg '2018-08-23'
    Returns:
        ds_selected (xArray Dataset): Dataset sliced to timeframe
    '''

    if start > end:
        print("start and end of the timeframe are not compatible!", file=sys.stderr)
    else:
        ds_selected = ds.sel(time = slice(start, end))
        return ds_selected





def safe_datacube(ds, name, directory):
    '''
    Saves the Datacube as NetCDF (.nc)
    Parameters:
        ds (xArray Dataset): Sourcedataset
        name (str): Name eg '2017', '2015_2019'
        directory (str): Pathlike string to the directory
    '''

    print("Start saving", file=sys.stderr)
    start = datetime.now()
    ds.to_netcdf(directory + name + ".nc")
    diff = datetime.now() - start
    print("Done saving after "+ str(diff.seconds) + 's', file=sys.stderr)





def merge_coords(ds_left, ds_right, name, directory):
    '''
    Merges two datasets by coordinates

    Parameters:
        ds_left (xArray dataset): Dataset to be merged
        ds_right (xArray dataset): Dataset to be merged
        name (str): Name of the new dataset
        directory (str): Pathlike string to the directory
    '''

    ds_selected = ds_left.sel(lon = slice(ds_left.lon[0], ds_right.lon[0]))
    ds_merge = [ds_selected, ds_right]
    merged = xr.combine_by_coords(ds_merge)
    safe_datacube(merged, name, directory)




# def slice_lat(ds, lat_left, lat_right):
#     '''
#     Slices a given dataset to given latitude bounds
#     Parameters:
#         ds (xArray Dataset): Dataset to be sliced
#         lat_left (float): Left latitude bound
#         lat_right (float): Right latitude bound
#     Returns:
#         ds (xArray Dataset): Sliced dataset
#     '''

#     ds_selected = ds.sel(lat = slice(lat_left, lat_right))
#     return ds_selected





# def slice_lon(ds, lon_left, lon_right):
#     '''
#     Slices a given dataset to given longitude bounds
#     Parameters:
#         ds (xArray Dataset): Dataset to be sliced
#         lon_left (float): Left longitude bound
#         lon_right (float): Right longitude bound
#     Returns:
#         ds (xArray Dataset): Sliced dataset
#     '''

#     ds_selected = ds.sel(lon = slice(lon_left, lon_right))
#     return ds_selected





# def slice_coords(ds, lon_left, lon_right, lat_left, lat_right):
#     '''
#     Slices a dataset to a given slice
#     Parameters:
#         ds (xArray Dataset): Dataset to be sliced
#         lon_left (float): Left bound for longitude
#         lon_right (float): Right bound for longitude
#         lat_left (float): Left bound for latitude
#         lat_right (float): Right bound for latitude
#     Returns:
#         ds (xArray Dataset): Sliced dataset
#     '''

#     ds_selected = slice_lon(ds, lon_left, lon_right)
#     return slice_lat(ds_selected, lat_left, lat_right)





def delete(path):
    '''
    Deletes the file/directory with the given path
    Parameters:
        path (str): Path to the file/directory
    '''
    try: 
        os.remove(path)
        print("File was deleted", file=sys.stderr)
    except FileNotFoundError:
        raise NoPath ("No file in this path")





def mainSentinel(resolution, directory, collectionDate, aoi, clouds, username, password, nameSentinel):
    '''
    Downloads, unzips, collects and merges Sentinel2 Satelliteimages to a single netCDF4 datacube

    Parameters:
        resolution (int): Resolution of the satelite image
        directory (str): Pathlike string to the workdirectory
        collectionDate (tuple of datetime 64[ns]): Start and end of the timeframe
        aoi (POLYGON): Area of interest
        clouds (tuple of ints): Min and max of cloudcoverpercentage
        username (str): Uername for the Copernicus Open Acess Hub
        password (str): Password for the Copernicus Open Acess Hub
        nameSentinel (str): Filename for the datacube
    '''
    if collectionDate[0]==collectionDate[1]:
        raise Exception("Start and end of collection can not be identical")
    plName = 'Sentinel-2'
    prLevel = 'Level-2A'
    downloadingData (aoi, collectionDate, plName, prLevel, clouds, username, password, directory)
    unzip(directory)
    buildCube(directory, resolution, clouds, plName, prLevel)
    merge_Sentinel(directory, nameSentinel)


# SST



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
            print("Downloading..." + file, file=sys.stderr)
            ftp.retrbinary("RETR " + file, open(directory + file, 'wb').write)
            ftp.close()
            end = datetime.now()
            diff = end - start
            print('File downloaded in ' + str(diff.seconds) + 's', file=sys.stderr)
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
            print("File deleted: " + path, file=sys.stderr)
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
#     datacube = xr.open_mfdataset(files) '''non dask'''
    datacube = xr.open_mfdataset(files, parallel = True, chunks = {"time": "auto"})
    '''save datacube'''
    print("Start saving", file=sys.stderr)
    datacube.to_netcdf(directory + name + ".nc", compute = True)
    print("Done saving", file=sys.stderr)
    datacube.close()
    '''delete yearly datasets'''
    for f in ds_merge:
        f.close()
    for f in files:
        deleteNetcdf(f)





def get_time_sub_datacube (data, timeframe):
    '''
    Generates a subset along the time dimension of the sst datacube and returns it

    Parameters:
        data (xArray.Dataset): Dataset to be sliced
        timeframe ([str]): Tuple with values for start and end dates, e.g. ['1981-10-01','1981-11-01']
        
    Returns:
        ds (bytes): sub dataset
    '''
    
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
    
    data_sub = data.sel(time = slice(timeframe[0], timeframe[1]))
    data.close()
    return data_sub


# Wrapper


def  load(collection,start, end):
    if collection == "SST":
        cube = xr.open_dataset(os.path.join(directorySST, nameSST))
        cube = timeframe(cube, start, end) 
        return cube

    if collection == "Sentinel2":
        cube = xr.open_dataset(os.path.join(directorySentinel, nameSentinel))
        cube = timeframe(cube, start, end) 
        return cube





def create_collection(collection, params):
    '''
    Executes the SST - or the Sentinel - Dataprocess
    
    Parameters:
        collection (str): The collection which is needed, SST or Sentinel2
        params ([]): The params for executing the main - method
   '''
    if client == None:
        main()
        
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
    if client == None:
        main()
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


def main():
    global client
    global cluster
    if client==None:
        cluster = LocalCluster()
        client = Client(cluster)
        client


'''Params Sentinel'''
global directorySentinel 
directorySentinel = "/SENTINEL/"
global nameSentinel 
nameSentinel = "Sentinel_datacube"
timeframeSentinel = (os.environ.get("Sentinel_Start"), os.environ.get("Sentinel_End"))
cloud = (0, 30)
username = os.environ.get("Username")
password = os.environ.get("Password")
paramsSentinel = [directorySentinel, timeframeSentinel, cloud, username, password, nameSentinel]

'''Params SST'''
global directorySST 
directorySST = "/SST/"
global nameSST 
nameSST = 'SST_datacube'
SST_start = int(os.environ.get("SST_Start"))
SST_end = int(os.environ.get("SST_End"))
paramsSST = [SST_start, SST_end, directorySST, nameSST]

'''Setup'''





def init():
    if os.environ.get("load_sst") == "True":
        create_collection("SST", paramsSST)
    if os.environ.get("load_sentinel") == "True":
        create_collection("Sentinel2", paramsSentinel)


'''
User Example
'''
# Sentinel = load_collection("Sentinel2",'2020-06-01', '2020-06-13')
# print(Sentinel)
# SST = load_collection("SST",'2013-06-01', '2018-06-03')
# print(SST)

