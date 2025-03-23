from fhirclient.client import FHIRClient
from fhirclient.models.patient import Patient
from requests import get
from json import dumps

def get_all_patient_ids(api_base: str) -> list[str]:
	"""
	>>> get_all_patient_ids("https://r4.smarthealthit.org")
	"""
	settings = {
		"app_id": "imagehr_bg_worker",
		"api_base": api_base
	}
	client = FHIRClient(settings=settings)
	search = Patient.where(struct={})
	patients = search.perform_resources(client.server)
	patient_ids = [patient.id for patient in patients]
	return patient_ids

def get_patient(api_base: str, patient_id: str) -> Patient:
	settings = {
		"app_id": "imagehr_bg_worker",
		"api_base": api_base
	}
	client = FHIRClient(settings=settings)
	patient = Patient.read(patient_id, client.server)
	return patient

def get_all_patient_info(api_base: str, patient_id: str) -> str:
	"""
	>>> get_all_patient_info("https://r4.smarthealthit.org", "bc6c8e2a-63de-4790-94af-fcab57874c21")
	"""
	try:
		res = get(f"{api_base}/Patient/{patient_id}/$everything?_format=json&_pretty=true")
		if res.status_code != 200:
			raise Exception(f"not ok status code: {res.status_code}")
		return res.text
	except Exception as e:
		print(f"[ERROR] an error occured in get_all_patient_info:", e)
		return ""
