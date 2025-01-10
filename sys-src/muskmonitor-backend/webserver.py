from flask import Flask, request, jsonify, current_app, Response
from flask_pymongo import PyMongo
from pymongo import MongoClient, DESCENDING, ASCENDING
import bson.json_util
import logging
from flask_apscheduler import APScheduler
import requests
from x_scraper.nitter_scraper import *
import re
import time
import datetime
from tesla_stock.stock_prediction import *
from threading import Thread
from flask_cors import CORS

from sentiment_analyse import analyse_and_return_json
from x_scraper.nitter_scraper import (
    fetch_tweets_from_nitter,
    load_existing_tweets,
    save_tweets,
)


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
CORS(app)
app.config.from_object(FlaskAPSchedulerConfig)
mongo = MongoClient("mongodb://root:root_password@stock-database:27017/")
# mongo = MongoClient("mongodb://stock-database:27017/")
stock_database = mongo["stock_data"]
tesla_stock = stock_database["tesla"]

tweets_database = mongo["tweet_data"]
elon_musk_tweets = tweets_database["elon_musk"]
important_tweets_collection = tweets_database["elon_musk_important_tweets"]

scheduler = APScheduler()
scheduler.init_app(app)
# scheduler.api_enabled = True
scheduler.start()

# API_KEY = "BJ22JP64AWPTKJN2"
# Stock-API-Konfiguration
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "0HODL581Z1697EQ7")
symbol = "TSLA"

with app.app_context():
    current_app.scraper_status = {"last_run": None, "new_tweets": 0}

json_file = "x_scraper/nitter_latest_tweets.json"


# Run this task at midnight everyday.
@scheduler.task(
    "cron",
    id="scrape_tesla_stock_daily",
    hour=1,
    minute=0,
    misfire_grace_time=900,
    coalesce=True,
)
def scrape_tesla_stock_daily():
    # Prevent exceptions when scraping too much data in a single day from crashing the server.
    try:
        response = requests.get(
            f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={API_KEY}"
        )
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

        try:
            new_tweets = fetch_tweets_from_nitter()
            if not new_tweets:
                logger.info("No new tweets fetched.")
                current_app.scraper_status["new_tweets"] = 0
                return

            # Fetch existing tweets from MongoDB (no need for JSON file operations)
            existing_tweets = list(elon_musk_tweets.find({}))
            existing_dates = {tweet["Date"] for tweet in existing_tweets}  # Using Date for uniqueness

            unique_tweets = [
                tweet for tweet in new_tweets if tweet["Created_At"] not in existing_dates
            ]

            if unique_tweets:
                logger.info(f"Adding {len(unique_tweets)} new tweets.")

                # Insert the new tweets into the database
                for tweet in unique_tweets:
                    try:
                        tweet_text = tweet["Created_At"]
                        
                        # Extract date and time using regex, more robust pattern matching
                        date_match = re.match(r"(\w{3})\s(\d{1,2}),\s(\d{4})\s·\s(\d{1,2}):(\d{2})\s(AM|PM)\sUTC", tweet_text)
                        if not date_match:
                            logger.error(f"Date format not found in tweet: {tweet_text}")
                            continue

                        month, day, year, hour, minute, period = date_match.groups()
                        month = time.strptime(month, "%b").tm_mon
                        day = day.strip()  # Remove any leading or trailing spaces
                        formatted_date = f"{year}-{month:02d}-{int(day):02d}"  # Zero-pads the day

                        # Convert 12-hour format to 24-hour format
                        hour = int(hour)
                        minute = int(minute)
                        if period == "PM" and hour != 12:
                            hour += 12
                        if period == "AM" and hour == 12:
                            hour = 0

                        formatted_time = f"{hour:02d}:{minute:02d}"
                        datetimestamp = f"{formatted_date} {formatted_time}"

                        # Insert the tweet into the database
                        result = elon_musk_tweets.update_one(
                            {"Date": datetimestamp},
                            {"$set": {"Text": tweet["Text"], "Date": datetimestamp}},
                            upsert=True
                        )

                        if result.matched_count > 0:
                            logger.info(f"Updated existing tweet with Date: {datetimestamp}")
                        elif result.upserted_id:
                            logger.info(f"Inserted new tweet with Date: {datetimestamp}")
                    except Exception as e:
                        logger.error(f"Error processing tweet: {e}")

                current_app.scraper_status["new_tweets"] = len(unique_tweets)
            else:
                logger.info("No new tweets to add.")
                current_app.scraper_status["new_tweets"] = 0

            current_app.scraper_status["last_run"] = "Ran successfully"

        except Exception as e:
            logger.error(f"Error in scrape_tweets_daily task: {e}")


@app.route("/")
def home():
    return "Hello, World!"


# Alle gespeicherten Stock-Daten abrufen
@app.route("/get_stock_data", methods=["GET", "POST"])
def get_stock_data():
    try:
        stock_data = tesla_stock.find({}).sort("Datum")
        response_data = bson.json_util.dumps(stock_data, ensure_ascii=False)
        return Response(response_data, mimetype="application/json")
    except Exception as e:
        logger.error(f"Error retrieving stock data: {e}")
        return jsonify({"error": "Failed to fetch stock data"}), 500


@app.route("/get_important_tweets", methods=["GET", "POST"])
def get_important_tweets():
    try:
        # Fetch important tweets from the database
        important_tweets = important_tweets_collection.find({}).sort("Date")
        
        # Serialize the data using bson.json_util to handle MongoDB BSON objects
        response_data = bson.json_util.dumps(important_tweets)
        
        # Return the response with correct mimetype
        return Response(response_data, mimetype="application/json")
    except Exception as e:
        logger.error(f"Error retrieving important tweets: {e}")
        return jsonify({"error": "Failed to fetch important tweets"}), 500



@app.route("/analyze_sentiments", methods=["GET", "POST"])
def analyse_sentiments():
    """
    Endpoint for performing sentiment analysis.
    Fetches recent tweets from the database and analyzes their sentiment.
    """
    try:
        # Retrieve the latest 100 tweets from the database
        tweets_from_db = list(elon_musk_tweets.find({}).sort("Date", DESCENDING))[-100:]
        tweets_text = [tweet["Text"] for tweet in tweets_from_db]

        # Perform sentiment analysis
        sentiment_results = analyse_and_return_json(tweets_text)

        # Update each tweet with its sentiment class
        for sentiment_result, tweet in zip(sentiment_results, tweets_from_db):
            tweet["Class"] = sentiment_result["sentiment"]
            tweet["Title"] = "Elon Musk schreibt auf X"
            del tweet["_id"]

        # Serialize the results and return them
        response_data = bson.json_util.dumps(tweets_from_db)
        return Response(response_data, mimetype="application/json")
    except Exception as e:
        logger.error(f"Error during sentiment analysis: {str(e)}")
        return jsonify({"error": "Failed to analyze sentiments"}), 500


@app.route("/start_scraper")
def start_scraper():
    """
    Endpoint to manually trigger the scraper for fetching tweets.
    """
    try:
        with app.app_context():
            scrape_tweets_daily()
            response_data = {
                "message": "Scraper executed manually.",
                "status": current_app.scraper_status,
            }
            return Response(
                bson.json_util.dumps(response_data), mimetype="application/json"
            )
    except Exception as e:
        logger.error(f"Error while manually starting scraper: {str(e)}")
        return jsonify({"error": "Failed to start scraper"}), 500



@app.route("/scraper_status")
def scraper_status_endpoint():
    """
    Endpoint to fetch the current status of the scraper.
    """
    try:
        with app.app_context():
            response_data = current_app.scraper_status
            return Response(
                bson.json_util.dumps(response_data), mimetype="application/json"
            )
    except Exception as e:
        logger.error(f"Error fetching scraper status: {str(e)}")
        return jsonify({"error": "Failed to fetch scraper status"}), 500


# Global variable to store results
results_file = "prediction_results.json"
with app.app_context():
    current_app.lock = False #prevent more concurrent predictions

# Function to perform stock prediction
import json  # Ensure you import the json module if you haven't


# Function to perform stock prediction
def perform_stock_prediction():
    with app.app_context():
        if current_app.lock:
            logger.info("Prediction is already in progress")
            return
        current_app.lock = True  # Acquire the lock
    try:
        # Fetch data from the database
        datafromdb = fetch_data_from_db()
        train_data, test_data, scaler = prepare_data(datafromdb)
        x_train, y_train = create_lstm_data(train_data)
        x_test, y_test = create_lstm_data(test_data)

        # Extract test dates
        test_dates = datafromdb["Datum"][-len(test_data):]

        # Train the model
        model = train_lstm_model(x_train, y_train)

        # Generate predictions and future forecast
        predicted_values_with_dates, actual_values, rmse, future_values_with_dates = (
            evaluate_and_forecast(
                model, x_test, y_test, scaler, test_dates, future_steps=10
            )
        )

        # Prepare results to be saved
        results = {
            "predicted_values": [
                {"date": date.strftime("%Y-%m-%d"), "value": value}
                for date, value in predicted_values_with_dates
            ],
            "actual_values": actual_values,
            "rmse": rmse,
            "future_predictions": [
                {"date": date.strftime("%Y-%m-%d"), "value": value}
                for date, value in future_values_with_dates
            ],
        }

        # Save results to MongoDB
        stock_database["predictions"].insert_one(results)
    except Exception as e:
        logger.error(f"Error during stock prediction: {e}")
    finally:
        with app.app_context():
            current_app.lock = False  # Release the lock



@app.route("/start_stock_prediction", methods=["GET", "POST"])
def start_stock_prediction():
    with app.app_context():
        if current_app.lock:
            return jsonify({"status": "Prediction is already in progress"}), 429  # Too Many Requests
        try:
            # Run the prediction in a background thread
            thread = Thread(target=perform_stock_prediction)
            thread.start()
            response_data = {"status": "Stock prediction started"}
            return Response(
                bson.json_util.dumps(response_data), mimetype="application/json"
            ), 202  # Accepted
        except Exception as e:
            logger.error(f"Error starting stock prediction: {str(e)}")
            return jsonify({"error": "Failed to start stock prediction"}), 500


@app.route("/get_prediction_results", methods=["GET"])
def get_prediction_results():
    """
    Endpoint to fetch the latest stock prediction results.
    """
    try:
        # Fetch the most recent prediction from the database
        prediction_results = stock_database["predictions"].find_one(
            {}, sort=[("_id", -1)]
        )
        if prediction_results:
            # Serialize the result and return it
            response_data = bson.json_util.dumps(prediction_results)
            return Response(response_data, mimetype="application/json")
        else:
            return jsonify({"status": "No predictions available yet"}), 404
    except Exception as e:
        logger.error(f"Error fetching prediction results: {str(e)}")
        return jsonify({"error": "An error occurred while fetching predictions"}), 500

# Anwendung starten
if __name__ == "__main__":
    try:
        app.run(debug=True)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
