# flask python package 
from flask import Flask, request
from flask_weaviate import FlaskWeaviate
# from flask_pymongo import PyMongo
from pymongo import MongoClient
import bson.json_util
import logging
import json

logger = logging.getLogger('Backend')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

app = Flask(__name__)  # Flask-Anwendungsobjekt erstellen und benennen
app.config["WEAVIATE_URL"] = "http://vector-database:8080"
weaviate = FlaskWeaviate(app)

mongo = MongoClient("mongodb://root:root_password@stock-database:27017/")
stock_database = mongo["stock_data"]
tesla_stock = stock_database["tesla"]

@app.route('/')
def home():
    c = weaviate.client
    c.connect()
    logger.info(c.is_connected())
    logger.info(c.get_meta())
    c.close()
    logger.info(tesla_stock.count_documents({}))
    return 'Hello, World!'

@app.route("/get_stock_data", methods=["GET", "POST"])
def get_stock_data():
    # PyMongo queries return a cursor on the data.
    # An empty query '{}' returns all data in the collection.
    return bson.json_util.dumps(tesla_stock.find({}))

if __name__ == '__main__':
    # Starte die Flask-Anwendung im Debug-Modus
    app.run(debug=True)