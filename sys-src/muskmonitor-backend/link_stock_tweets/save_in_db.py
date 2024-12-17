from pymongo import MongoClient
import json
import datetime

mongoClient = MongoClient("mongodb://root:root_password@stock-database:27017/")
tweets_db = mongoClient["tweet_data"]
important_tweets_collection = tweets_db["elon_musk_important_tweets"]

def sort_tweets_by_dates(tweet):
    return datetime.datetime.strptime(tweet["Date"], "%Y-%m-%d %H:%M:%S")

# Specify 'tweets'-folder, because the current directory when CMD in Dockerfile
# is executed is 'app' (contains all files in 'muskmonitor-backend') so 'open' can't
# find 'tweets.json', because it's inside the 'telsa_stock'-folder.
with open("link_stock_tweets/relevant_tweets.json", "r") as json_file:
    json_data = json.load(json_file)
    processed_tweets = list()

    for tweet in json_data:
        tweet_text = tweet["Text"]
        tweet_date = tweet["Date"]
        tweet_date = tweet_date[:tweet_date.index("+")]

        processed_tweets.append({
            "Date": tweet_date,
            "Text": tweet_text,
        })

    # Sort tweets in ascending order based on 'date' value of tweet objects.
    sorted_tweets = sorted(processed_tweets, key=sort_tweets_by_dates)
    inserted = 0

    for sorted_tweet in sorted_tweets:
        if not important_tweets_collection.find_one({"Date": sorted_tweet["Date"], "Text": sorted_tweet["Text"]}):
            important_tweets_collection.insert_one(sorted_tweet)
            inserted += 1
    
    print(f"Inserted {inserted} new objects")
    print(f"Total number of objects: {important_tweets_collection.count_documents({})}")