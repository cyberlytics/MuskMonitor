import pytest
from unittest.mock import patch, mock_open
import requests
from bs4 import BeautifulSoup
import json
from x_scraper.nitter_scraper import fetch_tweets_from_nitter, load_existing_tweets, save_tweets

# Mock configuration
MOCK_USERNAME = "elonmusk"
MOCK_BASE_URL = f"https://nitter.privacydev.net/{MOCK_USERNAME}/with_replies"


def test_fetch_tweets_from_nitter_success():
    """Test the fetch_tweets_from_nitter function with mocked HTML response."""
    mock_html = """
    <div class="timeline-item">
        <a class="tweet-link" href="/elonmusk/status/1234567890123456789#m"></a>
        <div class="tweet-content">This is a mock tweet!</div>
        <span class="tweet-date">
            <a title="2025-01-01 10:00:00">Jan 1</a>
        </span>
        <div class="tweet-stats">
            <span class="icon-retweet"></span>
            <span>1,234</span>
            <span class="icon-heart"></span>
            <span>5</span>
        </div>
    </div>
    """

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = mock_html

        tweets = fetch_tweets_from_nitter()
        assert len(tweets) == 1
        assert tweets[0]["Tweet_ID"] == "1234567890123456789"
        assert tweets[0]["Text"] == "This is a mock tweet!"
        assert tweets[0]["Created_At"] == "2025-01-01 10:00:00"
        assert tweets[0]["Retweets"] == 12345

def test_fetch_tweets_from_nitter_invalid_html():
    """Test the fetch_tweets_from_nitter function with invalid/malformed HTML."""
    mock_html = "<html><body><div>Malformed HTML</div></body></html>"

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = mock_html

        tweets = fetch_tweets_from_nitter()
        assert tweets == []  # Should handle gracefully and return an empty list.


def test_load_existing_tweets():
    """Test the load_existing_tweets function."""
    mock_file_path = "mock_tweets.json"
    mock_data = [{"Tweet_ID": "12345", "Text": "Mock tweet"}]

    # Mock file exists and contains valid JSON
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
        with patch("os.path.exists", return_value=True):
            tweets = load_existing_tweets(mock_file_path)
            assert tweets == mock_data

    # Mock file does not exist
    with patch("os.path.exists", return_value=False):
        tweets = load_existing_tweets(mock_file_path)
        assert tweets == []

    # Mock file contains invalid JSON
    with patch("builtins.open", mock_open(read_data="invalid json")):
        with patch("os.path.exists", return_value=True):
            tweets = load_existing_tweets(mock_file_path)
            assert tweets == []
