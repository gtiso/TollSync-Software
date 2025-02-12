import requests
from django.shortcuts import render

FLASK_BACKEND_URL = "http://127.0.0.1:9115"  # Flask backend port

def fetch_data():
    try:
        url = f"{FLASK_BACKEND_URL}/admin/healthcheck"  # Confirm this matches Flask!
        print(f"Sending request to Flask: {url}")  # Debugging output

        headers = {"X-OBSERVATORY-AUTH": "your_token"}
        response = requests.get(url, headers=headers, timeout=5)
        print(f"Response status: {response.status_code}")  # Debugging output

        if response.status_code == 200:
            return response.json()
        return {"error": f"Backend returned {response.status_code}"}
    
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Flask: {e}")
        return {"error": str(e)}

def home(request):
    data = fetch_data()
    return render(request, 'home.html', {"data": data})