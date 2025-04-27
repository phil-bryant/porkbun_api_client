#!/usr/bin/env python3

# #authored-by-ai #gemini-2.5-pro
# #autonomous-ai #cursor
# SPDX-License-Identifier: MIT

"""
Example script to delete a specific DNS record using the Porkbun API.
Reads record details from 08_dns_check_record_text.txt and takes domain as argument.
It first retrieves the record ID and then uses the delete-by-ID endpoint.

Ensure your virtual environment is active and ~/.env file is populated.
Usage: ./11_delete_dns_check_record.py yourdomain.com
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

    required_keys = ["RECORD_NAME", "RECORD_TYPE", "RECORD_CONTENT"]
    if not all(key in config for key in required_keys):
        print(f"Error: Config file {config_path} is missing one or more required keys: {required_keys}")
        sys.exit(1)
    return config

# --- Configuration (now loaded from file/args) ---
# DOMAIN is now a command-line argument
# RECORD_NAME, RECORD_TYPE, RECORD_CONTENT loaded from file
# --- End Configuration ---

def get_dns_record_id(domain, name, record_type, content_filter=None):
    """
    Retrieves DNS records matching the name and type, then filters by content
    to find the specific record ID.

    Args:
        domain (str): The domain name.
        name (str): The subdomain part.
        record_type (str): The type of DNS record.
        content_filter (str, optional): The exact content to match. Defaults to None.

    Returns:
        str or None: The ID of the matching record, or None if not found or ambiguous.
    """
    record_full_name = f"{name}.{domain}" if name else domain
    # Endpoint retrieves records by name and type
    endpoint = f"/dns/retrieveByNameType/{domain}/{record_type}/{name}"
    print(f"Attempting to retrieve {record_type} records for '{record_full_name}' to find ID...")
    try:
        response = make_porkbun_request(endpoint, {})
        if response.get("status") == "SUCCESS" and "records" in response:
            matching_records = []
            for record in response["records"]:
                # Filter by exact content if provided
                if content_filter is None or record.get("content") == content_filter:
                    matching_records.append(record)

            if len(matching_records) == 1:
                record_id = matching_records[0].get("id")
                print(f"Found unique matching record with ID: {record_id}")
                return record_id
            elif len(matching_records) > 1:
                print(f"Error: Found multiple records matching criteria. Cannot determine unique ID.")
                return None
            else:
                print(f"No record found matching name='{name}', type='{record_type}', content='{content_filter}'. Maybe already deleted?")
                return None
        else:
            # Handle case where retrieveByNameType returns empty list but success (record doesn't exist)
            if response.get("status") == "SUCCESS" and not response.get("records"):
                 print(f"No record found matching name='{name}', type='{record_type}'. Maybe already deleted?")
                 return None
            print(f"API Error during retrieval: {response.get('message', 'Unknown error')}")
            return None
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"API Call Error during retrieval: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error during retrieval: {e}")
        return None

def delete_dns_record_by_id(domain, record_id):
    """
    Deletes a DNS record using its specific ID.

    Args:
        domain (str): The domain name.
        record_id (str): The unique ID of the record to delete.

    Returns:
        dict: The JSON response from the Porkbun API.
    """
    endpoint = f"/dns/delete/{domain}/{record_id}"
    print(f"Attempting to delete record ID '{record_id}' for domain '{domain}'...")
    # Delete by ID endpoint uses an empty payload
    return make_porkbun_request(endpoint, {})

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <yourdomain.com>")
        sys.exit(1)

    DOMAIN = sys.argv[1]
    record_config = load_record_config(CONFIG_FILE)

    RECORD_NAME = record_config["RECORD_NAME"]
    RECORD_TYPE = record_config["RECORD_TYPE"]
    RECORD_CONTENT = record_config["RECORD_CONTENT"]
    # RECORD_TTL is not needed for deletion

    record_full_name = f"{RECORD_NAME}.{DOMAIN}" if RECORD_NAME else DOMAIN

    print(f"--- Running DNS Record Deletion (Retrieve ID then Delete) for {DOMAIN} ---")
    print(f"Using record config from: {CONFIG_FILE}")
    print(f"Target: {RECORD_TYPE} '{record_full_name}' Content: '{RECORD_CONTENT}'")
    print(f"IMPORTANT: Ensure API access is ENABLED for '{DOMAIN}' in the Porkbun dashboard.")

    record_id_to_delete = None
    try:
        # Step 1: Find the record ID
        record_id_to_delete = get_dns_record_id(
            domain=DOMAIN,
            name=RECORD_NAME,
            record_type=RECORD_TYPE,
            content_filter=RECORD_CONTENT
        )

        # Step 2: If ID found, attempt deletion
        if record_id_to_delete:
            delete_response = delete_dns_record_by_id(DOMAIN, record_id_to_delete)
            print("\nDeletion API Response:")
            print(json.dumps(delete_response, indent=2))

            if delete_response.get("status") == "SUCCESS":
                print(f"\nSuccessfully deleted record ID '{record_id_to_delete}'")
            else:
                print(f"\nAPI Error during deletion: {delete_response.get('message', 'Unknown error')}")
        else:
            print("\nSkipping deletion step as record ID was not found.")

    except (requests.exceptions.RequestException, ValueError) as e:
        # Catch errors from the delete_dns_record_by_id call if get_dns_record_id succeeded
        # Errors from get_dns_record_id are handled within that function
        print(f"\nAPI Call Error during deletion step: {e}")
    except Exception as e:
        print(f"\nUnexpected error during deletion step: {e}")

    print(f"--- Finished DNS Record Deletion Process for {DOMAIN} ---") 