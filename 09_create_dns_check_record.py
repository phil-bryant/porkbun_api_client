#!/usr/bin/env python3

# #authored-by-ai #gemini-2.5-pro
# #autonomous-ai #cursor
# SPDX-License-Identifier: MIT

"""
Example script to create a DNS record using the Porkbun API.
Reads record details from 08_dns_check_record_text.txt and takes domain as argument.

Ensure your virtual environment is active and ~/.env file is populated.
Usage: ./09_create_dns_check_record.py yourdomain.com
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
                # Use regex to handle potential quotes in values
                match = re.match(r'^([^=]+)="?([^"]*)"?$', line)
                if match:
                    key, value = match.groups()
                    # Special handling for escaped quotes within the content value if needed
                    if key == "RECORD_CONTENT":
                         # Remove outer quotes added by the simple parse, restore inner quotes
                         # Assumes content is like "\"string\""
                         value = value.replace('\\"', '"')
                    config[key] = value
                else:
                    print(f"Warning: Skipping malformed line in {config_path}: {line}")
    except FileNotFoundError:
        print(f"Error: Config file not found at {config_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading config file {config_path}: {e}")
        sys.exit(1)

    # Basic validation
    required_keys = ["RECORD_NAME", "RECORD_TYPE", "RECORD_CONTENT", "RECORD_TTL"]
    if not all(key in config for key in required_keys):
        print(f"Error: Config file {config_path} is missing one or more required keys: {required_keys}")
        sys.exit(1)

    return config

# --- Configuration (now loaded from file/args) ---
# DOMAIN is now a command-line argument
# RECORD_NAME, RECORD_TYPE, RECORD_CONTENT, RECORD_TTL loaded from file
# --- End Configuration ---

def create_dns_record(domain, name, record_type, content, ttl="600"):
    """
    Creates a DNS record for the specified domain.

    Args:
        domain (str): The domain name (e.g., 'yourdomain.com').
        name (str): The subdomain part (e.g., 'www', '_test', leave "" for root).
        record_type (str): The type of DNS record (e.g., 'A', 'TXT', 'CNAME').
        content (str): The record content (e.g., IP address, hostname, text value).
        ttl (str): The Time To Live for the record (default '600').

    Returns:
        dict: The JSON response from the Porkbun API.

    Raises:
        requests.exceptions.RequestException: If the API request fails.
        ValueError: If the API response indicates an error or is not valid JSON.
        Exception: For any other unexpected errors.
    """
    endpoint = f"/dns/create/{domain}"
    payload = {
        "name": name,
        "type": record_type,
        "content": content,
        "ttl": ttl
        # Optional: "prio": "10" for MX records
    }
    print(f"Attempting to create {record_type} record for '{name}.{domain}' pointing to '{content}'...")
    return make_porkbun_request(endpoint, payload)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <yourdomain.com>")
        sys.exit(1)

    DOMAIN = sys.argv[1]
    record_config = load_record_config(CONFIG_FILE)

    RECORD_NAME = record_config["RECORD_NAME"]
    RECORD_TYPE = record_config["RECORD_TYPE"]
    RECORD_CONTENT = record_config["RECORD_CONTENT"]
    RECORD_TTL = record_config["RECORD_TTL"]

    # Before running, ensure API access is enabled for DOMAIN in Porkbun UI!
    # https://porkbun.com/account/domains > Details > Authoritative Nameservers > API Access
    print(f"--- Running DNS Record Creation for {DOMAIN} ---")
    print(f"Using record config from: {CONFIG_FILE}")
    print(f"  Name:    {RECORD_NAME}")
    print(f"  Type:    {RECORD_TYPE}")
    print(f"  Content: {RECORD_CONTENT}")
    print(f"  TTL:     {RECORD_TTL}")
    print(f"IMPORTANT: Ensure API access is ENABLED for '{DOMAIN}' in the Porkbun dashboard.")

    try:
        response = create_dns_record(
            domain=DOMAIN,
            name=RECORD_NAME,
            record_type=RECORD_TYPE,
            content=RECORD_CONTENT,
            ttl=RECORD_TTL
        )
        print("\nAPI Response:")
        print(json.dumps(response, indent=2))

        if response.get("status") == "SUCCESS":
            record_full_name = f"{RECORD_NAME}.{DOMAIN}" if RECORD_NAME else DOMAIN
            print(f"\nSuccessfully created {RECORD_TYPE} record for {record_full_name}")
            record_id = response.get("id")
            if record_id:
                print(f"Record ID: {record_id} (useful for editing/deleting)")
        else:
            print(f"\nAPI Error: {response.get('message', 'Unknown error')}")

    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"\nAPI Call Error: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

    print(f"--- Finished DNS Record Creation for {DOMAIN} ---") 