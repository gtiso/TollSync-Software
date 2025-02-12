import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse

FLASK_BACKEND_URL = "http://127.0.0.1:9115"
AUTH_TOKEN = None  # Store authentication token globally

def usermod(request):
    """Creates or updates a user."""
    global AUTH_TOKEN
    if not AUTH_TOKEN:
        login_to_backend(request)  # Ensure login if no token is stored

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        url = f"{FLASK_BACKEND_URL}/api/admin/usermod"
        headers = {"X-OBSERVATORY-AUTH": AUTH_TOKEN}
        payload = {"username": username, "password": password}

        response = requests.post(url, json=payload, headers=headers)
        return JsonResponse(response.json(), status=response.status_code)

    return render(request, "usermod.html")

def list_users(request):
    """Fetches the list of users."""
    global AUTH_TOKEN
    if not AUTH_TOKEN:
        login_to_backend(None)  # Ensure login if no token is stored

    url = f"{FLASK_BACKEND_URL}/api/admin/users"
    headers = {"X-OBSERVATORY-AUTH": AUTH_TOKEN}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return JsonResponse(response.json())
    return JsonResponse({"error": "Failed to fetch users"}, status=response.status_code)

def login_to_backend(request):
    """Shows login form and logs in the user if form is submitted."""
    global AUTH_TOKEN

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        login_url = f"{FLASK_BACKEND_URL}/api/login"
        payload = {"username": username, "password": password}

        response = requests.post(login_url, data=payload)
        
        if response.status_code == 200:
            AUTH_TOKEN = response.json().get("token")  # Store token
            request.session["auth_token"] = AUTH_TOKEN  # Store in session for redirection
            request.session["username"] = username
            return redirect("home")  # Redirect to home page
        
        return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")  # Show login form

def logout_from_backend(request):
    """Logs out the user by invalidating the session."""
    global AUTH_TOKEN
    if AUTH_TOKEN:
        logout_url = f"{FLASK_BACKEND_URL}/api/logout"
        headers = {"X-OBSERVATORY-AUTH": AUTH_TOKEN}

        response = requests.post(logout_url, headers=headers)
        if response.status_code == 204:
            AUTH_TOKEN = None
            request.session.flush()  # Clear session data
            return redirect("login")
    
    return JsonResponse({"error": "Logout failed"}, status=400)

def create_user(request):
    """Creates a new user."""
    global AUTH_TOKEN
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        url = f"{FLASK_BACKEND_URL}/api/admin/usermod"
        headers = {"X-OBSERVATORY-AUTH": AUTH_TOKEN}
        payload = {"username": username, "password": password}

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return redirect("home")  # Redirect to home after creating a user

        return render(request, "create_user.html", {"error": "Failed to create user"})

    return render(request, "create_user.html")

def create_admin(request):
    """Creates a new admin."""
    global AUTH_TOKEN
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        url = f"{FLASK_BACKEND_URL}/api/admin/usermod"
        headers = {"X-OBSERVATORY-AUTH": AUTH_TOKEN}
        payload = {"username": username, "password": password, "role": "admin"}  # Setting role to admin

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return redirect("home")  # Redirect to home after creating an admin

        return render(request, "create_admin.html", {"error": "Failed to create admin"})

    return render(request, "create_admin.html")

def fetch_healthcheck():
    """Fetches healthcheck data using the JWT token."""
    global AUTH_TOKEN
    if not AUTH_TOKEN:
        return {"error": "User not authenticated"}

    url = f"{FLASK_BACKEND_URL}/api/admin/healthcheck"
    headers = {"X-OBSERVATORY-AUTH": AUTH_TOKEN}

    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"error": f"Backend returned {response.status_code}"}
    
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def home(request):
    """Home page displaying backend health status."""
    global AUTH_TOKEN
    if not AUTH_TOKEN:
        return redirect("login")  # Redirect to login if not authenticated

    data = fetch_healthcheck()
    return render(request, "home.html", {"data": data})