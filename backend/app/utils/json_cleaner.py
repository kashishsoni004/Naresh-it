import re

def clean_json(raw_text):
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    return match.group(0) if match else "{}"