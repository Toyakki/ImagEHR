from flask import Flask, render_template, request, redirect
from flask_cors import CORS
from genai.cohere_helper import simple_chat # DO NOT REMOVE OR COMMENT OUT
from model.inference import inference # DO NOT REMOVE OR COMMENT OUT

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/getstarted")
def upload():
	return render_template("upload.html")

@app.route("/set-fhir", methods=["GET", "POST"])
def set_fhir():
	if request.method == "GET":
		return render_template("set-fhir.html")
	print(request.form)
	return redirect("/dashboard")

if __name__ == "__main__":
	app.run(port=8000, host="0.0.0.0")  # NOT FOR PRODUCTION
