# Porkbun API v3 Client

# #authored-by-ai #gemini-2.5-pro
# #autonomous-ai #cursor
# SPDX-License-Identifier: MIT

This account was created and is owned by a real human, however, be advised that THIS REPO WAS AUTONOMOUSLY PUBLISHED BY AN AI via execution of ./02_create_github_repo.sh --personal --public

This project provides a basic framework for interacting with the Porkbun API v3 using direct HTTP requests in Python, focused on managing DNS records.

## Overview

Instead of relying on third-party client libraries, this project uses the standard `requests` library to make POST calls to the official Porkbun API v3 endpoints ([https://porkbun.com/api/json/v3/documentation](https://porkbun.com/api/json/v3/documentation)).

It includes:
- A core Python module (`porkbun_api.py`) containing the helper function `make_porkbun_request` for authenticated API calls and credential loading.
- An example script (`06_try_ping_endpoint.py`) demonstrating how to use the module to ping the API.
- An example script (`07_list_all_domains.py`) demonstrating how to use the module to list all domains.
- A text file (`08_dns_check_record_text.txt`) defining the details of a test DNS record used by subsequent scripts.
- An example script (`09_create_dns_check_record.py`) demonstrating how to create the test DNS record defined in `08...txt` for a specified domain.
- A shell script (`10_verify_create_dns_check_record.sh`) to verify DNS propagation for the created test record across multiple public DNS servers.
- An example script (`11_delete_dns_check_record.py`) demonstrating how to delete the specific test DNS record defined in `08...txt` for a specified domain.
- An example script (`12_check_delete_dns_check_record.py`) to retrieve all DNS records for a domain from the API and check if the test record is present.
- A shell script (`13_verify_delete_dns_check_record.sh`) to verify DNS propagation of the test record's deletion across multiple public DNS servers.
- Dependency management via `04_requirements.txt`.
- A shell script (`03_create_venv.sh`) to create a Python virtual environment.
- A shell script (`05_load_requirements.sh`) to install dependencies into the virtual environment.
- An optional shell script (`02_create_github_repo.sh`) to initialize a git repository and create a corresponding repository on GitHub.
- Secure loading of API credentials using `python-dotenv` from a `~/.env` file in the user's home directory.
- An example script (`14_change_name_servers_to_cloudflare.py`) demonstrating how to change domain nameservers to Cloudflare's nameservers.

## Requirements

- Python 3 (tested with 3.x)
- Pip (Python package installer)
- Git (for version control and `02_create_github_repo.sh`)
- GitHub CLI (`gh`) (optional, only required for `02_create_github_repo.sh`)
- `dig` command-line tool (usually part of `dnsutils` or `bind-utils` package on Linux, built-in on macOS) for DNS check scripts.
- **Platform:**
    - The Python scripts (`porkbun_api.py`, `06_*.py`, `07_*.py`, `09_*.py`, `11_*.py`, `12_*.py`) are expected to be cross-platform (Linux, macOS, Windows).
    - The setup and verification shell scripts (`02_*.sh`, `03_*.sh`, `05_*.sh`, `10_*.sh`, `13_*.sh`) are designed for **macOS and Linux**. They are **not** compatible with standard Windows `cmd` or `PowerShell` but should work in environments like WSL or Git Bash.

## Setup

1.  **Clone the repository (if applicable).**
2.  **Create a credentials file:**
    Create a file named `.env` in your home directory (`~/.env`) with your Porkbun API keys:
    ```env
    PORKBUN_API_KEY="YOUR_API_KEY_HERE"
    PORKBUN_SECRET_KEY="YOUR_SECRET_KEY_HERE"
    ```
    Replace the placeholders with your actual keys obtained from [https://porkbun.com/account/api](https://porkbun.com/account/api).

3.  **Create Python Virtual Environment (Recommended):**
    It's best practice to use a virtual environment.
    ```bash
    bash 03_create_venv.sh
    ```
    This will create a directory like `porkbun_api_client-venv`. Activate it:
    ```bash
    source ./*-venv/bin/activate
    # On Windows (Git Bash/WSL): source ./*-venv/Scripts/activate
    ```

4.  **Install Dependencies:**
    Ensure your virtual environment is active, then run the script:
    ```bash
    bash 05_load_requirements.sh
    ```
    *Note: This script will attempt to create the venv if it doesn't exist and remind you to activate it if necessary.*

5.  **(Optional) Initialize Git and Create GitHub Repo:**
    If you want to manage this project with Git and push it to GitHub:
    ```bash
    # Example: Create a private repository under your personal account
    bash 02_create_github_repo.sh --personal --private

    # Example: Create a public repository under your work organization (requires WORK_GITHUB env var)
    # bash 02_create_github_repo.sh --work --public
    ```
    Refer to the script's comments or run it without arguments for usage details. Requires `git` and `gh` CLI to be installed and configured.

## Usage

Make sure your virtual environment is activated (`source ./*-venv/bin/activate`).

Replace `yourdomain.com` with the actual domain you want to manage in the commands below.
**Important:** Ensure API access is enabled for the target domain in the Porkbun dashboard before running scripts that modify records.

```bash
# Test API credentials with the ping endpoint
./06_try_ping_endpoint.py

# List all domains associated with the API key
./07_list_all_domains.py

# --- Test Record Management Cycle --- 

# Define the test record details (edit if needed, but keep format)
# Review ./08_dns_check_record_text.txt

# Create the test DNS record for your domain
./09_create_dns_check_record.py yourdomain.com

# Check DNS propagation for the created test record (Uses public resolvers, may take time depending on TTL and propagation - tries multiple times)
./10_verify_create_dns_check_record.sh yourdomain.com

# Delete the test DNS record via API
./11_delete_dns_check_record.py yourdomain.com

# Check Porkbun's API directly to see if the record is gone
./12_check_delete_dns_check_record.py yourdomain.com

# Verify the deletion has propagated across public DNS (Uses public resolvers, may take significant time depending on previous TTL and propagation - tries 3 times with 10 min delays)
./13_verify_delete_dns_check_record.sh yourdomain.com

# --- End Test Record Management Cycle --- 

# --- Nameserver Management ---

# Change domain nameservers to Cloudflare (uses ns1.cloudflare.com and ns2.cloudflare.com)
./14_change_name_servers_to_cloudflare.py yourdomain.com

# --- End Nameserver Management ---
```

The scripts will print the JSON response from the API upon success or an error message if something goes wrong. DNS verification scripts will report success or failure after retries.

## Extending Functionality

To add more API calls (e.g., creating/updating different DNS records):

1.  Create a new Python script (e.g., `14_create_a_record.py`).
2.  Make it executable (`chmod +x 14_create_a_record.py`).
3.  Import the `make_porkbun_request` function:
    ```python
    #!/usr/bin/env python3
    from porkbun_api import make_porkbun_request
    import requests # For exception handling
    import json     # For printing output
    import sys      # For arguments
    ```
4.  Refer to the official Porkbun API v3 documentation: [https://porkbun.com/api/json/v3/documentation](https://porkbun.com/api/json/v3/documentation)
5.  Identify the required **endpoint** (e.g., `/dns/create/:domain`).
6.  Determine the required **JSON payload** for the specific command.
7.  Accept necessary parameters (like domain, record name, content) via command-line arguments (`sys.argv`).
8.  Call the `make_porkbun_request(endpoint, payload)` function within your new script, handling potential exceptions:
    ```python
    # Example: Get domain from command line
    if len(sys.argv) < 5:
        print("Usage: ./14_create_a_record.py <domain> <name> <content> <ttl>")
        sys.exit(1)
    domain = sys.argv[1]
    record_name = sys.argv[2] # Use "" for root
    record_content = sys.argv[3]
    record_ttl = sys.argv[4]

    try:
        record_payload = { "name": record_name, "type": "A", "content": record_content, "ttl": record_ttl }
        endpoint = f"/dns/create/{domain}"
        response = make_porkbun_request(endpoint, record_payload)
        print(json.dumps(response, indent=2))
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    ```
9.  Process the returned dictionary containing the API response as needed.

## Support

Please note that this repository is maintained primarily by autonomous AI agents. There is no guarantee that the human developer that created and owns this account will review your issues or pull requests.

An AI agent may review submitted issues and pull requests. However, there is no guarantee that the AI will choose to address them, nor that any AI-driven changes will be satisfactory.

The AI first screens all submissions for malicious intent or content. Malicious issues or pull requests will be reported to the various warranted channels.
