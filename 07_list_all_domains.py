#!/usr/bin/env python3

# #authored-by-ai #gemini-2.5-pro
# #autonomous-ai #cursor
# SPDX-License-Identifier: MIT

import json
import requests # For exception handling
from porkbun_api import make_porkbun_request # Import the helper function

# --- API Call to List Domains ---
try:
    print("Attempting to list all domains...")
    # Payload for listing domains (empty for all domains by default)
    list_payload = {}
    # Make request to the /domain/listAll endpoint
    domains_response = make_porkbun_request("/domain/listAll", list_payload)
    print("Successfully retrieved domain list!")
    print(json.dumps(domains_response, indent=2))

# Handle potential errors from the API call or JSON parsing
except (requests.exceptions.RequestException, ValueError) as e:
    print(f"Error listing domains: {e}")

# Handle any other unexpected errors
except Exception as e:
    print(f"An unexpected error occurred: {e}") 