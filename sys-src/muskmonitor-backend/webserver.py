# %%
from flask import Flask, request, jsonify
from flask_weaviate import FlaskWeaviate
from flask_pymongo import PyMongo
from pymongo import MongoClient
import bson.json_util
import logging

# %%
from sentiment_analyse import *

# %%
logger = logging.getLogger("Backend")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

app = Flask(__name__)  # Flask-Anwendungsobjekt erstellen und benennen
app.config["WEAVIATE_URL"] = "http://vector-database:8080"
weaviate = FlaskWeaviate(app)

mongo = MongoClient("mongodb://root:root_password@stock-database:27017/")
stock_database = mongo["stock_data"]
tesla_stock = stock_database["tesla"]


@app.route("/")
def home():
    c = weaviate.client
    c.connect()
    logger.info(c.is_connected())
    logger.info(c.get_meta())
    c.close()
    return "Hello, World!"


@app.route("/get_stock_data", methods=["GET", "POST"])
def get_stock_data():
    return bson.json_util.dumps(tesla_stock.find({}))


@app.route("/analyze_sentiments", methods=["POST"])
def analyse_sentiments():
    """
    Endpoint zum Durchführen der Sentiment-Analyse.
    Erwartet ein JSON mit einer Liste von Texten.
    """
    try:
        data = request.get_json()  # Empfang der JSON-Daten im POST-Request
        tweets = data["tweets"]  # Extrahiere die Tweets aus dem Request

        # Führe die Sentiment-Analyse durch
        result = analyse_and_return_json(tweets)

        # Sende das Ergebnis zurück als JSON-Antwort
        return jsonify(result)
    except Exception as e:
        logger.error(f"Fehler bei der Analyse: {str(e)}")
        return (
            jsonify({"error": "Invalid request, please provide a list of tweets."}),
            400,
        )


if __name__ == "__main__":
    # Starte die Flask-Anwendung im Debug-Modus
    app.run(debug=True)
