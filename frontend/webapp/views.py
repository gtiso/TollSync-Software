import requests
from django.shortcuts import render

FLASK_BACKEND_URL = "http://127.0.0.1:9115"

# Your login credentials
USERNAME = "admin"
PASSWORD = "freepasses4all"

def get_auth_token():
    """Logs in to Flask and retrieves JWT token."""
    login_url = f"{FLASK_BACKEND_URL}/api/login"
    payload = {"username": USERNAME, "password": PASSWORD}

    response = requests.post(login_url, data=payload)

    if response.status_code == 200:
        token = response.json().get("token")
        print(f"Received Token: {token}")  # Debugging output
        return token
    else:
        print(f"Login Failed: {response.json()}")  # Debugging output
        return None

def fetch_data():
    """Fetches healthcheck data using the JWT token."""
    token = get_auth_token()  # First, login to get a token
    
    if not token:
        return {"error": "Authentication failed. No token received."}

    url = f"{FLASK_BACKEND_URL}/api/admin/healthcheck"
    headers = {"X-OBSERVATORY-AUTH": token}  # Use the token in the headers}

    try:
        print(f"Sending request to: {url} with token: {token[:10]}...")  # Debugging output
        response = requests.get(url, headers=headers, timeout=5)
        print(f"Response status: {response.status_code}")

        if response.status_code == 200:
            return response.json()
        return {"error": f"Backend returned {response.status_code}"}
    
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Flask: {e}")
        return {"error": str(e)}

def home(request):
    data = fetch_data()
    return render(request, 'home.html', {"data": data})