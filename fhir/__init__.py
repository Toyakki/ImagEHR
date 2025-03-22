from fhirclient.client import FHIRClient
from fhirclient.models.patient import Patient

def get_client(api_base: str) -> FHIRClient:
	"""
	>>> get_client("https://hapi.fhir.org/baseR4")
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
