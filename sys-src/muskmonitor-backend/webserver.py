from flask import Flask, request, jsonify, current_app
from flask_pymongo import PyMongo
from pymongo import MongoClient
import bson.json_util
import logging
from sentiment_analyse import analyse_and_return_json
from flask_apscheduler import APScheduler
import requests
from x_scraper.nitter_scraper import *

class FlaskAPSchedulerConfig:
    SCHEDULER_API_ENABLED = True

logger = logging.getLogger("Backend")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

app = Flask(__name__)  # Flask-Anwendungsobjekt erstellen und benennen
app.config.from_object(FlaskAPSchedulerConfig)
mongo = MongoClient("mongodb://root:root_password@stock-database:27017/")
stock_database = mongo["stock_data"]
tesla_stock = stock_database["tesla"]
tweets_database = mongo["tweet_data"]
tweets_collection = tweets_database["elon_musk"]
scheduler = APScheduler()
scheduler.init_app(app)
#scheduler.api_enabled = True
scheduler.start()

#API_KEY = "BJ22JP64AWPTKJN2"
API_KEY = "0HODL581Z1697EQ7"
symbol = "TSLA"

with app.app_context():
    current_app.scraper_status = {"last_run": None, "new_tweets": 0}

json_file = "x_scraper/nitter_latest_tweets.json"

# Run this task at midnight everyday.
@scheduler.task("cron", id="scrape_tesla_stock_daily", hour=0, minute=0)
def scrape_tesla_stock_daily():
    # Prevent exceptions when scraping too much data in a single day from crashing the server.
    try:
        response = requests.get(f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={API_KEY}")
        data = response.json()["Time Series (Daily)"]
        
        for date, stock_data in data.items():
            if tesla_stock.count_documents({"Datum": date}) == 0:
                to_insert = {
                    "Datum": date,
                    "open": stock_data["1. open"],
                    "high": stock_data["2. high"],
                    "low": stock_data["3. low"],
                    "close": stock_data["4. close"],
                    "volume": stock_data["5. volume"],
                }
                tesla_stock.insert_one(to_insert)
                logger.info(f"Inserted: {to_insert}")
    except Exception as e:
        logger.info(f"Exception getting stock data from alpha vantage: {e}")

# Run this task every 30 minutes.
@scheduler.task("interval", id="scrape_tweets_daily", minutes=30)
def scrape_tweets_daily():
    with app.app_context():
        """Function to run the scraper periodically."""
        new_tweets = fetch_tweets_from_nitter()
        if not new_tweets:
            print("No new tweets fetched.")
            current_app.scraper_status["new_tweets"] = 0
            return

        existing_tweets = load_existing_tweets(json_file)
        existing_ids = {tweet["Tweet_ID"] for tweet in existing_tweets}

        unique_tweets = [tweet for tweet in new_tweets if tweet["Tweet_ID"] not in existing_ids]

        if unique_tweets:
            print(f"Adding {len(unique_tweets)} new tweets.")
            updated_tweets = unique_tweets + existing_tweets
            # Reassign tweet counts for all tweets
            for i, tweet in enumerate(updated_tweets, start=1):
                tweet["Tweet_count"] = i
            save_tweets(json_file, updated_tweets)
            current_app.scraper_status["new_tweets"] = len(unique_tweets)
        else:
            print("No new tweets to add.")
            current_app.scraper_status["new_tweets"] = 0
        current_app.scraper_status["last_run"] = "Ran successfully"


@app.route("/")
def home():
    return "Hello, World!"


@app.route("/get_stock_data", methods=["GET", "POST"])
def get_stock_data():
    return bson.json_util.dumps(tesla_stock.find({}).sort("Datum"))


@app.route("/analyze_sentiments", methods=["GET", "POST"])
def analyse_sentiments():
    """
    Endpoint zum Durchführen der Sentiment-Analyse.
    Erwartet ein JSON mit einer Liste von Texten.
    """
    try:
        data = request.get_json()  # Empfang der JSON-Daten im POST-Request
        tweets = data["tweets"]  # Extrahiere die Tweets aus dem Request

        ## Führe die Sentiment-Analyse durch
        result = analyse_and_return_json(tweets)

        tweets_from_db = tweets_collection.find({})
        tweets_text = [tweet["Text"] for tweet in tweets_from_db]
        result = analyse_and_return_json(tweets_text)

        for sentiment_result, tweet in zip(result, tweets_from_db):
            tweet["Class"] = sentiment_result["sentiment"]

        return jsonify(bson.json_util.dumps(tweets_from_db))
        # Sende das Ergebnis zurück als JSON-Antwort
        #return jsonify(result)
    except Exception as e:
        logger.error(f"Fehler bei der Analyse: {str(e)}")
        return (
            jsonify({"error": "Invalid request, please provide a list of tweets."}),
            400,
        )
    
@app.route("/start-scraper")
def start_scraper():
    with app.app_context():
        """Manually trigger the scraper."""
        scrape_tweets_daily()
        return jsonify({"message": "Scraper executed manually.", "status": current_app.scraper_status})

@app.route("/scraper-status")
def scraper_status_endpoint():
    with app.app_context():
        """Check the status of the scraper."""
        return jsonify(current_app.scraper_status)

if __name__ == "__main__":
    try:
        # Starte die Flask-Anwendung im Debug-Modus
        app.run(debug=True)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
