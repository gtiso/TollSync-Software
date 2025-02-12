import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from collections import defaultdict


FLASK_BACKEND_URL = "http://127.0.0.1:9115"



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


def get_op_id_for_user(username):
    """Fetches the OpID for the given user."""

    url = f"{FLASK_BACKEND_URL}/api/getOpID/{username}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "OpID" in data:
                return data["OpID"]
            else:
                print("Error: OpID not found in response")
                return None
        else:
            print(f"Error fetching OpID: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None 

def login_to_backend(request):
    """Logs in and redirects users to the dashboard."""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        login_url = f"{FLASK_BACKEND_URL}/api/login"
        payload = {"username": username, "password": password}

        response = requests.post(login_url, data=payload)
        
        if response.status_code == 200:
            request.session["auth_token"] = response.json().get("token")  # Store token in session
            request.session["username"] = username  # Store the actual username
            request.session["op_id"] = get_op_id_for_user(username)  # Store OpID in session
            request.session["is_authenticated"] = True  # Mark user as authenticated
            return redirect("dashboard")  # Redirect to dashboard
        
        return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")  # Show login form

def logout_from_backend(request):
    """Logs out and redirects to login."""
    if request.session.get("auth_token"):
        logout_url = f"{FLASK_BACKEND_URL}/api/logout"
        headers = {"X-OBSERVATORY-AUTH": request.session["auth_token"]}

        response = requests.post(logout_url, headers=headers)
        if response.status_code == 204:
            request.session.flush()  # Clear session data
            return redirect("login")
    
    return JsonResponse({"error": "Logout failed"}, status=400)

def dashboard(request):
    """Renders the dashboard only if the user is logged in."""
    if not request.session.get("is_authenticated"):
        return redirect("login")  # Redirect to login if not authenticated

    username = request.session.get("username", "User")  # Get the logged-in username

    return render(request, "dashboard.html", {"username": username})



def api_passes_cost(request, tollOpID, tagOpID, date_from, date_to):
    """Fetches Passes Cost data from Flask API and returns JSON."""
    if not request.session.get("is_authenticated"):
        return JsonResponse({"error": "Unauthorized"}, status=401)

    url = f"{FLASK_BACKEND_URL}/api/getTransactions/{tollOpID}/{tagOpID}/{date_from}/{date_to}"
    headers = {"X-OBSERVATORY-AUTH": request.session.get("auth_token")}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return JsonResponse(response.json(), status=200)

    return JsonResponse({"error": "Failed to fetch data"}, status=response.status_code)


def passes_cost_view(request):
    """Displays the form and processed Passes Cost data."""
    if not request.session.get("is_authenticated"):
        return redirect("login")

    op_id = request.session.get("op_id")  # Get the user's OpID
    all_operators = ["AM", "EG", "GE", "KO", "MO", "NAO", "NO"]  # Full list of operators

    # Exclude the logged-in operator
    available_operators = [op for op in all_operators if op != op_id]
    result_data = None

    if request.method == "POST":
        tollOpID = request.POST.get("tollOpID")
        tagOpID = op_id  # Automatically set Tag Operator ID from session
        date_from = request.POST.get("date_from")
        date_to = request.POST.get("date_to")

        url = f"{FLASK_BACKEND_URL}/api/getTransactions/{tollOpID}/{tagOpID}/{date_from}/{date_to}"
        headers = {"X-OBSERVATORY-AUTH": request.session.get("auth_token")}

        response = requests.get(url, headers=headers)

        print(response.text)
        if response.status_code == 200:
            data = response.json()

            # Ensure required fields exist in response
            if all(key in data for key in ["tollOpID", "tagOpID", "requestTimestamp", "periodFrom", "periodTo", "nPasses", "passesCost"]):
                result_data = {
                    "Toll_Operator_ID": data["tollOpID"],
                    "Tag_Operator_ID": data["tagOpID"],
                    "Request_Timestamp": data["requestTimestamp"],
                    "Period_From": data["periodFrom"],
                    "Period_To": data["periodTo"],
                    "Number_of_Passes": data["nPasses"],
                    "Total_Passes_Cost": data["passesCost"]
                }
            else:
                print("Error: Missing required fields in API response")

        else:
            print(f"Error Fetching Data: {response.status_code} - {response.text}")  # Debugging output

    return render(request, "passes_cost.html", {"data": result_data, "op_id": op_id, "op_id": op_id, "available_operators": available_operators})

def pay_transactions(request):
    """Processes payments for the passes cost and resets the total amount owed to zero."""
    if not request.session.get("is_authenticated"):
        return redirect("login")

    op_id = request.session.get("op_id")  # Get the logged-in user's OpID

    if request.method == "POST":
        tollOpID = request.POST.get("tollOpID")  # The toll operator receiving payment
        tagOpID = op_id  # The current user paying the amount
        date_from = request.POST.get("date_from").replace("-", "")  # Convert date format
        date_to = request.POST.get("date_to").replace("-", "")

        # Construct API request URL to trigger the payment
        url = f"{FLASK_BACKEND_URL}/api/payTransactions/{tollOpID}/{tagOpID}/{date_from}/{date_to}"
        headers = {"X-OBSERVATORY-AUTH": request.session.get("auth_token")}

        print("API Request URL for Payment:", url)  # Debugging output

        response = requests.post(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse({"message": data.get("message", "Payment processed successfully!")}, status=200)
        else:
            return JsonResponse({"error": "Payment failed, please try again."}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)

def toll_station_passes(request, tollStationID, date_from, date_to):
    """Fetches toll station passes."""
    global AUTH_TOKEN
    url = f"{FLASK_BACKEND_URL}/api/tollStationPasses/{tollStationID}/{date_from}/{date_to}"
    headers = {"X-OBSERVATORY-AUTH": AUTH_TOKEN}

    response = requests.get(url, headers=headers)
    return JsonResponse(response.json(), status=response.status_code)

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
    """Redirect users to the login page by default."""
    return redirect("login")  # Redirect to login page
