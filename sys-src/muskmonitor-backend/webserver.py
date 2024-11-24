# flask python package 
from flask import Flask, render_template
from flask_weaviate import FlaskWeaviate
import logging

logger = logging.getLogger('Backend')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

app = Flask(__name__)
app.config["WEAVIATE_URL"] = "http://database:8080"
weaviate = FlaskWeaviate(app)

@app.route("/")
def index():
    c = weaviate.client
    c.connect()
    logger.info(c.is_connected())
    logger.info(c.get_meta())
    c.close()
    return "Hello World"

if __name__ == "__main__":
    logger.info(__name__)
    app.run(host="0.0.0.0")