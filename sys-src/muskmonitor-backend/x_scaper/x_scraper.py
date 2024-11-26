from ntscraper import Nitter
from pprint import pprint
import json

# Scraper initialisieren
scraper = Nitter(log_level=1, skip_instance_check=False)

# Tweets abrufen
tweets = scraper.get_tweets('elonmusk', mode='user', number=-1)

# Tweets ausgeben
#pprint(tweets)

# Tweets in einer JSON-Datei speichern
with open('tweets.json', 'w') as f:
    json.dump(tweets, f, indent=4)

print("Tweets wurden erfolgreich in tweets.json gespeichert.")