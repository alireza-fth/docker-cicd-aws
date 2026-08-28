from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "Docker CI/CD AWS Pipeline V2 is working!"


@app.route("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)