import pandas as pd
import kagglehub
import os
# Funktion zum Speichern eines Datensatzes in einer CSV-Datei
def save_dataset(dataset_path, output_filename):
    # Suche nach der CSV-Datei im Verzeichnis
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            if file.endswith(".csv"):
                csv_path = os.path.join(root, file)
                df = pd.read_csv(csv_path)
                df.to_csv(output_filename, index=False)
                print(f"Dataset saved to {output_filename}")
                return

save_dataset("hf://datasets/hugginglearners/twitter-dataset-tesla/Tesla.csv", "tesla_tweets_hugginglearners.csv")
save_dataset(kagglehub.dataset_download("gpreda/elon-musk-tweets"), "elon-musk-tweets.csv")
save_dataset(kagglehub.dataset_download("marta99/elon-musks-tweets-dataset-2022"), "elon-musks-tweets-dataset-2022.csv")
save_dataset(kagglehub.dataset_download("kingburrito666/elon-musk-tweets"), "elon-musk-tweets-kingburrito666.csv")