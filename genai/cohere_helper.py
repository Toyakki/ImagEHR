from cohere import ClientV2
from config.env import get_env

client = ClientV2(get_env("COHERE_API_KEY"))

def simple_chat(message: str) -> str:
	"""
	Do a simple single-turn chat with Cohere.
	Returns a string containing the LLM's response if successful.
	If any error occurs, this function returns an empty string.

	>>> response = simple_chat("What colour is the sky?")
	>>> print(response) # "The colour of the sky is blue."
	"""
	try:
		response = client.chat(
			model="command-a-03-2025",
			messages=[
				{"role": "user", "content": message}
			]
		)
		if not response.message.content:
			raise Exception("empty response messages from cohere")
		if not response.message.content[0].text:
			raise Exception("empty response string from cohere")
		return response.message.content[0].text
	except Exception as e:
		print(f"simple_chat error: {e}")
		return ""


def self_test():
	response = simple_chat("What is 7 + 4? Answer in one word only.")
	assert "eleven" in response.lower()

self_test()
