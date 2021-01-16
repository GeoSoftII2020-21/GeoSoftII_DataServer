import os
import Collections_Sentinel2_SST_Data
import requests
from flask import Flask, request, jsonify, Response
import threading
import xarray
import uuid
import shutil
docker = False

app = Flask(__name__)

job = {"status": None, "id": None}


@app.route("/doJob/<uuid:id>", methods=["POST"])
def doJob(id):
    dataFromPost = request.get_json()
    job["status"] = "processing"
    t = threading.Thread(target=loadData, args=(dataFromPost,id,))
    t.start()
    return Response(status=200)


@app.route("/jobStatus", methods=["GET"])
def jobStatus():
    return jsonify(job)


def loadData(dataFromPost, id):
    os.mkdir("/data/"+str(id)+"/data")
    Collections_Sentinel2_SST_Data.load_collection("SST",[2016,2017,"/data/"+str(id)+"/data/","cube"])
    #sst.day.mean immer vor dem namen
    data = xarray.load_dataset("data/"+str(id)+"/data/sst.day.mean.cube.nc")
    subid = uuid.uuid1()
    data.to_netcdf("data/" + str(id) + "/" + str(subid) + ".nc")
    shutil.rmtree("data/"+str(id)+"/data")
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
