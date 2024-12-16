from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig
from scipy.special import softmax
import numpy as np
import json

class_mapping = {0: "Negative", 1: "Neutral", 2: "Positive"}


# Preprocess text (username and link placeholders)
def preprocess(text):
    new_text = []
    for t in text.split(" "):
        t = "@user" if t.startswith("@") and len(t) > 1 else t
        t = "http" if t.startswith("http") else t
        new_text.append(t)
    return " ".join(new_text)


def analyse_sentiment(text):
    processed_text = preprocess(text)
    encoeded_input = tokenizer(
        processed_text, return_tensors="pt", truncation=True, padding=True
    )
    output = model(**encoeded_input)
    scores = output[0].detach().numpy()
    scores = softmax(scores, axis=1)
    sentiment_class = np.argmax(scores)
    return class_mapping[sentiment_class]


def analyse_sentiment_list(text_list):
    results = []
    for text in text_list:
        sentiment = analyse_sentiment(text)
        results.append({"text": text, "sentiment": sentiment})
    return results


MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
config = AutoConfig.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)
# model.save_pretrained(MODEL)


def analyse_and_return_json(input_texts):
    sentiments = analyse_sentiment_list(input_texts)
    return sentiments
    #return json.dumps(sentiments, indent=4)
