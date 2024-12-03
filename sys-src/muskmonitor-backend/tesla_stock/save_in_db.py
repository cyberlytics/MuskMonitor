from pymongo import MongoClient
import json
import datetime

mongoClient = MongoClient("mongodb://root:root_password@stock-database:27017/")
stockDB = mongoClient["stock_data"]
telsaCollection = stockDB["tesla"]

def sort_data_by_dates(data):
    return datetime.datetime.strptime(data["Datum"], "%Y-%m-%d")

# Specify 'tesla_stock'-folder, because the current directory when CMD in Dockerfile
# is executed is 'app' (contains all files in 'muskmonitor-backend') so 'open' can't
# find 'konvertierte_datei.json', because it's inside the 'telsa_stock'-folder.
with open("tesla_stock/konvertierte_datei.json", "r") as jsonFile:
    jsonData = json.load(jsonFile)

    # Sort data in ascending order based on 'Datum' value of data objects.
    sortedData = sorted(jsonData, key=sort_data_by_dates)
    
    inserted = 0

    for stockDataObject in sortedData:
        # Insert data only if it doesn't already exist in the collection.
        if telsaCollection.count_documents({"Datum": stockDataObject["Datum"]}) == 0:
            telsaCollection.insert_one(stockDataObject)
            inserted += 1
            
    print(f"Inserted {inserted} new objects")
    print(f"Total number of objects: {telsaCollection.count_documents({})}")