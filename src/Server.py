from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/data", methods=["POST"])
def postData():
    """
    Absprache mit Dev Team Erforderlich zum Daten Einladen
    :return:
    """
    dataFromPost = request.get_json()
    print(dataFromPost)
    data = {
    "code" : 200
    }
    return jsonify(data)

@app.route("/data", methods=["GET"])
def getData():
    """
    Absprache mit Dev Teams erforderlich
    :returns:
        jsonify(data): Datacube der vom Data Team geliefert wird
    """
    dataFromPost = request.get_json()
    print(dataFromPost)
    data = None
    return jsonify(data)


def main():
    """
    Startet den Server. Aktuell im Debug Modus und Reagiert auf alle eingehenden Anfragen auf Port 80.
    """
    app.run(debug=True, host="0.0.0.0", port=443)

if __name__ == "__main__":
    main()
