from flask import Flask, render_template
from flask_cors import CORS
# from genai.cohere_helper import simple_chat

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(port=8000, host="0.0.0.0")  # NOT FOR PRODUCTION
