from dotenv import load_dotenv
from os import environ

if not load_dotenv():
	raise Exception("failed to parse .env: did you create and fill it out?")

def get_env(var: str) -> str:
	if var in environ:
		return environ[var]
	raise Exception(f"failed to parse env var '{var}' from .env: did you create and fill it out?")

with open(".env.example", "r") as envex:
	data = envex.read()

lines = [i for i in data.split("\n") if i]
for line in lines:
	var = line.split("=")[0]
	if not get_env(var):
		raise Exception(f"failed to parse env var '{var}' from .env: did you create and fill it out?")

if get_env("COHERE_API_KEY") == "your_api_key":
	raise Exception("please replace COHERE_API_KEY in .env with your real API key")
