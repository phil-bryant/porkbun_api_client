#!/usr/bin/env python3

# #authored-by-ai #gemini-2.5-pro
# #autonomous-ai #cursor
# SPDX-License-Identifier: MIT

import os
import json
import requests # Use requests for HTTP calls

from dotenv import load_dotenv
from pathlib import Path

# --- Configuration ---
# Load environment variables from ~/.env
dotenv_path = Path.home() / '.env'
load_dotenv(dotenv_path=dotenv_path)

# Load API keys from environment
API_KEY = os.environ.get("PORKBUN_API_KEY")
SECRET_KEY = os.environ.get("PORKBUN_SECRET_KEY")

PORKBUN_API_URL = "https://api.porkbun.com/api/json/v3"

# --- Helper Function for API Calls ---
def make_porkbun_request(endpoint, payload):
    """Sends a POST request to the Porkbun API.
    Args:
        endpoint (str): The API endpoint (e.g., '/ping').
        payload (dict): The JSON payload for the request.
    Returns:
        dict: The JSON response from the API.
    Raises:
        requests.exceptions.RequestException: If the request fails.
        ValueError: If the response is not valid JSON or indicates an error.
        SystemExit: If API keys are missing.
    """
    if not API_KEY or not SECRET_KEY:
        print("Error: PORKBUN_API_KEY or PORKBUN_SECRET_KEY not found.")
        print(f"Ensure they are set in your environment or in {dotenv_path}")
        print("You can get keys from: https://app.porkbun.com/account/apikeys")
        exit(1) # Exit if keys are missing

    url = PORKBUN_API_URL + endpoint
    headers = {'Content-Type': 'application/json'}

    # Add authentication keys to the payload
    auth_payload = {
        "apikey": API_KEY,
        "secretapikey": SECRET_KEY
    }
    full_payload = {**auth_payload, **payload}

    response = requests.post(url, headers=headers, json=full_payload)
    response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

    try:
        response_json = response.json()
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON received from API: {response.text}")

    if response_json.get("status") != "SUCCESS":
        error_message = response_json.get("message", "Unknown API error")
        raise ValueError(f"Porkbun API Error: {error_message}")

    return response_json

# Example of how to use this module if run directly (optional)
# if __name__ == '__main__':
#     try:
#         print("Testing API module by pinging...")
#         ping_data = make_porkbun_request("/ping", {})
#         print("Module test ping successful:")
#         print(json.dumps(ping_data, indent=2))
#     except (requests.exceptions.RequestException, ValueError) as e:
#         print(f"Error during module test ping: {e}")
#     except Exception as e:
#         print(f"An unexpected error occurred during module test: {e}") 