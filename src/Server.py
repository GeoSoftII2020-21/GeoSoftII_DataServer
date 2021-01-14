import os

import requests
from flask import Flask, request, jsonify, Response
import threading
import xarray
import uuid
docker = False

app = Flask(__name__)

job = {"status": None, "id": None}


@app.route("/doJob", methods=["POST"])
def doJob():
    dataFromPost = request.get_json()
    job["status"] = "processing"
    t = threading.Thread(target=loadData, args=(dataFromPost,))
    t.start()
    return Response(status=200)


@app.route("/jobStatus", methods=["GET"])
def jobStatus():
    return jsonify(job)

def loadData(dataFromPost):
    #Todo: Sinnvoll machen ?
    if dataFromPost["arguments"]["DataType"] == "SST":
        data = xarray.load_dataset("data/sst.day.mean.1984.v2.nc")
        id = uuid.uuid1()
        data.to_netcdf("data/"+str(id)+".nc")
        job["id"] = str(id)
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
