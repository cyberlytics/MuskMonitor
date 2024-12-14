import requests
from bs4 import BeautifulSoup
import json
import os

# Configuration
username = "elonmusk"
base_url = f"https://nitter.privacydev.net/{username}/with_replies"
json_file = "nitter_latest_tweets.json"

import time

def fetch_tweets_from_nitter():
    """Fetch tweets from the specified Nitter instance."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        time.sleep(4)  # Add delay to avoid being flagged as a bot
        response = requests.get(base_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        tweets = []

        for i, tweet_div in enumerate(soup.find_all("div", class_="timeline-item"), start=1):
            #print(i)
            try:
                tweet_id = tweet_div.find("a", class_="tweet-link").get("href").split("/")[-1].split("#")[0]

                tweet_content = tweet_div.find("div", class_="tweet-content")
                tweet_text = tweet_content.get_text(strip=True)

                tweet_meta = tweet_div.find("span", class_="tweet-date")
                created_at = tweet_meta.find("a").get("title")

                stats = tweet_div.find("div", class_="tweet-stats")
                retweet_stat = stats.find("span", class_="icon-retweet").parent.get_text(strip=True)
                retweets = int(retweet_stat.replace(",", ""))
                like_stat = stats.find("span", class_="icon-heart").parent.get_text(strip=True)
                likes = int(like_stat.replace(",", ""))    

                tweet_details = {
                "Tweet_count": i,
                "Tweet_ID": tweet_id,
                "Username": username,
                "Text": tweet_text,
                "Created_At": created_at,
                "Retweets": retweets,
                "Likes": likes,
                }

                tweets.append(tweet_details)
            except (AttributeError, ValueError):
                # Skip invalid entries or malformed tweet data
                continue

        return tweets

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return []


def load_existing_tweets(file_path):
    """Load existing tweets from the JSON file."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                print("Failed to load existing tweets. Starting fresh.")
                return []
    else:
        return []


def save_tweets(file_path, tweets):
    """Save tweets to the JSON file."""
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(tweets, file, indent=4)


def main():
    # Fetch tweets from Nitter
    new_tweets = fetch_tweets_from_nitter()
    if not new_tweets:
        print("No new tweets fetched.")
        return

    # Load existing tweets
    existing_tweets = load_existing_tweets(json_file)

    # Create a set of existing tweet IDs for quick lookup
    existing_ids = {tweet["Tweet_ID"] for tweet in existing_tweets}

    # Add only new tweets
    unique_tweets = [tweet for tweet in new_tweets if tweet["Tweet_ID"] not in existing_ids]

    if unique_tweets:
        print(f"Adding {len(unique_tweets)} new tweets.")
        updated_tweets = unique_tweets + existing_tweets
        # Reassign tweet counts for all tweets
        for i, tweet in enumerate(updated_tweets, start=1):
            tweet["Tweet_count"] = i
        save_tweets(json_file, updated_tweets)
    else:
        print("No new tweets to add.")


if __name__ == "__main__":
    main()
