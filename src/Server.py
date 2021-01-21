import os
import Collections_Sentinel2_SST_Data
import requests
from flask import Flask, request, jsonify, Response
import threading
import xarray
import uuid
import shutil
import datetime

docker = False

app = Flask(__name__)

job = {"status": None, "id": None, "jobid": None}


@app.route("/doJob/<uuid:id>", methods=["POST"])
def doJob(id):
    dataFromPost = request.get_json()
    job["status"] = "processing"
    t = threading.Thread(target=loadData, args=(dataFromPost, id,))
    t.start()
    return Response(status=200)


@app.route("/jobStatus", methods=["GET"])
def jobStatus():
    return jsonify(job)


def loadData(dataFromPost, id):
    job["status"] = "running"
    job["jobid"] = str(id)
    os.mkdir("/data/" + str(id) + "/data")
    if dataFromPost["arguments"]["DataType"] == "SST":
        fromDate = datetime.datetime.strptime(dataFromPost["arguments"]["timeframe"][0],dataFromPost["arguments"]["timeframe"][2])
        toDate = datetime.datetime.strptime(dataFromPost["arguments"]["timeframe"][1],
                                              dataFromPost["arguments"]["timeframe"][2])
        try:
            Collections_Sentinel2_SST_Data.load_collection("SST",
                                                           [fromDate.year, toDate.year,
                                                            os.path.join("/data/", str(id), "data/"), "cube"])
        except ValueError:
            job["status"] = "failed"
            print("Job Gescheitert!")
            return
        subid = uuid.uuid1()
        fromFile = os.path.join("/data/", str(id), "data/sst.day.mean.cube.nc")
        toFile = os.path.join("/data/", str(id), str(subid) + ".nc")
        os.rename(fromFile, toFile)
        shutil.rmtree("data/" + str(id) + "/data")
        job["id"] = str(subid)
        job["status"] = "done"
    elif dataFromPost["arguments"]["DataType"] == "Sentinel2":
        fromDate = datetime.datetime.strptime(dataFromPost["arguments"]["timeframe"][0],
                                              dataFromPost["arguments"]["timeframe"][2])
        toDate = datetime.datetime.strptime(dataFromPost["arguments"]["timeframe"][1],
                                            dataFromPost["arguments"]["timeframe"][2])
        fromDate = fromDate.strftime("%Y%m%d")
        toDate = toDate.strftime("%Y%m%d")
        params = [os.path.join("data/",str(id),"data/"),(fromDate,toDate),(dataFromPost["arguments"]["cloudcoverage"][0],dataFromPost["arguments"]["cloudcoverage"][1]),dataFromPost["arguments"]["Login"][0],dataFromPost["arguments"]["Login"][1]]
        Collections_Sentinel2_SST_Data.load_collection("Sentinel2",params)
        x = os.listdir("data/"+str(id)+"/data")
        subid = uuid.uuid1()
        toFile = os.path.join("/data/", str(id), str(subid) + ".nc")
        os.rename("data/"+str(id)+"/data/"+str(x[0]), toFile)
        job["id"] = str(subid)
        job["status"] = "done"


def main():
    """
    Startet den Server. Aktuell im Debug Modus und Reagiert auf alle eingehenden Anfragen auf Port 80.
    """
    global docker
    if os.environ.get("DOCKER") == "True":
        docker = True
    if docker:
        port = 80
    else:
        port = 443
    app.run(debug=True, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
