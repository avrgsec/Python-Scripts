# scout_api.py - Super simple script to pull RAW data from an Endpoint

import requests

api_url = input("Provide the link of the API Endpoint.") # Specify URL you want to scan

print(f"--- Scouting API endpoint: {api_url} ---")

try:
    response = requests.get(api_url)

    if response.status_code == 200:
        print("Success! Server responded with status 200 (OK).")
        print("\n--- RAW RESPONSE TEXT ---")

        print(response.text)
        
    else:
        print(f"Error: Server responded with status code {response.status_code}")

except requests.exceptions.ConnectionError:
    print("\nError: Could not connect to the API server.")
    print("Please make sure you've given the correct URL and the API is online.")
