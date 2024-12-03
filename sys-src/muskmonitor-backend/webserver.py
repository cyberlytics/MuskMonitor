# flask python package 
from flask import Flask, request
from flask_weaviate import FlaskWeaviate
import logging
import json

logger = logging.getLogger('Backend')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

app = Flask(__name__)  # Flask-Anwendungsobjekt erstellen und benennen
app.config["WEAVIATE_URL"] = "http://database:8080"
weaviate = FlaskWeaviate(app)

@app.route('/')
def home():
    c = weaviate.client
    c.connect()
    logger.info(c.is_connected())
    logger.info(c.get_meta())
    c.close()
    return 'Hello, World!'

@app.route("/get_stock_data", methods=["GET", "POST"])
def test():
    
    return json.dumps()

if __name__ == '__main__':
    # Starte die Flask-Anwendung im Debug-Modus
    app.run(debug=True)