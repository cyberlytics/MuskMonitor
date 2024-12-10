import pytest
from webserver import app


@pytest.fixture
# Ermöglicht das Senden von HTTP-Anfragen an die Flask-App während der Tests
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


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


# Test den Endpunkt /get_stock_data ob er die Stock-Daten korrekt zurückgibt
# -> Erwartet: JSon-Daten mit dem Namen "Tesla" und dem Preis 650
def test_get_stock_data(client, monkeypatch):
    """Test the /get_stock_data route"""

    class MockCollection:
        def find(self, query):
            return self

        def sort(self, key):
            return [{"name": "Tesla", "price": 650}]

    mock_collection = MockCollection()
    monkeypatch.setattr("webserver.tesla_stock", mock_collection)

    response = client.get("/get_stock_data")
    assert response.status_code == 200
    assert b'"name": "Tesla"' in response.data
    assert b'"price": 650' in response.data


# Test den Endpunkt /analyse_sentiments mit gültigen Eingaben
# -> Erwartet: HTTP-Statuscode 200 und Sentiment-Analyseergebnis
def test_analyze_sentiments_valid(client, monkeypatch):
    """Test the /analyze_sentiments route with valid input"""

    def mock_analyse_and_return_json(tweets):
        return {"positive": 1, "negative": 0, "neutral": 0}

    monkeypatch.setattr(
        "webserver.analyse_and_return_json", mock_analyse_and_return_json
    )

    data = {"tweets": ["Tesla stock is doing great!"]}
    response = client.post("/analyze_sentiments", json=data)
    assert response.status_code == 200
    assert response.get_json() == {"positive": 1, "negative": 0, "neutral": 0}


# Test den Endpunkt /analyse_sentiments mit ungültigen Eingaben
# -> Erwartet: HTTP-Statuscode 400 und Fehlermeldung "invalid request"
def test_analyze_sentiments_invalid(client):
    """Test the /analyze_sentiments route with invalid input"""

    data = {"invalid_key": "This is not a valid request"}
    response = client.post("/analyze_sentiments", json=data)
    assert response.status_code == 400
    assert b"Invalid request, please provide a list of tweets." in response.data


# Test den Endpunkt /analyse_sentiments ohne JSON-Payload
# -> Erwartet: HTTP-Statuscode 400 und Fehlermeldung "invalid request"
def test_analyze_sentiments_no_json(client):
    """Test the /analyze_sentiments route with no JSON payload"""

    response = client.post("/analyze_sentiments")
    assert response.status_code == 400
    assert b"Invalid request, please provide a list of tweets." in response.data
