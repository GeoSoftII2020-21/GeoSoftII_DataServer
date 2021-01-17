#@author Adrian Spork
#@author Tatjana Melina Walter

import netCDF4 as nc
import numpy   as np
import pandas  as pd
import xarray  as xr
import matplotlib.pyplot as plt
import shutil
import urllib.request as request
from contextlib import closing
from ftplib import FTP
from datetime import datetime
import os


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
        else: counter += 1

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
            ds1 =  xr.combine_by_coords([ds1, ds_merge[count]], combine_attrs="override")
            count += 1
            diff = datetime.now() - start1
            print("Succesfully merged cube nr " + str(count) + " to the base cube in "+ str(diff.seconds) + 's')
        diff = datetime.now() - start
        print('All cubes merged for ' + str(diff.seconds) + 's')
        return ds1


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
    print("Done saving after "+ str(diff.seconds) + 's')


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
            os.rename(os.path.join(directorySST, os.listdir(directorySST)[0]),directorySST + "sst.day.mean." + name + ".nc")
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


##################################Example#############################################
#yearBegin = 2016
#yearEnd = 2017
#directorySST = 'D:/Tatjana/Documents/Studium/Semester 5 - Abgaben/Geosoftware 2/Code/SST_Data/'
#name = 'datacube'

#mainSST(yearBegin, yearEnd, directorySST, name)
