#!/usr/bin/env python3

# #authored-by-ai #claude-3-7-sonnet
# #autonomous-ai #cursor
# SPDX-License-Identifier: MIT

"""
Script to change the name servers of a domain to Cloudflare's name servers using the Porkbun API.
Takes the domain as a command line argument to keep domain names out of public repositories.

Ensure your virtual environment is active and ~/.env file is populated with API keys.
Usage: ./14_change_name_servers_to_cloudflare.py yourdomain.com
"""

from porkbun_api import make_porkbun_request
import requests  # For exception handling
import json      # For printing output
import sys       # For command-line arguments

# Cloudflare's nameservers
CLOUDFLARE_NS = [
    "ns1.cloudflare.com",
    "ns2.cloudflare.com"
]

def get_current_nameservers(domain):
    """
    Retrieves the current name servers for the specified domain.
    
    Args:
        domain (str): The domain name to check.
        
    Returns:
        list: The current name servers for the domain.
    """
    endpoint = f"/domain/getNs/{domain}"
    print(f"Retrieving current nameservers for '{domain}'...")
    
    try:
        response = make_porkbun_request(endpoint, {})
        return response.get("ns", [])
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"Error retrieving nameservers: {e}")
        return []

def update_nameservers(domain, nameservers):
    """
    Updates the name servers for the specified domain.
    
    Args:
        domain (str): The domain name to update.
        nameservers (list): List of name servers to set.
        
    Returns:
        dict: The JSON response from the Porkbun API.
    """
    endpoint = f"/domain/updateNs/{domain}"
    payload = {
        "ns": nameservers
    }
    
    print(f"Updating nameservers for '{domain}' to:")
    for ns in nameservers:
        print(f"  - {ns}")
        
    return make_porkbun_request(endpoint, payload)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <yourdomain.com>")
        sys.exit(1)

    DOMAIN = sys.argv[1]
    
    print(f"--- Running Nameserver Change to Cloudflare for {DOMAIN} ---")
    print(f"IMPORTANT: Ensure API access is ENABLED for '{DOMAIN}' in the Porkbun dashboard.")
    
    try:
        # Get current nameservers
        current_ns = get_current_nameservers(DOMAIN)
        if current_ns:
            print("\nCurrent nameservers:")
            for ns in current_ns:
                print(f"  - {ns}")
        
        # Update to Cloudflare nameservers
        print("\nChanging nameservers to Cloudflare...")
        response = update_nameservers(DOMAIN, CLOUDFLARE_NS)
        
        print("\nAPI Response:")
        print(json.dumps(response, indent=2))
        
        if response.get("status") == "SUCCESS":
            print(f"\nSuccessfully changed nameservers for {DOMAIN} to Cloudflare's nameservers.")
            print("\nNOTE: DNS changes may take up to 48 hours to propagate worldwide.")
            print("      In practice, most places will see the change within a few hours.")
            print("      You can track nameserver propagation using a service like whatsmydns.net.")
        else:
            print(f"\nAPI Error: {response.get('message', 'Unknown error')}")
            
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"\nAPI Call Error: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        
    print(f"--- Finished Nameserver Change Process for {DOMAIN} ---") 