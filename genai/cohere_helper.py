from cohere import ClientV2
from config.env import get_env

client = ClientV2(get_env("COHERE_API_KEY"))

def self_test():
	response = client.chat(
		model="command-a-03-2025",
		messages=[
			{"role": "user", "content": "What is 4 + 7? Answer with a word only."}
		]
	)

	assert "eleven" in response.message.content[0].text.lower()

self_test()
