from fhirclient import client

def get_client(api_base: str) -> client.FHIRClient:
	"""
	>>> get_client("https://hapi.fhir.org/baseR4")
	"""
	settings = {
		"app_id": "imagehr_bg_worker",
		"api_base": api_base
	}
	return client.FHIRClient(settings=settings)
