#@author Adrian Spork
#@author Tatjana Melina Walter

#import Sentinel2_Data
#import SST_Data

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
        #mainSST(yearBegin, yearEnd, directorySST, name)
        
    elif collection == "Sentinel2":
        resolution = 100
        directory = params[0]
        collectionDate = params[1]
        clouds = params[2]
        username = params[3]
        password = params[4]
        aoi = 'POLYGON((7.52834379254901 52.01238155392252,7.71417925515199 52.01183230436206,7.705255583805303 51.9153349236737,7.521204845259327 51.90983021961716,7.52834379254901 52.01238155392252,7.52834379254901 52.01238155392252))'
        #mainSentinel(resolution, directory, collectionDate, aoi, clouds, username, password)
    
    else:
        raise NameError("No Collection named like this")
	

#############################Execution##########################	
#paramsSentinel = ['C:/Users/adria/Desktop/Uni/Semester5/Geosoft2/Code/Notebooks/Sentinel/Data/', ('20200601', '20200630'), (0, 30), "", ""]
#load_collection("Sentinel2", paramsSentinel)

#paramsSST = [2016, 2018, 'C:/Users/adria/Desktop/Uni/Semester5/Geosoft2/Code/Notebooks/Sentinel/Data/', 'datacube']
#load_collection("SST", paramsSST)
