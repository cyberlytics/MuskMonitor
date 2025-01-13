from pymongo import MongoClient
import json
import datetime
import yfinance
import requests

# mongoClient = MongoClient("mongodb://root:root_password@stock-database:27017/")
mongoClient = MongoClient("mongodb://stock-database:27017/")
stockDB = mongoClient["stock_data"]
telsaCollection = stockDB["tesla"]

tesla_data = yfinance.download("TSLA", start="2010-01-01", end="2014-12-31")
# Convert multi column index of 'Price' (Open, Close, ...) and 'Ticker' (TSLA) into just 'Price'.
tesla_data.columns = tesla_data.columns.get_level_values("Price")

inserted = 0
for date_and_time_index, row in tesla_data.iterrows():
    date = date_and_time_index.strftime("%Y-%m-%d")
    if telsaCollection.count_documents({"Datum": date}) == 0:
        telsaCollection.insert_one({
            "Datum": date,
            "open": row["Open"],
            "high": row["High"],
            "low": row["Low"],
            "close": row["Close"],
            "volume": row["Volume"],
        })
        inserted += 1

# Specify 'tesla_stock'-folder, because the current directory when CMD in Dockerfile
# is executed is 'app' (contains all files in 'muskmonitor-backend') so 'open' can't
# find 'konvertierte_datei.json', because it's inside the 'telsa_stock'-folder.
with open("tesla_stock/konvertierte_datei.json", "r") as jsonFile:
    def sort_data_by_dates(data):
        return datetime.datetime.strptime(data["Datum"], "%Y-%m-%d")

    jsonData = json.load(jsonFile)

    # Sort data in ascending order based on 'Datum' value of data objects.
    sortedData = sorted(jsonData, key=sort_data_by_dates)

    for stockDataObject in sortedData:
        # Insert data only if it doesn't already exist in the collection.
        if telsaCollection.count_documents({"Datum": stockDataObject["Datum"]}) == 0:
            telsaCollection.insert_one(stockDataObject)
            inserted += 1
            
print(f"Inserted {inserted} new objects")
print(f"Total number of objects: {telsaCollection.count_documents({})}")