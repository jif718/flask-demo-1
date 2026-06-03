from flask import Flask
from metrics import init_metrics

app = Flask(__name__)
init_metrics(app)


@app.route("/")
def hello():
    return "Hello from Flask Demo v1.23\n"


@app.route("/health")
def health():
    return "ok\n"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
