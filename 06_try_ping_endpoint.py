#!/usr/bin/env python3

# #authored-by-ai #gemini-2.5-pro
# #autonomous-ai #cursor
# SPDX-License-Identifier: MIT

import json
import requests # Still need for exception handling
from porkbun_api import make_porkbun_request # Import the helper function

# --- API Call specific to ping ---
try:
    print("Attempting to ping Porkbun API to check credentials...")
    # Make request to the /ping endpoint using the imported function
    ping_response = make_porkbun_request("/ping", {})
    print("Ping successful!")
    print(json.dumps(ping_response, indent=2))

# Handle potential errors from the API call or JSON parsing
except (requests.exceptions.RequestException, ValueError) as e:
    print(f"Error calling Porkbun API: {e}")

# Handle any other unexpected errors
except Exception as e:
    print(f"An unexpected error occurred: {e}")