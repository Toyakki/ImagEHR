from fhirclient.client import FHIRClient
from fhirclient.models.patient import Patient
from fhirclient.models.adverseevent import AdverseEvent

def get_client(api_base: str) -> FHIRClient:
	"""
	>>> get_client("https://r4.smarthealthit.org")
	"""
	settings = {
		"app_id": "imagehr_bg_worker",
		"api_base": api_base
	}
	return FHIRClient(settings=settings)

def get_all_patient_ids(cli: FHIRClient) -> set[str]:
	search = Patient.where(struct={})
	patients = search.perform_resources(cli.server)
	patient_ids = [patient.id for patient in patients]
	return set(patient_ids)

def get_all_patient_info_as_json(cli: FHIRClient, patient_id: str) -> str:
	info: str = ""

	# AdverseEvent
	search = AdverseEvent.where(struct={"subject": f"Patient/{patient_id}"})
	for event in search.perform_resources(cli.server):
		info += event.as_json()
