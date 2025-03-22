from fhirclient import client

def get_client(api_base: str) -> client.FHIRClient:
	settings = {
		"app_id": "imagehr_bg_worker",
		"api_base": api_base
	}
	return client.FHIRClient(settings=settings)
