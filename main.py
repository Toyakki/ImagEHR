from flask import Flask, render_template, stream_template, request, redirect
from werkzeug.utils import secure_filename
from flask_cors import CORS
from fhir import get_all_patient_ids, get_patient, get_all_patient_info
from genai.cohere_helper import simple_chat # DO NOT REMOVE OR COMMENT OUT
from genai.prompt import generate_cdisc
from model.inference import images_dir, labels_dir # DO NOT REMOVE OR COMMENT OUT
from json import loads, dumps
from base64 import b64encode
from os.path import join, abspath, dirname
from hashlib import sha3_224
import os
import shutil

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = join(dirname(abspath(__file__)), "upload")
CORS(app)
fhir_api_base: str = ""

@app.route("/")
def index():
	return render_template("index.html")

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

@app.route("/dashboard")
def dashboard():
	if not fhir_api_base:
		return redirect("/set-fhir")
	return stream_template("dashboard.html", fhir=fhir_api_base)

@app.route("/patients")
def patients():
	if not fhir_api_base:
		return redirect("/set-fhir")
	try:
		ids = get_all_patient_ids(fhir_api_base)
	except:
		return render_template("error.html", message="Failed to fetch patient IDs through FHIR!")

	return stream_template("patients.html",
		fhir=fhir_api_base,
		ids=ids,
		gp=get_patient,
		api_base=fhir_api_base,
		loads=loads,
		dumps=dumps,
		b64encode=b64encode
	)

def sha_str(inp: str) -> str:
	return sha3_224(inp.encode()).hexdigest()

@app.route("/patient/<patient_id>")
def patient(patient_id: str):
	if not fhir_api_base:
		return redirect("/set-fhir")
	try:
		info = get_all_patient_info(fhir_api_base, patient_id)
		if not info:
			raise Exception
		prefix = sha_str(patient_id)
		files = [f for f in os.listdir(app.config["UPLOAD_FOLDER"]) if f.startswith(prefix)]
		return stream_template("patient.html",
			patient_id=patient_id,
			patient=get_patient(fhir_api_base, patient_id),
			info=info,
			dumps=dumps,
			b64encode=b64encode,
			simple_chat=simple_chat,
			files=files,
			prefix=prefix,
		)
	except Exception as e:
		print(e)
		return render_template("error.html", message="Failed to fetch patient info!")

@app.route("/upload/to/<patient_id>", methods=["POST"])
def upload_to(patient_id: str):
	if not fhir_api_base:
		return redirect("/set-fhir")
	if "file" not in request.files:
		return render_template("error.html", message="No file specified!")
	file = request.files["file"]
	if file.filename == "":
		return render_template("error.html", message="No file specified!")
	filename = secure_filename(file.filename)
	file.save(join(app.config["UPLOAD_FOLDER"], f"{sha_str(patient_id)}{filename}"))
	return redirect(f"/patient/{patient_id}")

@app.route("/cdisc/<patient_id>")
def cdisc(patient_id: str):
	if not fhir_api_base:
		return redirect("/set-fhir")
	try:
		info = get_all_patient_info(fhir_api_base, patient_id)
		if not info:
			raise Exception

		prefix = sha_str(patient_id)
		files = [f for f in os.listdir(app.config["UPLOAD_FOLDER"]) if f.startswith(prefix)]

		os.makedirs(images_dir, exist_ok=True)
		for filename in os.listdir(images_dir):
			file_path = os.path.join(images_dir, filename)
			if os.path.isfile(file_path):
				os.remove(file_path)

		os.makedirs(labels_dir, exist_ok=True)
		for filename in os.listdir(labels_dir):
			file_path = os.path.join(labels_dir, filename)
			if os.path.isfile(file_path):
				os.remove(file_path)

		for filename in os.listdir(os.path.dirname(labels_dir)):
			file_path = os.path.join(os.path.dirname(labels_dir), filename)
			if os.path.isfile(file_path):
				os.remove(file_path)

		upload_folder = app.config["UPLOAD_FOLDER"]
		for filename in files:
			src_path = os.path.join(upload_folder, filename)
			dst_path = os.path.join(images_dir, filename)
			shutil.copy(src_path, dst_path)

		return generate_cdisc(fhir_api_base, patient_id)
	except Exception as e:
		print(e)
		return render_template("error.html", message="Failed to create CDISC export!")

if __name__ == "__main__":
	app.run(port=8000, host="0.0.0.0")  # NOT FOR PRODUCTION
