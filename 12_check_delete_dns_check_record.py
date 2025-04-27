#!/usr/bin/env python3

# #authored-by-ai #gemini-2.5-pro
# #autonomous-ai #cursor
# SPDX-License-Identifier: MIT

"""
Example script to retrieve all DNS records for a domain using the Porkbun API
and specifically check if the test record from 08_dns_check_record_text.txt is present.
Reads record details from 08_dns_check_record_text.txt and takes domain as argument.

Ensure your virtual environment is active and ~/.env file is populated.
Usage: ./12_check_delete_dns_check_record.py yourdomain.com
"""

from porkbun_api import make_porkbun_request
import requests  # For exception handling
import json      # For printing output
import os        # For potential future env var use
import sys       # For command-line arguments
import re        # For parsing the config file

CONFIG_FILE = "08_dns_check_record_text.txt"

def load_record_config(config_path):
    """Loads record details from the specified config file."""
    config = {}
    try:
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                # Original regex: match = re.match(r'^([^=]+)=\"?([^\"]*)\"?$', line)
                # Improved parsing: Split by first '=', handle quotes, and unescape
                parts = line.split('=', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    # Remove surrounding quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    # Replace escaped quotes \\\" with actual quotes \"
                    value = value.replace('\\\\"', '"')
                    config[key] = value
                else:
                    print(f"Warning: Skipping malformed line in {config_path}: {line}")
    except FileNotFoundError:
        print(f"Error: Config file not found at {config_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading config file {config_path}: {e}")
        sys.exit(1)

    required_keys = ["RECORD_NAME", "RECORD_TYPE"]
    if not all(key in config for key in required_keys):
        print(f"Error: Config file {config_path} is missing required keys: {required_keys}")
        sys.exit(1)
    return config

# --- Configuration (now loaded from file/args) ---
# DOMAIN is now a command-line argument
# --- End Configuration ---

def retrieve_all_records(domain):
    """
    Retrieves all DNS records for the specified domain.

    Args:
        domain (str): The domain name (e.g., 'yourdomain.com').

    Returns:
        dict: The JSON response from the Porkbun API, expecting {"status": ..., "records": [...]}.

    Raises:
        requests.exceptions.RequestException: If the API request fails.
        ValueError: If the API response indicates an error or is not valid JSON.
        Exception: For any other unexpected errors.
    """
    endpoint = f"/dns/retrieve/{domain}"
    print(f"Attempting to retrieve all DNS records for '{domain}'...")
    # This endpoint requires an empty payload
    return make_porkbun_request(endpoint, {})

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <yourdomain.com>")
        sys.exit(1)

    DOMAIN = sys.argv[1]
    record_config = load_record_config(CONFIG_FILE)

    record_name_to_check = record_config["RECORD_NAME"]
    record_type_to_check = record_config["RECORD_TYPE"]
    record_full_name = f"{record_name_to_check}.{DOMAIN}" if record_name_to_check else DOMAIN

    print(f"--- Running Check DNS Records for {DOMAIN} ---")
    print(f"Checking for presence of test record from {CONFIG_FILE}:")
    print(f"  Name: {record_name_to_check}")
    print(f"  Type: {record_type_to_check}")
    print(f"IMPORTANT: Ensure API access is ENABLED for '{DOMAIN}' in the Porkbun dashboard.")

    try:
        response = retrieve_all_records(DOMAIN)

        if response.get("status") == "SUCCESS" and "records" in response:
            print(f"\nSuccessfully retrieved {len(response['records'])} records for {DOMAIN}.")
            # Check specifically for the test record
            found_test_record = False
            for record in response['records']:
                # Porkbun API might return name with or without trailing domain
                # Let's check both possibilities for robustness
                api_record_name = record.get('name')
                is_match = (api_record_name == record_name_to_check or api_record_name == record_full_name) and record.get('type') == record_type_to_check

                if is_match:
                    print(f"\n[!] FOUND: The test record ({record_type_to_check} for {record_full_name}) was found in the list.")
                    print(json.dumps(record, indent=4))
                    found_test_record = True
                    # Don't break, show all matches if duplicates exist (shouldn't normally)

            if not found_test_record:
                 print(f"\n[✓] NOT FOUND: The specific test record ({record_type_to_check} for {record_full_name}) was NOT found in the list.")
            # Consider exit code based on whether the record was found?
            # For now, just printing status.

            # Optionally print all records
            # print("\nFull Record List:")
            # print(json.dumps(response['records'], indent=2))
        else:
            print(f"\nAPI Error: {response.get('message', 'Could not retrieve records or unexpected format')}")

    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"\nAPI Call Error: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

    print(f"--- Finished Check DNS Records for {DOMAIN} ---") 