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


docker = False

app = Flask(__name__)

job = {"status": None, "id": None, "jobid": None, "errorType": None}


@app.route("/doJob/<uuid:id>", methods=["POST"])
def doJob(id):
    dataFromPost = request.get_json()
    job["status"] = "processing"
    t = threading.Thread(target=wrapper, args=(dataFromPost, id,))
    t.start()
    return Response(status=200)


@app.route("/jobStatus", methods=["GET"])
def jobStatus():
    return jsonify(job)


def wrapper(dataFromPost, id):
    # try:
    #    loadData(dataFromPost, id)
    # except:
    #    job["status"] = "error"
    #    job["errorType"] = "Unkown Error"
    #    return
    loadData(dataFromPost, id)


def loadData(dataFromPost, id):
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
    Startet den Server. Aktuell im Debug Modus und Reagiert auf alle eingehenden Anfragen auf Port 80.
    """
    global docker
    Collections_Sentinel2_SST_Data.init()
    if os.environ.get("DOCKER") == "True":
        docker = True
    if docker:
        port = 80
    else:
        port = 443
    app.run(debug=False, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
