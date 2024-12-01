import pytest
from webserver import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home(client):
    """Test the home route"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Hello, World!" in response.data

def test_404(client):
    """Test a non-existent route"""
    response = client.get('/non-existent-route')
    assert response.status_code == 404
