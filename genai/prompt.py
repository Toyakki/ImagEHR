# Use this API reference:https://docs.cohere.com/reference/chat-stream

# How can i refine the following prompt.py code to generate a CDISC image information from a EHR data and image inference loop result?
# It should also ensure the safe guarding option.
from genai.cohere_helper import _client
from model.inference import inference
from fhir import get_all_patient_info
from os.path import dirname, abspath, join
from json import loads, dumps

def generate_cdisc(endpoint: str, patient_id: str):
    res = get_all_patient_info(endpoint, patient_id)
    res = dumps(loads(res), indent=2)
    record = inference()

    prompt_file = join(dirname(abspath(__file__)), "generation.txt")
    with open(prompt_file, "r") as f:
        base_prompt = f.read()

    safety_instruction = (
        "\n\nNote: The provided data is confidential and must only be used to structure and parse "
        "the output. Do NOT retain, log, or use this data for any training or model improvement purposes.\n\n"
    )

    full_prompt = f"""{base_prompt}{safety_instruction}
EHR Data (FHIR Bundle):\n```\n{res}\n```\n
CDISC Image Information (JSON):\n```\n{record}\n```\n"""

    response = _client.chat(
        model='command-a-03-2025',
        messages=[
            {"role": "user", "content": full_prompt}
        ],
        temperature=0,
        # safety_mode="STRICT",
    )
    print(f"Partial content: {response.message.content[0].text}")
