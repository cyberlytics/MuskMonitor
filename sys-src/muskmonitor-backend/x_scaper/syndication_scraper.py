import requests
import json
import os

# Configuration
username = "elonmusk"
url = f"https://syndication.twitter.com/srv/timeline-profile/screen-name/{username}"
json_file = "syndication_latest_tweets.json"
cookies_file = "twitter_cookies.json"

def load_cookies(file_path):
    """Load cookies from a JSON file."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                print("Failed to load cookies. Ensure the file is properly formatted.")
                return {}
    else:
        print(f"Cookies file {file_path} not found.")
        return {}

def fetch_tweets(cookies):
    """Fetch tweets from the syndication URL using provided cookies."""
    session = requests.Session()
    session.cookies.update(cookies)
    
    response = session.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch data: {response.status_code}")
        return []
    
    html = response.text
    start_str = '<script id="__NEXT_DATA__" type="application/json">'
    end_str = '</script></body></html>'
    
    try:
        start_index = html.index(start_str) + len(start_str)
        end_index = html.index(end_str, start_index)
        json_str = html[start_index:end_index]
        data = json.loads(json_str)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Failed to parse JSON: {e}")
        return []
    
    entries = data["props"]["pageProps"]["timeline"]["entries"]
    tweets = []
    for i, entry in enumerate(entries, start=1):
        try:
            tweet_content = entry["content"]["tweet"]
            tweet_details = {
                "Tweet_count": i,
                "Username": "Elon Musk",
                "Text": tweet_content["full_text"],
                "Created_At": tweet_content["created_at"],
                "Retweets": tweet_content.get("retweet_count", 0),
                "Likes": tweet_content.get("favorite_count", 0),
            }
            tweets.append(tweet_details)
        except KeyError:
            # Skip invalid entries
            continue
    
    return tweets

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
    # Load session cookies
    cookies = load_cookies(cookies_file)
    print("Cookies loaded: ", cookies)
    if not cookies:
        print("No cookies loaded. Exiting.")
        return

    # Fetch new tweets
    new_tweets = fetch_tweets(cookies)
    if not new_tweets:
        print("No new tweets fetched.")
        return

    # Load existing tweets
    existing_tweets = load_existing_tweets(json_file)
    
    # Create a set of existing tweet timestamps for quick lookup
    existing_timestamps = {tweet["Created_At"] for tweet in existing_tweets}
    
    # Add only new tweets
    unique_tweets = [tweet for tweet in new_tweets if tweet["Created_At"] not in existing_timestamps]
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
