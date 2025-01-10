from pymongo import MongoClient
import json
import datetime
import re
import time

mongoClient = MongoClient("mongodb://root:root_password@stock-database:27017/")
# mongoClient = MongoClient("mongodb://stock-database:27017/")
tweets_db = mongoClient["tweet_data"]
tweets_collection = tweets_db["elon_musk"]

def sort_tweets_by_dates(tweet):
    return datetime.datetime.strptime(tweet["Date"], "%Y-%m-%d %H:%M")

# Specify 'tweets'-folder, because the current directory when CMD in Dockerfile
# is executed is 'app' (contains all files in 'muskmonitor-backend') so 'open' can't
# find 'tweets.json', because it's inside the 'telsa_stock'-folder.
with open("tweets/tweets.json", "r") as json_file:
    json_data = json.load(json_file)
    processed_tweets = list()

    for tweet in json_data["tweets"]:
        tweet_text = tweet["text"]
        tweet_date = tweet["date"]
        # Extract date from tweet date removing information about hours.
        date = re.match(r"\w{3}\s\d{2},\s\d{4}", tweet_date)[0]
        month, day, year = date.split(" ")
        # Convert months from abbreviated strings to numbers (e.g. 'Nov' to '11').
        month = time.strptime(month, "%b").tm_mon
        # Remove trailing ','.
        day = day[:-1]
        date = f"{year}-{month}-{day}"

        tweet_time = tweet_date[tweet_date.index(":") - 2:].strip()
        timestamp = re.match(r"\d{1,2}:\d{2}\s(AM|PM)", tweet_time)[0]
        # Convert 12-hour format with AM/PM to 24-hour format.
        timestamp = datetime.datetime.strptime(timestamp, "%I:%M %p")
        timestamp = datetime.datetime.strftime(timestamp, "%H:%M")
        datetimestamp = f"{date} {timestamp}"

        processed_tweets.append({
            "Date": datetimestamp,
            "Text": tweet_text
        })

    # Sort tweets in ascending order based on 'date' value of tweet objects.
    sorted_tweets = sorted(processed_tweets, key=sort_tweets_by_dates)

    inserted = 0

    for sorted_tweet in sorted_tweets:
        if not tweets_collection.find_one({"Date": sorted_tweet["Date"], "Text": sorted_tweet["Text"]}):
            tweets_collection.insert_one(sorted_tweet)
            inserted += 1
    
    print(f"Inserted {inserted} new objects")
    print(f"Total number of objects: {tweets_collection.count_documents({})}")