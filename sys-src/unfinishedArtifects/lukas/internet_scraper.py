import time
from datetime import datetime
import json
from configparser import ConfigParser
from random import randint
from twikit import Client, TooManyRequests

# Konfiguration
QUERY = '(from:elonmusk) lang:en until:2024-11-23 since:2018-01-01'
MINIMUM_TWEETS = 35000
OUTPUT_FILE = 'tweets_latest.json'

# Vorhandene Tweets aus der JSON-Datei laden
try:
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as file:
        all_tweets = json.load(file)
except FileNotFoundError:
    all_tweets = []

# Anmeldedaten laden
config = ConfigParser()
config.read('config.ini')
username = config['X']['username']
email = config['X']['email']
password = config['X']['password']

# Twikit-Client initialisieren
client = Client(language='en-US')
client.login(auth_info_1=username, auth_info_2=email, password=password)
client.save_cookies('cookies.json')


# Funktion, um Tweets zu holen
async def fetch_tweets():
    tweet_count = 0
    tweets = None  # Erstabfrage
    all_tweets = []  # Sammlung aller Tweets
    while True:
        try:
            if tweets is None:
                print(f'{datetime.now()} - Initialisiere Tweet-Suche...')
                tweets = await client.search_tweet(QUERY, product='Top', count=10)
            else:
                wait_time = randint(10, 20)
                print(f'{datetime.now()} - Warte {wait_time} Sekunden für nächste Tweets...')
                time.sleep(wait_time)
                tweets = await tweets.next()

        except TooManyRequests as e:
            # Wenn Rate-Limit erreicht wird
            reset_time = datetime.fromtimestamp(e.rate_limit_reset)
            print(f'{datetime.now()} - Rate-Limit erreicht. Warte bis {reset_time}')
            wait_time = (reset_time - datetime.now()).total_seconds()
            time.sleep(max(wait_time, 1))
            continue
        except StopIteration:
            print(f'{datetime.now()} - Keine weiteren Tweets gefunden.')
            break

        if not tweets:
            print(f'{datetime.now()} - Keine Tweets gefunden.')
            break

        # Tweets in der Sammlung speichern
        for tweet in tweets:
            tweet_count += 1
            tweet_data = {
                "Tweet_count": tweet_count,
                "Username": tweet.user.name,
                "Text": tweet.text,
                "Created_At": tweet.created_at.format(),
                "Retweets": tweet.retweet_count,
                "Likes": tweet.favorite_count,
            }
            all_tweets.append(tweet_data)

        print(f'{datetime.now()} - {tweet_count} Tweets verarbeitet.')

        # Zwischenspeichern in der JSON-Datei
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as file:
            json.dump(all_tweets, file, ensure_ascii=False, indent=4)

        # Abbruchbedingung
        if tweet_count >= MINIMUM_TWEETS:
            print(f'{datetime.now()} - Mindestanzahl von {MINIMUM_TWEETS} Tweets erreicht.')
            break

    print(f'{datetime.now()} - Fertig! Insgesamt {tweet_count} Tweets gespeichert.')

# Hauptprogramm ausführen
import asyncio
asyncio.run(fetch_tweets())
