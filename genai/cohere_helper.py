from cohere import ClientV2
from config.env import get_env

client = ClientV2(get_env("COHERE_API_KEY"))

def self_test():
	response = client.chat(
		model="command-a-03-2025",
		messages=[
			{"role": "user", "content": "Repeat after me: 'banana'"}
		]
	)

	print(response)
	print(response.message.content)

self_test()
