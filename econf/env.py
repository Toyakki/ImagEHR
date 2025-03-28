from dotenv import load_dotenv
from os import environ
from os.path import exists

if not exists(".env"):
	raise Exception(".env file not found! Please create one using .env.example as a reference!")

if not load_dotenv(dotenv_path=".env"):
	raise Exception("failed to parse .env file! Please fill it out using .env.example as a reference!")

def get_env(var: str) -> str:
	if var in environ:
		return environ[var]
	raise Exception(f"WARNING: failed to parse env var '{var}' from .env: did you create and fill it out?")

with open(".env.example", "r") as envex:
	data = envex.read()

lines = [i for i in data.split("\n") if i]
for line in lines:
	var = line.split("=")[0]
	if not get_env(var):
		raise Exception(f"WARNING: failed to parse env var '{var}' from .env: did you create and fill it out?")
