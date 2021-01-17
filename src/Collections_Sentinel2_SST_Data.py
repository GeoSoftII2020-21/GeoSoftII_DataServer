# @author Adrian Spork
# @author Tatjana Melina Walter

from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
import geopandas as gpd
import getpass
import xarray as xr
import rasterio as rio
import os
import pandas as pd
import numpy as np
import shutil
from time import sleep
import stat
import io
from rasterio.enums import Resampling
import netCDF4 as nc
from datetime import datetime
from zipfile import ZipFile
import matplotlib.pyplot as plt
import urllib.request as request
from contextlib import closing
from ftplib import FTP


##############################Sentinel2##################################################

def downloadingData(aoi, collectionDate, plName, prLevel, clouds, username, password, directory):
    '''
    Downloads the Sentinel2 - Data with the given parameters

    Parameters:
        aoi (str): The type and the coordinates of the area of interest
        collectionDate (datetime 64[ns]): The date of the data
        plName (str): The name of the platform
        prLevel (str): The name of the process
        clouds (tuple of ints): Min and max of cloudcoverpercentage
        username (str): The username of the Copernicus SciHub
        password (str): The password of the Copernicus SciHub
        directory (str): Pathlike string to the directory
    '''

    api = SentinelAPI(username, password, 'https://scihub.copernicus.eu/dhus')

    '''Choosing the data with bounding box (footprint), date, platformname, processinglevel and cloudcoverpercentage'''
    products = api.query(aoi, date=collectionDate, platformname=plName, processinglevel=prLevel,
                         cloudcoverpercentage=clouds)

    '''Filters the products and sorts by cloudcoverpercentage'''
    products_gdf = api.to_geodataframe(products)
    products_gdf_sorted = products_gdf.sort_values(['cloudcoverpercentage'], ascending=[True])

    '''Downloads the choosen files from Scihub'''
    products_gdf_sorted.to_csv(os.path.join(directory, 'w'))
    api.download_all(products, directory, max_attempts=10, checksum=True)


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
            if (filename[39:41] != "32"):
                print("CRS not supported! Only EPSG:32632 supported")  # do not throw an exception here
                delete(os.path.join(directory, filename))
            else:
                unzipping(filename, directory)
                delete(os.path.join(directory, filename))
                continue
        else:
            continue


def delete(path):
    '''
    Deletes the file/directory with the given path

    Parameters:
        path (str): Path to the file/directory
    '''

    if os.path.exists(path):
        os.remove(path)
        print("File deleted: " + path)
    else:
        print("The file does not exist")


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

    lTwoA = os.listdir(os.path.join(directory, filename, "GRANULE"))

    if resolution == 10:
        bandName = os.listdir(os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R10m"))
        pathRed = os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R10m", str(bandName[3]))
        pathNIR = os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R10m", str(bandName[4]))
        bandPaths = [pathRed, pathNIR]

    elif resolution == 20:
        bandName = os.listdir(os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R20m"))
        pathRed = os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R20m", str(bandName[3]))
        pathNIR = os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R20m", str(bandName[9]))
        bandPaths = [pathRed, pathNIR]

    elif resolution == 60:
        bandName = os.listdir(os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R60m"))
        pathRed = os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R60m", str(bandName[4]))
        pathNIR = os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R60m", str(bandName[11]))
        bandPaths = [pathRed, pathNIR]

    elif resolution == 100:
        bandName = os.listdir(os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R20m"))
        pathRed = os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R20m", str(bandName[3]))
        pathNIR = os.path.join(directory, filename, "GRANULE", str(lTwoA[0]), "IMG_DATA", "R20m", str(bandName[9]))
        bandPaths = [pathRed, pathNIR]

    else:
        print("No such resolution")
        return -1

    return bandPaths


def loadBand(bandpath, date, tile, resolution, clouds, plName, prLevel, directory):
    '''
    Opens and reads the red and nir band, saves them as NetCDF file

    Parameters:
        bandpath (str[]): Array with the paths to the red and nir band
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
        print("No such resolution")
        return -1

    j = res - 1
    i = 0
    lat = [0] * res
    lon = [0] * res
    while j >= 0:
        lon[i] = b4.bounds.left + i * resolution
        lat[i] = b4.bounds.bottom + j * resolution
        i = i + 1
        j = j - 1

    time = pd.date_range(date, periods=1)

    if resolution == 100:
        upscale_factor = (1 / 5)
        nir = b8.read(
            out_shape=(
                b8.count,
                int(b8.height * upscale_factor),
                int(b8.width * upscale_factor)
            ),
            resampling=Resampling.bilinear
        )
        #        transform = b8.transform * b8.transform.scale(
        #            (b8.width / nir.shape[-1]),
        #            (b8.height / nir.shape[-2])
        #        )
        red = b4.read(
            out_shape=(
                b4.count,
                int(b4.height * upscale_factor),
                int(b4.width * upscale_factor)
            ),
            resampling=Resampling.bilinear
        )

    #       transform = b4.transform * b4.transform.scale(
    #           (b4.width / red.shape[-1]),
    #           (b4.height / red.shape[-2])
    #       )

    dataset = xr.Dataset(
        {
            "red": (["time", "lat", "lon"], red),
            "nir": (["time", "lat", "lon"], nir)
        },
        coords=dict(
            time=time,
            lat=(["lat"], lat),
            lon=(["lon"], lon),
        ),
        attrs=dict(
            platform=plName,
            processingLevel=prLevel,
            cloudcover=clouds,
            source="https://scihub.copernicus.eu/dhus",
            resolution=str(resolution) + " x " + str(resolution) + " m"
        ),
    )

    dataset.to_netcdf(directory + "datacube_" + str(date) + "_" + str(tile) + "_R" + str(resolution) + ".nc", 'w',
                      format='NETCDF4')
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

    for filename in os.listdir(directory):
        if filename.endswith(".SAFE"):
            bandPath = extractBands(os.path.join(directory, filename), resolution, directory)
            band = loadBand(bandPath, getDate(filename), getTile(filename), resolution, clouds, plName, prLevel,
                            directory)
            shutil.rmtree(os.path.join(directory, filename), onerror=on_rm_error)
            continue
        else:
            continue


def merge_Sentinel(directory):
    '''
    Merges datacubes by coordinates and time

    Parameters:
        directory (str): Pathlike string where Data is stored
    '''

    start = datetime.now()
    count1 = 0
    files = os.listdir(directory)

    if len(files) == 0:
        print("Directory empty")
        return
    elif len(files) == 1:
        print("Only one file in directory")
        return
    else:
        print('Start merging')
        for file1 in files:
            if count1 == len(files):
                return
            for file2 in files:
                count2 = 0
                if file1.endswith(".nc") and file2.endswith(".nc"):
                    file1Date = file1[9:19]
                    file1Tile = file1[20:26]
                    file1Res = file1[27:31]
                    file2Date = file2[9:19]
                    file2Tile = file2[20:26]
                    file2Res = file2[27:31]
                    if file1[21:23] == "31":
                        delete(os.path.join(directory, file1))
                    elif file2[21:23] == "31":
                        delete(os.path.join(directory, file2))
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
                        continue
                else:
                    raise TypeError("Wrong file in directory")

        files = os.listdir(directory)
        while len(os.listdir(directory)) > 1:
            files = os.listdir(directory)
            if files[0].endswith(".nc") and files[1].endswith(".nc"):
                file1 = xr.open_dataset(os.path.join(directory, files[0]))
                file2 = xr.open_dataset(os.path.join(directory, files[1]))
                merge_time(file1, file2, files[0][0:31], directory)
                file1.close()
                file2.close()
                delete(os.path.join(directory, files[1]))
                continue
            else:
                print("Error: Wrong file in directory")
                raise TypeError("Wrong file in directory")

    end = datetime.now()
    diff = end - start
    print('All cubes merged for ' + str(diff.seconds) + 's')
    return


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
        print("start and end of the timeframe are not compatible!")
    else:
        ds_selected = ds.sel(time=slice(start, end))
        return ds_selected


def safe_datacube(ds, name, directory):
    '''
    Saves the Datacube as NetCDF (.nc)

    Parameters:
        ds (xArray Dataset): Sourcedataset
        name (str): Name eg '2017', '2015_2019'
        directory (str): Pathlike string to the directory
    '''

    print("Start saving")
    start = datetime.now()
    if type(name) != str:
        name = str(name)
    ds.to_netcdf(directory + name + ".nc")
    diff = datetime.now() - start
    print("Done saving after " + str(diff.seconds) + 's')


def merge_coords(ds_left, ds_right, name, directory):
    '''
    Merges two datasets by coordinates

    Parameters:
        ds_left (xArray dataset): Dataset to be merged
        ds_right (xArray dataset): Dataset to be merged
        name (str): Name of the new dataset
        directory (str): Pathlike string to the directory
    '''

    ds_selected = slice_lon(ds_left, ds_left.lon[0], ds_right.lon[0])
    ds_merge = [ds_selected, ds_right]
    merged = xr.combine_by_coords(ds_merge)
    safe_datacube(merged, name, directory)


def merge_time(ds1, ds2, name, directory):
    '''
    Merges two datasets by time

    Parameters:
        ds1 (xArray dataset): Dataset to be merged
        ds2 (xArray dataset): Dataset to be merged
        name (str): Name of the new dataset
        directory (str): Pathlike string to the directory
    '''

    res = xr.combine_by_coords([ds1, ds2])
    ds1.close()
    ds2.close()
    safe_datacube(res, name, directory)


def slice_lat(ds, lat_left, lat_right):
    '''
    Slices a given dataset to given latitude bounds

    Parameters:
        ds (xArray Dataset): Dataset to be sliced
        lat_left (float): Left latitude bound
        lat_right (float): Right latitude bound

    Returns:
        ds (xArray Dataset): Sliced dataset
    '''

    ds_selected = ds.sel(lat=slice(lat_left, lat_right))
    return ds_selected


def slice_lon(ds, lon_left, lon_right):
    '''
    Slices a given dataset to given longitude bounds

    Parameters:
        ds (xArray Dataset): Dataset to be sliced
        lon_left (float): Left longitude bound
        lon_right (float): Right longitude bound

    Returns:
        ds (xArray Dataset): Sliced dataset
    '''

    ds_selected = ds.sel(lon=slice(lon_left, lon_right))
    return ds_selected


def slice_coords(ds, lon_left, lon_right, lat_left, lat_right):
    '''
    Slices a dataset to a given slice

    Parameters:
        ds (xArray Dataset): Dataset to be sliced
        lon_left (float): Left bound for longitude
        lon_right (float): Right bound for longitude
        lat_left (float): Left bound for latitude
        lat_right (float): Right bound for latitude

    Returns:
        ds (xArray Dataset): Sliced dataset
    '''

    ds_selected = slice_lon(ds, lon_left, lon_right)
    return slice_lat(ds_selected, lat_left, lat_right)


def mainSentinel(resolution, directory, collectionDate, aoi, clouds, username, password):
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
    '''

    plName = 'Sentinel-2'
    prLevel = 'Level-2A'
    downloadingData(aoi, collectionDate, plName, prLevel, clouds, username, password, directory)
    delete(os.path.join(directory, 'w'))
    unzip(directory)
    buildCube(directory, resolution, clouds, plName, prLevel)
    merge_Sentinel(directory)


# #################################SST####################################################

def download_file(year, directorySST):
    '''
    Downloads the sst data file for the given year

    Parameters:
        year (int): The year the sst is needed
        directorySST (str): Pathlike string to the directory
   '''

    start = datetime.now()
    ftp = FTP('ftp.cdc.noaa.gov')
    ftp.login()
    ftp.cwd('/Projects/Datasets/noaa.oisst.v2.highres/')

    files = ftp.nlst()
    counter = 0

    for file in files:
        if file == 'sst.day.mean.' + str(year) + '.nc':
            print("Downloading... " + file)
            ftp.retrbinary("RETR " + file, open(directorySST + file, 'wb').write)
            ftp.close()
            end = datetime.now()
            diff = end - start
            print('File downloaded ' + str(diff.seconds) + 's')
        else:
            counter += 1

        if counter == len(files):
            print('No matching dataset found for this year')


def merge_datacubes(ds_merge):
    '''
    Merges datacubes by coordinates

    Parameters:
        ds_merge (xArray Dataset[]): Array of datasets to be merged

    Returns:
        ds1 (xArray Dataset): A single datacube with all merged datacubes
    '''

    start = datetime.now()
    if len(ds_merge) == 0:
        print("Error: No datacubes to merge")
        return
    if len(ds_merge) == 1:
        return ds_merge[0]
    else:
        print('Start merging')
        ds1 = ds_merge[0]
        count = 1
        while count < len(ds_merge):
            start1 = datetime.now()
            ds1 = xr.combine_by_coords([ds1, ds_merge[count]], combine_attrs="override")
            count += 1
            diff = datetime.now() - start1
            print("Succesfully merged cube nr " + str(count) + " to the base cube in " + str(diff.seconds) + 's')
        diff = datetime.now() - start
        print('All cubes merged for ' + str(diff.seconds) + 's')
        return ds1


def safe_datacubeSST(ds, name, directorySST):
    '''
    Saves the Datacube as NetCDF (.nc)

    Parameters:
        ds (xArray Dataset): Sourcedataset
        name (str): Name or timeframe for saving eg '2017', '2015_2019'
        directorySST (str): Pathlike string to the directory
    '''

    print("Start saving")
    start = datetime.now()
    if type(name) != str:
        name = str(name)
    ds.to_netcdf(directorySST + "sst.day.mean." + name + ".nc")
    diff = datetime.now() - start
    print("Done saving after " + str(diff.seconds) + 's')


def mainSST(yearBegin, yearEnd, directorySST, name):
    '''
    The main function to download, merge and safe the datacubes

    Parameters:
        yearBegin (int): First year to download
        yearEnd (int): Last year to download
        directorySST (str): Pathlike string to the directory
        name (str): Name or timeframe for saving eg 'datacube', '2015_2019'
    '''

    if yearBegin > yearEnd:
        print("Wrong years")
    else:
        i = yearBegin
        j = 0
        while i <= yearEnd:
            download_file(i, directorySST)
            i = i + 1
        if yearBegin == yearEnd:
            print("Nothing to merge")
        else:
            ds_merge = []
            for filename in os.listdir(directorySST):
                cube = xr.open_dataset(os.path.join(directorySST, filename))
                ds_merge.append(cube)
                j = j + 1
            datacube = merge_datacubes(ds_merge)
            safe_datacubeSST(datacube, name, directorySST)
            datacube.close()
            for file in ds_merge:
                file.close()
            for file in os.listdir(directorySST):
                if file == "sst.day.mean." + name + ".nc":
                    continue
                else:
                    delete(os.path.join(directorySST, file))
                    continue


#################################Wrapper#################################################

def load_collection(collection, params):
    '''
    Executes the SST - or the Sentinel - Dataprocess

    Parameters:
        collection (str): The collection which is needed, SST or Sentinel2
        params ([]): The params for executing the main - method
   '''

    if collection == "SST":
        yearBegin = params[0]
        yearEnd = params[1]
        directorySST = params[2]
        name = params[3]
        mainSST(yearBegin, yearEnd, directorySST, name)

    elif collection == "Sentinel2":
        resolution = 100
        directory = params[0]
        collectionDate = params[1]
        clouds = params[2]
        username = params[3]
        password = params[4]
        aoi = 'POLYGON((7.52834379254901 52.01238155392252,7.71417925515199 52.01183230436206,7.705255583805303 51.9153349236737,7.521204845259327 51.90983021961716,7.52834379254901 52.01238155392252,7.52834379254901 52.01238155392252))'
        mainSentinel(resolution, directory, collectionDate, aoi, clouds, username, password)

    else:
        raise NameError("No Collection named like this")

###############################Example#############################################

# paramsSentinel = ['C:/Users/adria/Desktop/Uni/Semester5/Geosoft2/Code/Notebooks/Data/', ('20200601', '20200605'), (0, 30), "", ""]
# load_collection("Sentinel2", paramsSentinel)

# paramsSST = [2016, 2018, 'C:/Users/adria/Desktop/Uni/Semester5/Geosoft2/Code/Notebooks/Data/', 'datacube']
# load_collection("SST", paramsSST)
