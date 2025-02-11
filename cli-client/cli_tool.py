import click
import requests
import json
import csv
import os
import pandas as pd

API_BASE_URL = "http://127.0.0.1:9115"
DEFAULT_FORMAT = "csv"
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

def print_output(data, output_format):
    if output_format == "json":
        print(json.dumps(data, indent=4))
    else:
        try:
            if isinstance(data, dict):  # If it's already a dictionary
                df = pd.DataFrame([data])  # Wrap in a list to ensure correct DataFrame structure
            else:  # Assume it's a file path
                with open(data, 'r', encoding='utf-8') as file:
                    json_data = json.load(file)
                df = pd.DataFrame(json_data if isinstance(json_data, list) else [json_data])
            
            df.to_csv('output.csv', index=False)
            print(f"CSV file saved successfully as 'output.csv'")
        except Exception as e:
            print(f"Error: {e}")


@click.group()
def cli():
    "Command Line Interface for Toll System"
    pass

# HEALTH CHECK
@click.command()
def healthcheck():
    "Check system health"
    token = load_token()
    if not token:
        print("Error: Not authenticated. Please log in first.")
        exit(401)

    url = f"{API_BASE_URL}/admin/healthcheck"
    response = requests.get(url, headers={"X-OBSERVATORY-AUTH": token})

    if response.status_code == 200:
        print_output(response.json(), "json")
    else:
        print(f"Error: {response.json().get('info', 'Unknown error')}")

# RESET PASSES
@click.command()
def resetpasses():
    "Reset all pass data"
    token = load_token()
    if not token:
        print("Error: Not authenticated. Please log in first.")
        exit(401)

    url = f"{API_BASE_URL}/admin/resetpasses"
    response = requests.post(url, headers={"X-OBSERVATORY-AUTH": token})

    if response.status_code == 200:
        print_output(response.json(), "json")
    else:
        print(f"Error: {response.json().get('info', 'Unknown error')}")

# RESET STATIONS
@click.command()
def resetstations():
    "Reset all toll station data"
    token = load_token()
    if not token:
        print("Error: Not authenticated. Please log in first.")
        exit(401)

    url = f"{API_BASE_URL}/admin/resetstations"
    response = requests.post(url, headers={"X-OBSERVATORY-AUTH": token})

    if response.status_code == 200:
        print_output(response.json(), "json")
    else:
        print(f"Error: {response.json().get('info', 'Unknown error')}")

# LOGIN
@click.command()
@click.option("--username", required=True, help="Username")
@click.option("--passw", required=True, help="Password")
def login(username, passw):
    "User login"
    url = f"{API_BASE_URL}/login"
    response = requests.post(url, data={"username": username, "password": passw})
    data = response.json()
    if "token" in data and response.status_code == 200:
        save_token(data["token"])
        print("Login Successful.")
    elif response.status_code == 401:
        print(f"Error: {response.json().get('message', 'Unknown error')}")
        return
    else:
        try:
            print(f"Error: {response.json().get('message', 'Unknown error')}")
        except requests.exceptions.JSONDecodeError:
            print("Error: Unexpected response from server.")

# LOGOUT
@click.command()
def logout():
    "User logout"
    token = load_token()
    if not token:
        print("Error: Not logged in.")
        return
    url = f"{API_BASE_URL}/logout"
    response = requests.post(url, headers={"X-OBSERVATORY-AUTH": token})
    if response.status_code == 204:
        delete_token()
        print_output(response.json(), "json")
    else:
        print(f"Error: {response.json().get('info', 'Unknown error')}")

# TOLLSTATIONPASSES
@click.command()
@click.option("--station", required=True, help="Station ID")
@click.option("--from", "date_from", required=True, help="Start date in YYYYMMDD")
@click.option("--to", "date_to", required=True, help="End date in YYYYMMDD")
@click.option("--format", default=DEFAULT_FORMAT, help="Output format: csv or json")
def tollstationpasses(station, date_from, date_to, format):
    "Retrieve toll station passes"
    token = load_token()
    if not token:
        print("Error: Not authenticated. Please log in first.")
        exit(401)

    url = f"{API_BASE_URL}/tollStationPasses/{station}/{date_from}/{date_to}"
    response = requests.get(url, headers={"X-OBSERVATORY-AUTH": token})
    if response.status_code == 200:
        print_output(response.json(), format)
    else:
        print(f"Error: {response.json().get('info', 'Unknown error')}")

# PASSANALYSIS
@click.command()
@click.option("--stationop", required=True, help="Station Operator ID")
@click.option("--tagop", required=True, help="Tag Operator ID")
@click.option("--from", "date_from", required=True, help="Start date in YYYYMMDD")
@click.option("--to", "date_to", required=True, help="End date in YYYYMMDD")
@click.option("--format", default=DEFAULT_FORMAT, help="Output format: csv or json")
def passanalysis(stationop, tagop, date_from, date_to, format):
    "Retrieve pass analysis between operators"
    token = load_token()
    if not token:
        print("Error: Not authenticated. Please log in first.")
        exit(401)
    url = f"{API_BASE_URL}/passAnalysis/{stationop}/{tagop}/{date_from}/{date_to}"
    response = requests.get(url, headers={"X-OBSERVATORY-AUTH": token})
    if response.status_code == 200:
        print_output(response.json(), format)
    else:
        print(f"Error: {response.json().get('info', 'Unknown error')}")

# PASSESCOST
@click.command()
@click.option("--stationop", required=True, help="Station Operator ID")
@click.option("--tagop", required=True, help="Tag Operator ID")
@click.option("--from", "date_from", required=True, help="Start date in YYYYMMDD")
@click.option("--to", "date_to", required=True, help="End date in YYYYMMDD")
@click.option("--format", default=DEFAULT_FORMAT, help="Output format: csv or json")
def passescost(stationop, tagop, date_from, date_to, format):
    "Retrieve pass cost between two operators"
    token = load_token()
    if not token:
        print("Error: Not authenticated. Please log in first.")
        exit(401)
    url = f"{API_BASE_URL}/passesCost/{stationop}/{tagop}/{date_from}/{date_to}"
    response = requests.get(url, headers={"X-OBSERVATORY-AUTH": token})
    if response.status_code == 200:
        print_output(response.json(), format)
    else:
        print(f"Error: {response.json().get('info', 'Unknown error')}")
        
# CHARGESBY
@click.command()
@click.option("--opid", required=True, help="Operator ID")
@click.option("--from", "date_from", required=True, help="Start date in YYYYMMDD")
@click.option("--to", "date_to", required=True, help="End date in YYYYMMDD")
@click.option("--format", default=DEFAULT_FORMAT, help="Output format: csv or json")
def chargesby(opid, date_from, date_to, format):
    "Retrieve charges from other operators"
    token = load_token()
    if not token:
        print("Error: Not authenticated. Please log in first.")
        exit(401)
    url = f"{API_BASE_URL}/chargesBy/{opid}/{date_from}/{date_to}"
    response = requests.get(url, headers={"X-OBSERVATORY-AUTH": token})
    if response.status_code == 200:
        print_output(response.json(), format)
    else:
        print(f"Error: {response.json().get('info', 'Unknown error')}")

# ADMIN
@click.command()
@click.option("--addpasses", is_flag=True, help="Upload pass data from a CSV file")
@click.option("--source", type=click.Path(exists=True), help="CSV file path (required with --addpasses)")
@click.option("--usermod", is_flag=True, help="Modify user credentials")
@click.option("--username", help="Username (required with --usermod)")
@click.option("--passw", help="Password (required with --usermod)")
@click.option("--users", is_flag=True, help="List all users")
def admin(addpasses, source, usermod, username, passw, users):
    """Admin tasks: Upload pass data, modify users, list users"""
    token = load_token()
    if not token:
        print("Error: Not authenticated. Please log in first.")
        exit(401)

    selected_options = sum([addpasses, usermod, users])
    if selected_options > 1:
        print("Error: You cannot use multiple admin options at the same time.")
        exit(1)

    if addpasses:
        if not source:
            print("Error: --addpasses requires --source <CSV file>")
            exit(1)
        url = f"{API_BASE_URL}/admin/addpasses"
        with open(source, "rb") as f:
            response = requests.post(url, headers={"X-OBSERVATORY-AUTH": token}, files={"file": f})
        print_output(response.json(), "json")

    elif usermod:
        if not username or not passw:
            print("Error: --usermod requires --username and --passw.")
            exit(1)
        url = f"{API_BASE_URL}/admin/usermod"
        response = requests.post(url, headers={"X-OBSERVATORY-AUTH": token}, json={"username": username, "password": passw})
        print_output(response.json(), "json")

    elif users:
        url = f"{API_BASE_URL}/admin/users"
        response = requests.get(url, headers={"X-OBSERVATORY-AUTH": token})
        print_output(response.json(), "json")
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
