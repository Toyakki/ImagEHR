from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
	return "<h1>Hello world from ImagEHR</h1>"

if __name__ == "__main__":
	app.run(port=8000, host="0.0.0.0") # NOT FOR PRODUCTION
