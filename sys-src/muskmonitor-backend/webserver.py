# flask python package 
from flask import Flask, request
from flask_weaviate import FlaskWeaviate
from flask_pymongo import PyMongo
from pymongo import MongoClient
import bson.json_util
import logging
from flask_apscheduler import APScheduler
import requests

class FlaskAPSchedulerConfig:
    SCHEDULER_API_ENABLED = True

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

# app.config["MONGO_URI"] = "mongodb://root:root_password@stock-database:27017/stock_data?authSource=admin"
# mongo = PyMongo(app)
# logger.info(mongo.cx.list_database_names())
mongo = MongoClient("mongodb://root:root_password@stock-database:27017/")
stock_database = mongo["stock_data"]
tesla_stock = stock_database["tesla"]

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

API_KEY = "BJ22JP64AWPTKJN2"
symbol = "TSLA"

# Run this task at midnight everyday.
@scheduler.task("cron", id="scrape_tesla_stock_daily", hour=0, minute=0)
def scrape_tesla_stock_daily():
    response = requests.get(f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={API_KEY}")
    data = response.json()["Time Series (Daily)"]
    
    for date, stock_data in data.items():
        if tesla_stock.count_documents({"Datum": date}) == 0:
            tesla_stock.insert_one({
                "Datum": date,
                "open": stock_data["1. open"],
                "high": stock_data["2. high"],
                "low": stock_data["3. low"],
                "close": stock_data["4. close"],
                "volume": stock_data["5. volume"],
            })

@app.route('/')
def home():
    c = weaviate.client
    c.connect()
    logger.info(c.is_connected())
    logger.info(c.get_meta())
    c.close()
    # logger.info(tesla_stock.count_documents({}))
    return 'Hello, World!'

@app.route("/get_stock_data", methods=["GET", "POST"])
def get_stock_data():
    # PyMongo queries return a cursor on the data.
    # An empty query '{}' returns all data in the collection.
    return bson.json_util.dumps(tesla_stock.find({}))
    # return bson.json_util.dumps(mongo.db["tesla"].find({}))

if __name__ == '__main__':
    # Starte die Flask-Anwendung im Debug-Modus
    app.run(debug=True)