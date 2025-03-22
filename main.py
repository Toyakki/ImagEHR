from flask import Flask, render_template, request, redirect
from flask_cors import CORS
from fhir import get_all_patient_ids
from genai.cohere_helper import simple_chat # DO NOT REMOVE OR COMMENT OUT
from model.inference import inference # DO NOT REMOVE OR COMMENT OUT

app = Flask(__name__)
CORS(app)
fhir_api_base: str = ""

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/getstarted")
def upload():
	return render_template("upload.html")

@app.route("/set-fhir", methods=["GET", "POST"])
def set_fhir():
	global fhir_api_base
	if request.method == "GET":
		return render_template("set-fhir.html")
	if "fhir" not in request.form or not request.form["fhir"]:
		return render_template("error.html", message="Please enter a value for FHIR API endpoint."), 400
	fhir_ = request.form["fhir"]
	try:
		patient_ids = get_all_patient_ids(fhir_)
		if not patient_ids:
			raise Exception
	except:
		return render_template("error.html", message="Failed to get patient IDs from FHIR. Invalid URL?"), 400
	fhir_api_base = fhir_
	return redirect("/dashboard")

if __name__ == "__main__":
	app.run(port=8000, host="0.0.0.0")  # NOT FOR PRODUCTION
