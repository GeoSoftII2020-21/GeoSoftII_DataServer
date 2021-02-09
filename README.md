# GeoSoftII_DataServer
### Geosoftware II Projekt WiSe 2020/21
---

## Inhaltsverzeichnis
[1. Übersicht](#overview) \
[2. Installation](#install) \
[3. Anwendung](#use) \
  3.1. Zentrale Funktionalität \
  3.2. API Endpunkte \
[4. Anhang](#annex)

\
<a name="overview"><h3>Übersicht</h3></a>
Dieses Projekt ist ein Teil für einen neuen [openEO](https://openeo.org/) Backenddriver der mit [Pangeo Software Stack](https://pangeo.io/) arbeitet.

:construction: Ziel ist die von Servern Daten herunterzuladen und an die Processe SST und NDVI zu übergeben.
Dabei wird konkret die Funktion /F0020/ Collections des Pflichtenheftes umgesetzt.

Außerdem gibt es ein [Docker Repository](https://hub.docker.com/repository/docker/felixgi1516/geosoft2_dataserver), welches mit diesem verlinkt ist und über das nach Fertigstellung der Service als Image bezogen werden. Und dann als Container lokal genutzt werden kann.

\
<a name="install"><h3>Installation</h3></a>
:warning: _Die folgende Installation ist noch nicht verfügbar. Der Port und ähnliches können sich noch ändern._ 

Die Installation und Ausführung des Containers erfolgt über den Befehl:
```
docker run -p 443:443 felixgi1516/geosoft2_dataserver
````

\
<a name="use"><h3>Anwendung</h3></a>


#### Zentrale Funktionalität
Der Data_Server enthält zwei Hauptfunktionen:
- `create_Collection()` für das Erstellen der Collections
- `load_Collection()` für das Einladen der Collections

`create_Collection()` umfasst dabei die Parameter:
1. `collection`  "Sentinel" oder "SST"
2. `params` eine Liste mit den jeweils benötigten Parametern:
	- params für Sentinel:
		1. `directory` Pfad zum Arbeitsbereich (muss mit / enden)
		2. `timeframe` A touple with two values: (startdate, enddate). The dates must be in the ISO 8601 format yyyy-mm-ddThh:mm:ssZ (e.g. '2020-06-15T23:59:59Z').
		3. `cloud` Min und Maxwert für die Wolkenbedeckung
		4. `username` Username für den Copernicus Open Acess Hub
		5. `password` Passwort für den Copernicus Open Acess Hub
		6. `name` Name unter dem der Cube abgespeichert wird
	
	- params für SST:
		1. `start` Erstes Jahr des Cubes
		2. `end` Letztes Jahr des Cubes
		3. `directory` Pfad zum Arbeitsbereich (muss mit / enden)
		4. `name` Name unter dem der Cube abgespeichert wird
		
Die Funktion umfasst dabei den automatisierten Download der Dateien als Zip- btw. netCDF-Datei,
die Verarbeitung der Zip- zu netCDF-Dateien, die Umwandlung dieser zu xArray Datasets,
das Verbinden einzelner Datensätze zu einer Gesammtdatei, sowie das Abspeichern dieser.

`load_Collection()` umfasst dabei die Parameter:
1. `collection` "Sentinel" oder "SST"
2. `start` Erster Tag des Cubes. The date must be in the ISO 8601 format yyyy-mm-dd (e.g. '2020-06-15').
3. `end` Letzter Tag des Cubes. The date must be in the ISO 8601 format yyyy-mm-dd (e.g. '2020-06-15').

Die Funktion umfasst dabei das einladen des gespeicherten Cubes, eine zeitlich Auwahl, 
sowie die Rückgabe des Cubes zur weiteren Verwendung

####Example of Use
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

#### API Endpunkte
Der Microservice soll über Endpoints aufrufbar sein, leider sind noch keine verfügbar.

:bangbang: Endpoints anlegen und hier dokumentieren

\
<a name="annex"><h3>Anhang</h3></a>


#### Verwendete Software
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

