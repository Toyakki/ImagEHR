from cohere import ClientV2
from econf.env import get_env
import os

_client = ClientV2(get_env("COHERE_API_KEY"))

def refresh_cohere_client():
	global _client
	_client = ClientV2(os.environ["COHERE_API_KEY"])

def simple_chat(message: str, model: str = "command-a-03-2025") -> str:
	"""
	Do a simple single-turn chat with Cohere.
	Returns a string containing the LLM's response if successful.
	If any error occurs, this function returns an empty string.

	>>> response = simple_chat("What colour is the sky?")
	>>> print(response) # "The colour of the sky is blue."
	"""
	try:
		response = _client.chat(
			model=model,
			messages=[
				{"role": "user", "content": message}
			],
		)
		if not response: raise Exception("cohere response is falsy")
		if not response.message: raise Exception("cohere response.message is falsy")
		if not response.message.content: raise Exception("cohere response.message.content is empty")
		if not response.message.content[0]: raise Exception("cohere response content is falsy")
		if not response.message.content[0].text: raise Exception("cohere response text is empty")
		return response.message.content[0].text
	except Exception as e:
		print(f"[ERROR] an error occured in genai.cohere_helper.simple_chat:", e)
		return ""

def _self_test():
	response = simple_chat("What is 7 + 4? Answer with one English word only.")
	if "eleven" not in response.lower():
		print("WARNING: _self_test failed, MISSING API KEY!!!")

_self_test()
