import os
import Collections_Sentinel2_SST_Data
import requests
from flask import Flask, request, jsonify, Response
import threading
import xarray
import uuid
import shutil
import datetime
import numpy as np
import sys
import time

docker = False

app = Flask(__name__)

'''Job Meta information'''
job = {"status": None, "id": None, "jobid": None, "errorType": None}


@app.route("/doJob/<uuid:id>", methods=["POST"])
def doJob(id):
    """
    Expects a job reference which will be processed.
    Args:
        id: JobID

    Returns:

    """
    dataFromPost = request.get_json()
    job["status"] = "processing"
    t = threading.Thread(target=wrapper, args=(dataFromPost, id,))
    t.start()
    return Response(status=200)


@app.route("/jobStatus", methods=["GET"])
def jobStatus():
    """
    Returns the Job Status as a json.
    Returns:
        object:
    """
    return jsonify(job)


def wrapper(dataFromPost, id):
    """
    Wrapper function for the Load Data Function
    Returns:
        object:
    """
    try:
        loadData(dataFromPost, id)
    except:
        job["status"] = "error"
        job["errorType"] = "Unkown Error"
        print(sys.exc_info())
        return


def loadData(dataFromPost, id):
    """
    Loadin a dataset from the given Function from the Collections_Sentinel2__ST_Data.py
    Args:
        dataFromPost: JSON which got delivered with the request
        id: Job ID

    Returns: Void

    """
    job["status"] = "running"
    job["jobid"] = str(id)
    if dataFromPost["arguments"]["DataType"] == "SST":
        try:
            fromDate = datetime.datetime.strptime(dataFromPost["arguments"]["timeframe"][0],
                                                  dataFromPost["arguments"]["timeframe"][2])
            toDate = datetime.datetime.strptime(dataFromPost["arguments"]["timeframe"][1],
                                                dataFromPost["arguments"]["timeframe"][2])
            fromDate = fromDate.strftime("%Y-%m-%d")
            toDate = toDate.strftime("%Y-%m-%d")
        except:
            job["status"] = "error"
            job["errorType"] = "TimeframeLengthError"
            print(sys.exc_info())
            return
        try:
            cube: xarray.Dataset = Collections_Sentinel2_SST_Data.load_collection("SST",
                                                                                  fromDate, toDate)
        except Collections_Sentinel2_SST_Data.TimeframeLengthError:
            job["status"] = "error"
            job["errorType"] = "TimeframeLengthError"
            return
        except Collections_Sentinel2_SST_Data.ParameterTypeError:
            job["status"] = "error"
            job["errorType"] = "ParameterTypeError"
            return
        except Collections_Sentinel2_SST_Data.FileNotFoundError:
            job["status"] = "error"
            job["errorType"] = "FileNotFoundError"
            return
        except:
            job["status"] = "error"
            job["errorType"] = "Unkown Error"
            print(sys.exc_info())
            return
        subid = uuid.uuid1()
        toFile = os.path.join("/data/", str(id), str(subid) + ".nc")
        cube = cube.fillna(np.nan)
        cube.to_netcdf(toFile)
        job["id"] = str(subid)
        job["status"] = "done"
    elif dataFromPost["arguments"]["DataType"] == "Sentinel2":
        try:
            fromDate = datetime.datetime.strptime(dataFromPost["arguments"]["timeframe"][0],
                                                  dataFromPost["arguments"]["timeframe"][2])
            toDate = datetime.datetime.strptime(dataFromPost["arguments"]["timeframe"][1],
                                                dataFromPost["arguments"]["timeframe"][2])
            fromDate = fromDate.strftime("%Y-%m-%d")
            toDate = toDate.strftime("%Y-%m-%d")
        except:
            job["status"] = "error"
            job["errorType"] = "TimeframeLengthError"
            print(sys.exc_info())
            return
        try:
            cube: xarray.DataArray = Collections_Sentinel2_SST_Data.load_collection("Sentinel2", fromDate, toDate)
        except Collections_Sentinel2_SST_Data.TimeframeLengthError:
            job["status"] = "error"
            job["errorType"] = "TimeframeLengthError"
            return
        except Collections_Sentinel2_SST_Data.ParameterTypeError:
            job["status"] = "error"
            job["errorType"] = "ParameterTypeError"
            return
        except Collections_Sentinel2_SST_Data.FileNotFoundError:
            job["status"] = "error"
            job["errorType"] = "FileNotFoundError"
            return
        except:
            job["status"] = "error"
            job["errorType"] = "Unkown Error"
            print(sys.exc_info())
            return
        subid = uuid.uuid1()
        toFile = os.path.join("/data/", str(id), str(subid) + ".nc")
        cube.to_netcdf(toFile)
        job["id"] = str(subid)
        job["status"] = "done"


def main():
    """
    Starts the Server.
    """
    global docker
    '''Downloadeing Datasets'''
    Collections_Sentinel2_SST_Data.init()
    time.sleep(10)
    '''Sends a request to signal that the server is ready to use'''
    url = os.environ.get("process_name")
    url = "http://"+ str(url) +":80/dataStatus"
    requests.get(url)
    if os.environ.get("DOCKER") == "True":
        docker = True
    if docker:
        port = 80
    else:
        port = 443
    app.run(debug=False, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
