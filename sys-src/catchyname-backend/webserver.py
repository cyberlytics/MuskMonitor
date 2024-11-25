from flask import Flask
app = Flask(__name__)  # Flask-Anwendungsobjekt erstellen und benennen


@app.route('/')
def home():
    return 'Hello, World!'


if __name__ == '__main__':
    # Starte die Flask-Anwendung im Debug-Modus
    app.run(debug=True)
