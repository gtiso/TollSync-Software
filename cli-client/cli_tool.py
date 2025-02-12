import click
import requests
import io
import csv
import os

API_BASE_URL = "http://127.0.0.1:9115/api"
TOKEN_FILE = "auth_token.txt"

def save_token(token):
    with open(TOKEN_FILE, "w") as file:
        file.write(token)

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as file:
            return file.read().strip()
    return None

def delete_token():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)

@click.group()
def cli():
    "Command Line Interface for Toll System"
    pass

# HEALTH CHECK
@click.command()
@click.option("--format", type=str, default="csv", help="Specify the response format (json or csv).")
def healthcheck(format):
    "Check system health"
    token = load_token()
    if not token:
        print("Error: Not authenticated. Please log in first.")
        exit(401)

    normalized_format = "json" if format.lower() == "json" else "csv"
    url = f"{API_BASE_URL}/admin/healthcheck?format={normalized_format}"
    response = requests.get(url, headers={"X-OBSERVATORY-AUTH": token})

    if response.status_code == 200:
        print(response.text)
    else:
        print(response.text)

# RESET PASSES
@click.command()
@click.option("--format", type=str, default="csv", help="Specify the response format (json or csv).")
def resetpasses(format):
    "Reset all pass data"
    token = load_token()
    if not token:
        print("Error: Not authenticated. Please log in first.")
        exit(401)

    normalized_format = "json" if format.lower() == "json" else "csv"
    url = f"{API_BASE_URL}/admin/resetpasses?format={normalized_format}"
    response = requests.post(url, headers={"X-OBSERVATORY-AUTH": token})

    if response.status_code == 200:
        print(response.text)
    else:
        print(response.text)

# RESET STATIONS
@click.command()
@click.option("--format", type=str, default="csv", help="Specify the response format (json or csv).")
def resetstations(format):
    "Reset all toll station data"
    token = load_token()
    if not token:
        print("Error: Not authenticated. Please log in first.")
        exit(401)

    normalized_format = "json" if format.lower() == "json" else "csv"
    url = f"{API_BASE_URL}/admin/resetstations?format={normalized_format}"
    response = requests.post(url, headers={"X-OBSERVATORY-AUTH": token})

    if response.status_code == 200:
        print(response.text)
    else:
        print(response.text)

# LOGIN
@click.command()
@click.option("--username", required=True, help="Username")
@click.option("--passw", required=True, help="Password")
@click.option("--format", type=str, default="csv", help="Specify the response format (json or csv).")
def login(username, passw, format):
    """User login"""
    normalized_format = "json" if format.lower() == "json" else "csv"
    url = f"{API_BASE_URL}/login?format={normalized_format}"
    response = requests.post(url, data={"username": username, "password": passw})

    if response.status_code == 200:
        content_type = response.headers.get("Content-Type", "").lower()

        if "application/json" in content_type:
            # Parse JSON response
            data = response.json()
            token = data.get("token")
        else:
            # Assume CSV format and parse it
            csv_reader = csv.reader(io.StringIO(response.text))
            rows = list(csv_reader)

            if len(rows) > 1 and len(rows[1]) > 0:  # Ensure there is a second row
                token = rows[1][0]  # Assuming the token is the first value in the second row

        if token:
            save_token(token)
        print(response.text)
    else:
        print(response.text)

# LOGOUT
@click.command()
@click.option("--format", type=str, default="csv", help="Specify the response format (json or csv).")
def logout(format):
    "User logout"
    token = load_token()
    if not token:
        print("Error: Not logged in.")
        return
    
    normalized_format = "json" if format.lower() == "json" else "csv"
    url = f"{API_BASE_URL}/logout?format={normalized_format}"
    response = requests.post(url, headers={"X-OBSERVATORY-AUTH": token})
    if response.status_code == 204:
        delete_token()
        print("Logout Successful.")

# TOLLSTATIONPASSES
@click.command()
@click.option("--station", required=True, help="Station ID")
@click.option("--from", "date_from", required=True, help="Start date in YYYYMMDD")
@click.option("--to", "date_to", required=True, help="End date in YYYYMMDD")
@click.option("--format", type=str, default="csv", help="Specify the response format (json or csv).")
def tollstationpasses(station, date_from, date_to, format):
    "Retrieve toll station passes"
    token = load_token()
    if not token:
        print("Error: Not authenticated. Please log in first.")
        exit(401)

    normalized_format = "json" if format.lower() == "json" else "csv"
    url = f"{API_BASE_URL}/tollStationPasses/{station}/{date_from}/{date_to}?format={normalized_format}"
    response = requests.get(url, headers={"X-OBSERVATORY-AUTH": token})
    if response.status_code == 200:
        print(response.text)
    else:
        print(response.text)

# PASSANALYSIS
@click.command()
@click.option("--stationop", required=True, help="Station Operator ID")
@click.option("--tagop", required=True, help="Tag Operator ID")
@click.option("--from", "date_from", required=True, help="Start date in YYYYMMDD")
@click.option("--to", "date_to", required=True, help="End date in YYYYMMDD")
@click.option("--format", type=str, default="csv", help="Specify the response format (json or csv).")
def passanalysis(stationop, tagop, date_from, date_to, format):
    "Retrieve pass analysis between operators"
    token = load_token()
    if not token:
        print("Error: Not authenticated. Please log in first.")
        exit(401)

    normalized_format = "json" if format.lower() == "json" else "csv"
    url = f"{API_BASE_URL}/passAnalysis/{stationop}/{tagop}/{date_from}/{date_to}?format={normalized_format}"
    response = requests.get(url, headers={"X-OBSERVATORY-AUTH": token})
    if response.status_code == 200:
        print(response.text)
    else:
        print(response.text)

# PASSESCOST
@click.command()
@click.option("--stationop", required=True, help="Station Operator ID")
@click.option("--tagop", required=True, help="Tag Operator ID")
@click.option("--from", "date_from", required=True, help="Start date in YYYYMMDD")
@click.option("--to", "date_to", required=True, help="End date in YYYYMMDD")
@click.option("--format", type=str, default="csv", help="Specify the response format (json or csv).")
def passescost(stationop, tagop, date_from, date_to, format):
    "Retrieve pass cost between two operators"
    token = load_token()
    if not token:
        print("Error: Not authenticated. Please log in first.")
        exit(401)

    normalized_format = "json" if format.lower() == "json" else "csv"
    url = f"{API_BASE_URL}/passesCost/{stationop}/{tagop}/{date_from}/{date_to}?format={normalized_format}"
    response = requests.get(url, headers={"X-OBSERVATORY-AUTH": token})
    if response.status_code == 200:
        print(response.text)
    else:
        print(response.text)
        
# CHARGESBY
@click.command()
@click.option("--opid", required=True, help="Operator ID")
@click.option("--from", "date_from", required=True, help="Start date in YYYYMMDD")
@click.option("--to", "date_to", required=True, help="End date in YYYYMMDD")
@click.option("--format", type=str, default="csv", help="Specify the response format (json or csv).")
def chargesby(opid, date_from, date_to, format):
    "Retrieve charges from other operators"
    token = load_token()
    if not token:
        print("Error: Not authenticated. Please log in first.")
        exit(401)
    
    normalized_format = "json" if format.lower() == "json" else "csv"
    url = f"{API_BASE_URL}/chargesBy/{opid}/{date_from}/{date_to}?format={normalized_format}"
    response = requests.get(url, headers={"X-OBSERVATORY-AUTH": token})
    if response.status_code == 200:
        print(response.text)
    else:
        print(response.text)

# ADMIN
@click.command()
@click.option("--addpasses", is_flag=True, help="Upload pass data from a CSV file")
@click.option("--source", type=click.Path(exists=True), help="CSV file path (required with --addpasses)")
@click.option("--usermod", is_flag=True, help="Modify user credentials")
@click.option("--username", help="Username (required with --usermod)")
@click.option("--passw", help="Password (required with --usermod)")
@click.option("--users", is_flag=True, help="List all users")
@click.option("--format", type=str, default="csv", help="Specify the response format (json or csv).")
def admin(addpasses, source, usermod, username, passw, users, format):
    """Admin tasks: Upload pass data, modify users, list users"""
    token = load_token()
    if not token:
        print("Error: Not authenticated. Please log in first.")
        exit(401)

    normalized_format = "json" if format.lower() == "json" else "csv"

    selected_options = sum([addpasses, usermod, users])
    if selected_options > 1:
        print("Error: You cannot use multiple admin options at the same time.")
        exit(1)

    if addpasses:
        if not source:
            print("Error: --addpasses requires --source <CSV file>")
            exit(1)
        url = f"{API_BASE_URL}/admin/addpasses?format={normalized_format}"
        with open(source, "rb") as f:
            response = requests.post(url, headers={"X-OBSERVATORY-AUTH": token}, files={"file": f})
        print(response.text)

    elif usermod:
        if not username or not passw:
            print("Error: --usermod requires --username and --passw.")
            exit(1)
        url = f"{API_BASE_URL}/admin/usermod?format={normalized_format}"
        response = requests.post(url, headers={"X-OBSERVATORY-AUTH": token}, json={"username": username, "password": passw})
        print(response.text)

    elif users:
        url = f"{API_BASE_URL}/admin/users?format={normalized_format}"
        response = requests.get(url, headers={"X-OBSERVATORY-AUTH": token})
        print(response.text)
    else:
        print("Error: No valid admin option provided. Use --addpasses, --usermod, or --users.")

cli.add_command(resetpasses)
cli.add_command(resetstations)
cli.add_command(healthcheck)
cli.add_command(login)
cli.add_command(logout)
cli.add_command(tollstationpasses)
cli.add_command(passanalysis)
cli.add_command(passescost)
cli.add_command(chargesby)
cli.add_command(admin)

if __name__ == "__main__":
    cli()
