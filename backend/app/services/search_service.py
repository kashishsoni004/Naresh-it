import requests
import os
from dotenv import load_dotenv

load_dotenv()

SERP_API_KEY = os.getenv("SERP_API_KEY")

def search_google(query):
    try:
        url = "https://serpapi.com/search"

        params = {
            "q": query,
            "api_key": SERP_API_KEY,
            "num": 5
        }

        res = requests.get(url, params=params)
        data = res.json()

        results = []

        for r in data.get("organic_results", []):
            title = r.get("title", "")
            snippet = r.get("snippet", "")
            results.append(f"{title}: {snippet}")

        return "\n".join(results)

    except Exception as e:
        print("Search Error:", e)
        return ""