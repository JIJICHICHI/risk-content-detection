import requests

url = "http://localhost:5000/audio_fraud_analysis"
files = {
    "audio": open("ai-audio.mp3", "rb")
}

response = requests.post(url, files=files)
print(response.json())
