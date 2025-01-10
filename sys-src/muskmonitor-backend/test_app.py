import pytest
from webserver import app
from pymongo import MongoClient
import datetime
from unittest.mock import MagicMock

@pytest.fixture
# Ermöglicht das Senden von HTTP-Anfragen an die Flask-App während der Tests
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mongodb_client():
    yield MongoClient("mongodb://root:root_password@stock-database:27017/")

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
    
    # Überprüfen des Statuscodes
    assert response.status_code == 200
    # Überprüfen, ob die Antwort JSON ist
    assert response.is_json
    # JSON-Daten aus der Antwort laden
    data = response.json

    # Überprüfen, ob die Antwort eine Liste ist und nicht leer ist
    assert isinstance(data, list)
    assert len(data) > 0

    # Prüfung der Struktur und der Typen des ersten Eintrags
    first_entry = data[0]

    assert "Datum" in first_entry
    assert isinstance(first_entry["Datum"], str)
    import datetime
    assert isinstance(datetime.datetime.strptime(first_entry["Datum"], "%Y-%m-%d"), datetime.datetime)

    assert "open" in first_entry
    assert isinstance(first_entry["open"], float)
    assert first_entry["open"] >= 0.0

    assert "high" in first_entry
    assert isinstance(first_entry["high"], float)
    assert first_entry["high"] >= 0.0

    assert "low" in first_entry
    assert isinstance(first_entry["low"], float)
    assert first_entry["low"] >= 0.0

    assert "close" in first_entry
    assert isinstance(first_entry["close"], float)
    assert first_entry["close"] >= 0.0

    assert "volume" in first_entry
    assert isinstance(first_entry["volume"], float)
    assert first_entry["volume"] >= 0

    
def test_get_important_tweets(client):
    response = client.get("/get_important_tweets")
    
    assert response.status_code == 200
    assert response.is_json  # Check if the response claims to be JSON
    assert isinstance(response.json, list)  # Ensure response is a list
    assert len(response.json) > 0  # Ensure the list is not empty

    # Validate structure of the first object in the response
    first_tweet = response.json[0]
    assert "Date" in first_tweet.keys(), "Key 'Date' is missing in the response"
    assert "Text" in first_tweet.keys(), "Key 'Text' is missing in the response"

    # Validate 'Date' field format and type
    assert isinstance(first_tweet["Date"], str), "'Date' field is not a string"
    try:
        datetime.datetime.strptime(first_tweet["Date"], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        pytest.fail(f"'Date' field does not match the format '%Y-%m-%d %H:%M:%S'")

    # Validate 'Text' field type
    assert isinstance(first_tweet["Text"], str), "'Text' field is not a string"

    
def test_analyze_sentiments(client):
    response = client.get("/analyze_sentiments")
    sentiments = ["Negative", "Neutral", "Positive"]

    assert response.status_code == 200
    assert response.is_json
    data = response.json

    assert isinstance(data, list)
    assert len(data) <= 100

    first_entry = data[0]
    
    assert "Date" in first_entry
    assert isinstance(first_entry["Date"], str)
    assert isinstance(datetime.datetime.strptime(first_entry["Date"], "%Y-%m-%d %H:%M"), datetime.datetime)

    assert "Title" in first_entry
    assert isinstance(first_entry["Title"], str)
    assert first_entry["Title"] == "Elon Musk schreibt auf X"

    assert "Class" in first_entry
    assert isinstance(first_entry["Class"], str)
    assert first_entry["Class"] in sentiments

    assert "Text" in first_entry
    assert isinstance(first_entry["Text"], str)

    assert "_id" not in first_entry
     
# def test_start_scraper(client):
#     response = client.get("/start_scraper")

#     assert response.status_code == 200
#     assert response.is_json
#     data = response.json

#     assert "message" in data
#     assert "status" in data
#     status = data["status"]

#     assert "last_run" in status
#     assert "new_tweets" in status

#     assert data["message"] == "Scraper executed manually"
#     assert status["last_run"] == "Ran successfully"
#     assert isinstance(status["new_tweets"], int)
#     assert status["new_tweets"] >= 0
     
def test_scraper_status_endpoint(client):
    response = client.get("/scraper_status")

    assert response.status_code == 200
    assert response.is_json
    data = response.json

    assert "last_run" in data
    assert "new_tweets" in data
    
def test_perform_stock_prediction(monkeypatch):
    # Mock dependencies
    mock_fetch_data_from_db = MagicMock(return_value={
        "Datum": [datetime.datetime(2025, 1, i) for i in range(1, 31)],
        "Close": [i * 10 for i in range(1, 31)]
    })
    mock_prepare_data = MagicMock(return_value=(
        [[1, 2, 3]],  # train_data
        [[4, 5, 6]],  # test_data
        "mock_scaler"  # scaler
    ))
    mock_create_lstm_data = MagicMock(side_effect=lambda data: (["mock_x"], ["mock_y"]))
    mock_train_lstm_model = MagicMock(return_value="mock_model")
    mock_evaluate_and_forecast = MagicMock(return_value=(
        [(datetime.datetime(2025, 1, i), i) for i in range(1, 6)],  # predicted_values_with_dates
        [10, 20, 30, 40, 50],  # actual_values
        0.1,  # rmse
        [(datetime.datetime(2025, 2, i), i * 10) for i in range(1, 6)]  # future_values_with_dates
    ))
    mock_insert_one = MagicMock()

    # Patch functions and database collection
    monkeypatch.setattr("webserver.fetch_data_from_db", mock_fetch_data_from_db)
    monkeypatch.setattr("webserver.prepare_data", mock_prepare_data)
    monkeypatch.setattr("webserver.create_lstm_data", mock_create_lstm_data)
    monkeypatch.setattr("webserver.train_lstm_model", mock_train_lstm_model)
    monkeypatch.setattr("webserver.evaluate_and_forecast", mock_evaluate_and_forecast)
    monkeypatch.setattr("webserver.stock_database", {"predictions": MagicMock(insert_one=mock_insert_one)})

    # Call the function under test
    from webserver import perform_stock_prediction
    perform_stock_prediction()

    # Assertions
    mock_fetch_data_from_db.assert_called_once()
    mock_prepare_data.assert_called_once_with(mock_fetch_data_from_db.return_value)
    mock_create_lstm_data.assert_any_call([[1, 2, 3]])  # train_data
    mock_create_lstm_data.assert_any_call([[4, 5, 6]])  # test_data
    mock_train_lstm_model.assert_called_once_with(["mock_x"], ["mock_y"])
    mock_evaluate_and_forecast.assert_called_once_with(
        "mock_model", ["mock_x"], ["mock_y"], "mock_scaler",
        mock_fetch_data_from_db.return_value["Datum"][-len([[4, 5, 6]]) :],  # test_dates
        future_steps=10
    )
    mock_insert_one.assert_called_once_with({
        "predicted_values": [
            {"date": date.strftime("%Y-%m-%d"), "value": value}
            for date, value in mock_evaluate_and_forecast.return_value[0]
        ],
        "actual_values": mock_evaluate_and_forecast.return_value[1],
        "rmse": mock_evaluate_and_forecast.return_value[2],
        "future_predictions": [
            {"date": date.strftime("%Y-%m-%d"), "value": value}
            for date, value in mock_evaluate_and_forecast.return_value[3]
        ],
    })

def test_mongodb_insert_stock_data(client, mongodb_client):
    temp_db = mongodb_client["temporary_test_database"]
    temp_collection = temp_db["temporary_test_collection"]
    temp_collection.drop()

    date = datetime.datetime.now().strftime("%Y-%m-%d")
    temp_collection.insert_one({
        "Datum": date,
        "open": 100.0,
        "close": 200.0,
        "low": 50.0,
        "high": 300.0,
        "volume": 400
    })

    assert temp_collection.count_documents({}) == 1
    mongodb_client.drop_database("temporary_test_database")
    
def test_mongodb_get_stock_data(client, mongodb_client):
    temp_db = mongodb_client["temporary_test_database"]
    temp_collection = temp_db["temporary_test_collection"]
    temp_collection.drop()

    date = datetime.datetime.now().strftime("%Y-%m-%d")
    temp_collection.insert_one({
        "Datum": date,
        "open": 100.0,
        "close": 200.0,
        "low": 50.0,
        "high": 300.0,
        "volume": 400
    })

    assert temp_collection.count_documents({"Datum": date}) == 1

    for obj in temp_collection.find({"Datum": date}):
        assert "Datum" in obj
        assert "open" in obj
        assert "close" in obj
        assert "low" in obj
        assert "high" in obj
        assert "volume" in obj

        assert obj["Datum"] == date
        assert obj["open"] == 100.0
        assert obj["close"] == 200.0
        assert obj["low"] == 50.0
        assert obj["high"] == 300.0
        assert isinstance(obj["volume"], (int, float))
        assert obj["volume"] == 400

    mongodb_client.drop_database("temporary_test_database")

def test_mongodb_insert_tweet_data(client, mongodb_client):
    temp_db = mongodb_client["temporary_test_database"]
    temp_collection = temp_db["temporary_test_collection"]
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
    temp_collection.drop()

    date = datetime.datetime.now().strftime("%Y-%m-%d")
    text = "Text for testing purposes only"

    temp_collection.insert_one({
        "Datum": date,
        "Text": text
    })

    assert temp_collection.count_documents({"Datum": date}) == 1

    for obj in temp_collection.find({"Datum": date}):
        assert "Datum" in obj
        assert "Text" in obj
        assert obj["Datum"] == date
        assert obj["Text"] == text

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
