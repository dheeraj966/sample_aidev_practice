import requests

API_KEY = "AIzaSyCxdyk3RVWjnsAX__HuVLWVfoW1Bz2QtnE"
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