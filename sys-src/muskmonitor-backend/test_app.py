import pytest
from webserver import app
from pymongo import MongoClient
import datetime


@pytest.fixture
# Ermöglicht das Senden von HTTP-Anfragen an die Flask-App während der Tests
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mongodb_client():
    yield MongoClient("mongodb://stock-database:27017/")

# Test, ob die Startseite der Anwendung korrekt funktioniert
# -> Erwartet: HTTP-Statuscode 200 und "Hello, World!" im Inhalt
def test_home(client):
    """Test the home route"""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Hello, World!" in response.data


# Test, ob eine nicht existierende Route korrekt behandelt wird
# -> Erwartet: HTTP-Statuscode 404
def test_404(client):
    """Test a non-existent route"""
    response = client.get("/non-existent-route")
    assert response.status_code == 404

def test_get_stock_data(client):
    response = client.get("/get_stock_data")
    
    assert response.status_code == 200
    assert response.is_json
    assert isinstance(response.json, list)
    assert len(response.json) > 0

    assert "Datum" in response.json[0].keys()
    assert isinstance(response.json[0]["Datum"], str)
    assert isinstance(datetime.datetime.strptime(response[0]["Datum"], "%Y-%m-%d"), datetime)

    assert "open" in response.json[0].keys()
    assert isinstance(response.json[0]["open"], float)
    assert response.json[0]["open"] >= 0.0

    assert "high" in response.json[0].keys()
    assert isinstance(response.json[0]["high"], float)
    assert response.json[0]["high"] >= 0.0

    assert "low" in response.json[0].keys()
    assert isinstance(response.json[0]["low"], float)
    assert response.json[0]["low"] >= 0.0

    assert "close" in response.json[0].keys()
    assert isinstance(response.json[0]["close"], float)
    assert response.json[0]["close"] >= 0.0

    assert "volume" in response.json[0].keys()
    assert isinstance(response.json[0]["volume"], int)
    assert response.json[0]["int"] >= 0
    
def test_get_important_tweets(client):
    response = client.get("/get_important_tweets")
    
    assert response.status_code == 200
    assert response.is_json
    assert isinstance(response.json, list)
    assert len(response.json) > 0

    assert "Date" in response.json[0].keys()
    assert isinstance(response.json[0]["Datum"], str)
    assert isinstance(datetime.datetime.strptime(response[0]["Datum"], "%Y-%m-%d %H:%M:%S"), datetime)

    assert "Text" in response.json[0].keys()
    assert isinstance(response.json[0]["Text"], str)
    
def test_analyze_sentiments(client):
    response = client.get("/analyze_sentiments")
    sentiments = ["Negative", "Neutral", "Positive"]
    
    assert response.status_code == 200
    assert response.is_json()
    
    assert isinstance(response.json, list)
    assert len(response.json) == 100
    
    assert "Datum" in response[0].keys()
    assert isinstance(response[0]["Datum"], str)
    assert isinstance(datetime.datetime.strptime(response[0]["Datum"], "%Y-%m-%d %H:%M"), datetime)
    
    assert "Title" in response[0].keys()
    assert isinstance(response[0]["Title"], str)
    assert response[0]["Title"] == "Elon Musk schreibt auf X"
    
    assert "Class" in response[0].keys()
    assert isinstance(response[0]["Class"], str)
    assert response[0]["Class"] in sentiments
    
    assert "Text" in response[0].keys()
    assert isinstance(response[0]["Text"], str)
    
    assert "_id" not in response[0].keys()
     
def test_start_scraper(client):
    response = client.get("/start-scraper")
    
    assert response.status_code == 200
    assert response.is_json()
    assert "message" in response.json.keys()
    assert "status" in response.json.keys()
    assert "last_run" in response.json["status"].keys()
    assert "new_tweets" in response.json["status"].keys()
    assert response.json["message"] == "Scraper executed manually"
    assert response.json["status"]["last_run"] == "Ran successfully"
    assert isinstance(response.json["status"]["new_tweets"], int)
    assert response.json["status"]["new_tweets"] >= 0
     
def test_scraper_status_endpoint(client):
    response = client.get("/scraper-status")
    
    assert response.status_code == 200
    assert response.is_json()
    assert "status" in response.json.keys()
    assert "last_run" in response.json["status"].keys()
    assert "new_tweets" in response.json["status"].keys()
    assert response.json["status"]["last_run"] == "Ran successfully"
    assert isinstance(response.json["status"]["new_tweets"], int)
    assert response.json["status"]["new_tweets"] >= 0
    
def test_stock_prediction(client, monkeypatch):
    response = client.get("/scraper-status")
    
    
    def mock_evaluate_and_plot(model, x_test, y_test, scaler):
        predicted_values = [0, 1, 2, 3, 4]
        actual_values = [1, 2, 3, 4, 5]
        rmse = 0.1
        return [predicted_values, actual_values, rmse]

    monkeypatch.setattr(
        "webserver.evaluate_and_plot", mock_evaluate_and_plot
    )
    
    assert response.status_code == 200
    assert response.is_json()
    assert "predicted_values" in response.json.keys()
    assert "actual_values" in response.json.keys()
    assert "rmse" in response.json.keys()
    
    assert isinstance(response.json["predicted_values"], list)
    assert isinstance(response.json["actual_values"], list)
    assert isinstance(response.json["rmse"], float)
    assert response.json["predicted_values"] == [0, 1, 2, 3, 4]
    assert response.json["actual_values"] == [1, 2, 3, 4, 5]
    assert response.json["rmse"] == 0.1

def test_mongodb_insert_stock_data(client, mongodb_client):
    temp_db = mongodb_client["temporary_test_database"]
    temp_collection = temp_db["temporary_test_collection"]
    # Clear collection to remove artifacts.
    temp_collection.drop()
    
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    temp_collection.insert_one({
        "Datum": date,
        "open": 100,
        "close": 200,
        "low": 50,
        "high": 300,
        "volume": 400
    })

    assert temp_collection.count_documents({}) == 1
    
    mongodb_client.drop_database("temporary_test_database")
    
def test_mongodb_get_stock_data(client, mongodb_client):
    temp_db = mongodb_client["temporary_test_database"]
    temp_collection = temp_db["temporary_test_collection"]
    # Clear collection to remove artifacts.
    temp_collection.drop()
    
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    temp_collection.insert_one({
        "Datum": date,
        "open": 100,
        "close": 200,
        "low": 50,
        "high": 300,
        "volume": 400
    })

    assert temp_collection.count_documents({"Datum": date}) == 1
    
    for object in temp_collection.find({"Datum": date}):
        assert "Datum" in object.keys()
        assert "open" in object.keys()
        assert "close" in object.keys()
        assert "low" in object.keys()
        assert "high" in object.keys()
        assert "low" in object.keys()
        assert object["Datum"] == date
        assert object["open"] == 100
        assert object["close"] == 200
        assert object["low"] == 50
        assert object["high"] == 300
        assert object["volume"] == 400

    day_before_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    day_after_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    
    assert temp_collection.count_documents({"Datum": day_before_date}) == 0
    assert temp_collection.count_documents({"Datum": day_after_date}) == 0
    assert temp_collection.count_documents({"Datum": {"$gte": day_before_date, "$lte": day_after_date}}) == 1
    
    for object in temp_collection.find({"Datum": {"$gte": day_before_date, "$lte": day_after_date}}):
        assert "Datum" in object.keys()
        assert "open" in object.keys()
        assert "close" in object.keys()
        assert "low" in object.keys()
        assert "high" in object.keys()
        assert "low" in object.keys()
        assert object["Datum"] == date
        assert object["open"] == 100
        assert object["close"] == 200
        assert object["low"] == 50
        assert object["high"] == 300
        assert object["volume"] == 400
    mongodb_client.drop_database("temporary_test_database")

def test_mongodb_insert_tweet_data(client, mongodb_client):
    temp_db = mongodb_client["temporary_test_database"]
    temp_collection = temp_db["temporary_test_collection"]
    # Clear collection to remove artifacts.
    temp_collection.drop()
    
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    temp_collection.insert_one({
        "Datum": date,
        "Text": "Text for testing purposes only"
    })

    assert temp_collection.count_documents({}) == 1
    mongodb_client.drop_database("temporary_test_database")
    
def test_mongodb_get_tweet_data(client, mongodb_client):
    temp_db = mongodb_client["temporary_test_database"]
    temp_collection = temp_db["temporary_test_collection"]
    # Clear collection to remove artifacts.
    temp_collection.drop()
    
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    text = "Text for testing purposes only"
    
    temp_collection.insert_one({
        "Datum": date,
        "Text": text
    })

    assert temp_collection.count_documents({"Datum": date}) == 1
    
    for object in temp_collection.find({"Datum": date}):
        assert "Datum" in object.keys()
        assert "Text" in object.keys()
        assert object["Datum"] == date
        assert object["Text"] == text

    day_before_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    day_after_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    
    assert temp_collection.count_documents({"Datum": day_before_date}) == 0
    assert temp_collection.count_documents({"Datum": day_after_date}) == 0
    assert temp_collection.count_documents({"Datum": {"$gte": day_before_date, "$lte": day_after_date}}) == 1
    
    for object in temp_collection.find({"Datum": {"$gte": day_before_date, "$lte": day_after_date}}):
        assert "Datum" in object.keys()
        assert "Text" in object.keys()
        assert object["Datum"] == date
        assert object["Text"] == text
    mongodb_client.drop_database("temporary_test_database")
     
# Test den Endpunkt /get_stock_data ob er die Stock-Daten korrekt zurückgibt
# -> Erwartet: JSon-Daten mit dem Namen "Tesla" und dem Preis 650
# def test_get_stock_data(client, monkeypatch):
#     """Test the /get_stock_data route"""

#     class MockCollection:
#         def find(self, query):
#             return self

#         def sort(self, key):
#             return [{"name": "Tesla", "price": 650}]

#     mock_collection = MockCollection()
#     monkeypatch.setattr("webserver.tesla_stock", mock_collection)

#     response = client.get("/get_stock_data")
#     assert response.status_code == 200
#     assert b'"name": "Tesla"' in response.data
#     assert b'"price": 650' in response.data


# Test den Endpunkt /analyse_sentiments mit gültigen Eingaben
# -> Erwartet: HTTP-Statuscode 200 und Sentiment-Analyseergebnis
# def test_analyze_sentiments_valid(client, monkeypatch):
#     """Test the /analyze_sentiments route with valid input"""

#     def mock_analyse_and_return_json(tweets):
#         return {"positive": 1, "negative": 0, "neutral": 0}

#     monkeypatch.setattr(
#         "webserver.analyse_and_return_json", mock_analyse_and_return_json
#     )

#     data = {"tweets": ["Tesla stock is doing great!"]}
#     response = client.post("/analyze_sentiments", json=data)
#     assert response.status_code == 200
#     assert response.get_json() == {"positive": 1, "negative": 0, "neutral": 0}


# Test den Endpunkt /analyse_sentiments mit ungültigen Eingaben
# -> Erwartet: HTTP-Statuscode 400 und Fehlermeldung "invalid request"
# def test_analyze_sentiments_invalid(client):
#     """Test the /analyze_sentiments route with invalid input"""

#     data = {"invalid_key": "This is not a valid request"}
#     response = client.post("/analyze_sentiments", json=data)
#     assert response.status_code == 400
#     assert b"Invalid request, please provide a list of tweets." in response.data


# # Test den Endpunkt /analyse_sentiments ohne JSON-Payload
# # -> Erwartet: HTTP-Statuscode 400 und Fehlermeldung "invalid request"
# def test_analyze_sentiments_no_json(client):
#     """Test the /analyze_sentiments route with no JSON payload"""

#     response = client.post("/analyze_sentiments")
#     assert response.status_code == 400
#     assert b"Invalid request, please provide a list of tweets." in response.data
