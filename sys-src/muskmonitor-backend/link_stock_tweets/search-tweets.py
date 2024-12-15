import json
import os
import pandas as pd

# JSON-Daten der Kursänderungen einlesen
with open('large_differences.json', 'r') as file:
    large_differences = json.load(file)

# Liste der relevanten Daten extrahieren
relevant_dates = {entry['Datum'] for entry in large_differences}

# Funktion, um relevante Tweets zu finden und in ein einheitliches Format zu bringen
def find_relevant_tweets(tweet_files, relevant_dates, filter_username=False):
    relevant_tweets = []

    for tweet_file in tweet_files:
        df = pd.read_csv(tweet_file)
        
        # Überprüfen, welche Spalten vorhanden sind und die entsprechende Spalte für das Datum verwenden
        if 'date' in df.columns:
            date_column = 'date'
        elif 'created_at' in df.columns:
            date_column = 'created_at'
        elif 'Date' in df.columns:
            date_column = 'Date'
        else:
            continue

        # Tweets filtern, die an relevanten Daten gesendet wurden
        filtered_tweets = df[df[date_column].str[:10].isin(relevant_dates)]
        
        for _, row in filtered_tweets.iterrows():
            text_column = 'text' if 'text' in row else 'tweet' if 'tweet' in row else None
            if text_column is None:
                continue

            # Nur Tweets von "elonmusk" berücksichtigen, wenn filter_username True ist
            if filter_username:
                if 'username' in row and row['username'].lower() != 'elonmusk':
                    continue

            tweet = {
                'Date': row[date_column],
                'Text': row[text_column],
            }
            relevant_tweets.append(tweet)

    return relevant_tweets

# Listen von CSV-Dateien einlesen
tweet_files_list1 = [os.path.join('tweets_list1', file) for file in os.listdir('tweets_list1') if file.endswith('.csv')]
tweet_files_list2 = [os.path.join('tweets_list2', file) for file in os.listdir('tweets_list2') if file.endswith('.csv')]

# Relevante Tweets finden
relevant_tweets_list1 = find_relevant_tweets(tweet_files_list1, relevant_dates)
relevant_tweets_list2 = find_relevant_tweets(tweet_files_list2, relevant_dates, filter_username=True)

# Alle relevanten Tweets kombinieren
all_relevant_tweets = relevant_tweets_list1 + relevant_tweets_list2

# Ergebnis in eine JSON-Datei schreiben
with open('relevant_tweets.json', 'w') as outfile:
    json.dump(all_relevant_tweets, outfile, indent=4)

print('Ergebnis wurde in relevant_tweets.json gespeichert.')