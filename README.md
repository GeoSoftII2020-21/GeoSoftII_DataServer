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
docker run -p 3000:3000 felixgi1516/geosoft2_dataserver
````

\
<a name="use"><h3>Anwendung</h3></a>


#### Zentrale Funktionalität
:bangbang: Funktionalität dokumentieren


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

