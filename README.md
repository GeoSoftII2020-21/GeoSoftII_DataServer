# GeoSoftII_DataServer
### Geosoftware II Project WiSe 2020/21
---

## Table of contents
[1. Overview](#overview) \
[2. Installation](#install) \
[3. Scope of functionalities](#functionalities)  \
[4. Examples of use](#use) \
[5. Technologies](#technologies)\
\
<a name="overview"><h3>Overview</h3></a>
This project is part of a new [openEO](https://openeo.org/) back-end driver which uses the [Pangeo Software Stack](https://pangeo.io/).

The aim is to download data from servers and transfer it to the SST and NDVI processes.
The function /F0020/ Collections of the functional specification is implemented.

There also exists a [Docker Repository](https://hub.docker.com/repository/docker/felixgi1516/geosoft2_dataserver), which is linked with this one and from which the service can be obtained as an image. And can then be used locally as a container.

\
<a name="install"><h3>Installation</h3></a>
The installation and execution is possible exclusively provided within the framework of the *[docker-compose.yml](https://github.com/GeoSoftII2020-21/GeoSoftII_Projekt/blob/Docker-compose/docker-compose.yml)*.
```docker
docker-compose up
```
\
<a name="functionalities"><h3>Scope of functionalities</h3></a>
The Data_Server contains two main functions:
- `create_Collection()` for creating the Collections
- `load_Collection()` for loading the collections.

`create_Collection()` includes the parameters:
1. `collection` "Sentinel" or "SST".
2. `params` a list with the required parameters:
	- params for Sentinel:
		1. `directory` path to the workspace (must end with /)
		2. `timeframe` A touple with two values: (startdate, enddate). The dates must be in the ISO 8601 format yyyy-mm-ddThh:mm:ssZ (e.g. '2020-06-15T23:59:59Z').
		3. `cloud` Min and max value for cloud cover
		4. `username` username for the Copernicus Open Acess Hub
		5. `password` Password for the Copernicus Open Acess Hub
		6. `name` Name under which the cube is stored
	
	- params for SST:
		1. `start` First year of the cube
		2. `end` Last year of the cube
		3. `directory` Path to the workspace (must end with /)
		4. `name` Name under which the cube is saved
		
The function includes the automated download of the files as Zip- btw. netCDF-file,
the processing of the Zip- to netCDF-files, the conversion of these to xArray Datasets,
the linking of individual datasets to a complete file, and the saving of this file.

`load_Collection()` includes the parameters:
1. `collection` "Sentinel" or "SST".
2. `start` First day of the cube. The date must be in the ISO 8601 format yyyy-mm-dd (e.g. '2020-06-15').
3. `end` Last day of the cube. The date must be in the ISO 8601 format yyyy-mm-dd (e.g. '2020-06-15').

The function includes the loading of the stored cube, a temporal selection, 
and the return of the cube for further use.

\
<a name="use"><h3>Examples of use</h3></a>
`create_Collection()`
```
'''Params Sentinel'''
directorySentinel = "C:/example/SentinelData/"
nameSentinel = "Sentinel_datacube"
timeframeSentinel = ('2020-06-01T00:00:00Z', '2020-06-15T23:59:59Z')
cloud = (0, 30)
username = "xyz"
password = "xyz"
paramsSentinel = [directorySentinel, timeframeSentinel, cloud, username, password, nameSentinel]

'''Params SST'''
directorySST = "C:/example/SSTData/"
nameSST = 'SST_datacube'
SST_start = 2013
SST_end = 2018
paramsSST = [SST_start, SST_end, directorySST, nameSST]

'''Setup'''
create_collection("Sentinel2", paramsSentinel)
create_collection("SST", paramsSST)
````

`load_Collection`
```
Sentinel = load_collection("Sentinel2",'2020-06-01', '2020-06-13')
SST = load_collection("SST",'2013-06-01', '2018-06-03')
````

#### API endpoints

- `POST /doJob/{job_id}` Accepts a job which is being processed.
- `GET /jobstatus` Returns a JSON with the job status.


\
<a name="technologies"><h3>Technologies</h3></a>

Software | Version
------ | ------
numpy | 1.19.3
scipy | 
netCDF4 | 
pandas | 1.1.5
xarray | 0.16.2
sentinelsat | 0.14
rasterio | 1.1.8
dask[complete] | 2.30.0

