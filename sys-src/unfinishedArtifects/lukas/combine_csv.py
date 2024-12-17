import pandas as pd

# Funktion zum Vereinheitlichen des Datumsformats
def unify_date_format(df, date_column):
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
    df[date_column] = df[date_column].dt.strftime('%Y-%m-%d')
    return df

# CSV-Dateien laden
df1 = pd.read_csv("elon-musk-tweets-kingburrito666.csv")
df2 = pd.read_csv("elon-musk-tweets.csv")
df3 = pd.read_csv("elon-musks-tweets-dataset-2022.csv")
df4 = pd.read_csv("tesla_tweets_hugginglearners.csv")

# Vereinheitlichung der Spalten und Datumsformate
df1_cleaned = df1.rename(columns={"created_at": "date", "text": "text"})[["date", "text"]]
df1_cleaned = unify_date_format(df1_cleaned, "date")

df2_cleaned = df2.rename(columns={"text": "text", "date": "date"})[["date", "text"]]
df2_cleaned = unify_date_format(df2_cleaned, "date")

df3_cleaned = df3.rename(columns={"Cleaned_Tweets": "text", "Date": "date"})[["date", "text"]]
df3_cleaned = unify_date_format(df3_cleaned, "date")

df4_cleaned = df4.rename(columns={"tweet": "text", "date": "date"})[["date", "text"]]
df4_cleaned = unify_date_format(df4_cleaned, "date")

# Alle DataFrames zusammenführen
combined_df = pd.concat([df1_cleaned, df2_cleaned, df3_cleaned, df4_cleaned], ignore_index=True)

# Duplikate entfernen (basierend auf Text und Datum)
cleaned_df = combined_df.drop_duplicates(subset=["date", "text"]).reset_index(drop=True)

# Spaltenreihenfolge explizit festlegen
cleaned_df = cleaned_df[["date", "text"]]

# Nach Datum absteigend sortieren
cleaned_df['date'] = pd.to_datetime(cleaned_df['date'], errors='coerce')
cleaned_df = cleaned_df.sort_values(by='date', ascending=False)

# Ergebnis anzeigen
print(cleaned_df.shape)
print(cleaned_df.head())

# Gemeinsame Datei speichern
cleaned_df.to_csv("combined_tweets.csv", index=False)