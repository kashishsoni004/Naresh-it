from app.services.groq_service import client
from app.services.search_service import search_google
from app.utils.json_cleaner import clean_json

def generate_trainer(name, role):

    google_data = search_google(f"{name} {role} trainer profile skills experience")

    if not google_data:
        google_data = f"{name} is a professional {role} trainer."

    prompt = f"""
Generate a trainer profile.

Trainer: {name}
Role: {role}

Use this data:
{google_data}

STRICT RULES:
- Return ONLY valid JSON

FORMAT:
{{
  "about": "string",
  "courses": "string",
  "style": "string",
  "tags": ["string"],
  "why": "string"
}}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Return only JSON"},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    raw = response.choices[0].message.content

    return clean_json(raw)