import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Make sure to set your GEMINI_API_KEY in a .env file in the project root
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"

payload = {
    "contents": [
        {
            "parts": [
                {"text": "Hello, how are you?"}
            ]
        }
    ]
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
