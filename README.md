# Porkbun API v3 Client

# #authored-by-ai #gemini-2.5-pro
# #autonomous-ai #cursor
# SPDX-License-Identifier: MIT

This account was created and is owned by a real human, however, be advised that THIS REPO WAS AUTONOMOUSLY PUBLISHED BY AN AI via execution of ./02_create_github_repo.sh --personal --public

This project provides a basic framework for interacting with the Porkbun API v3 using direct HTTP requests in Python.

## Overview

Instead of relying on third-party client libraries, this project uses the standard `requests` library to make POST calls to the official Porkbun API v3 endpoints ([https://api.porkbun.com/api/json/v3/documentation](https://api.porkbun.com/api/json/v3/documentation)).

It includes:
- A core Python module (`porkbun_api.py`) containing the helper function `make_porkbun_request` for authenticated API calls and credential loading.
- An example script (`06_try_ping_endpoint.py`) demonstrating how to use the module to ping the API.
- An example script (`07_list_all_domains.py`) demonstrating how to use the module to list all domains.
- Dependency management via `04_requirements.txt`.
- A shell script (`03_create_venv.sh`) to create a Python virtual environment.
- A shell script (`05_load_requirements.sh`) to install dependencies into the virtual environment.
- An optional shell script (`02_create_github_repo.sh`) to initialize a git repository and create a corresponding repository on GitHub.
- Secure loading of API credentials using `python-dotenv` from a `~/.env` file.

## Requirements

- Python 3 (tested with 3.x)
- Pip (Python package installer)
- Git (for version control and `02_create_github_repo.sh`)
- GitHub CLI (`gh`) (optional, only required for `02_create_github_repo.sh`)
- **Platform:**
    - The Python scripts (`porkbun_api.py`, `06_*.py`, `07_*.py`) are expected to be cross-platform (Linux, macOS, Windows).
    - The setup shell scripts (`02_*.sh`, `03_*.sh`, `05_*.sh`) are designed for **macOS and Linux**. They are **not** compatible with standard Windows `cmd` or `PowerShell` but should work in environments like WSL or Git Bash.

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

Execute the example Python scripts:

```bash
# Test API credentials with the ping endpoint
./06_try_ping_endpoint.py

# List all domains associated with the API key
./07_list_all_domains.py
```

The scripts will print the JSON response from the API upon success or an error message if something goes wrong.

## Extending Functionality

To add more API calls (e.g., creating/updating DNS records):

1.  Create a new Python script (e.g., `09_create_dns_record.py`).
2.  Make it executable (`chmod +x 09_create_dns_record.py`).
3.  Import the `make_porkbun_request` function:
    ```python
    #!/usr/bin/env python3
    from porkbun_api import make_porkbun_request
    import requests # For exception handling
    import json     # For printing output
    ```
4.  Refer to the official Porkbun API v3 documentation: [https://porkbun.com/api/json/v3/documentation](https://porkbun.com/api/json/v3/documentation)
5.  Identify the required **endpoint** (e.g., `/dns/create/yourdomain.com`).
6.  Determine the required **JSON payload** for the specific command.
7.  Call the `make_porkbun_request(endpoint, payload)` function within your new script, handling potential exceptions:
    ```python
    # Make sure your venv is active before running
    try:
        # Example payload structure - replace with actual data for the desired endpoint
        record_payload = { "name": "subdomain", "type": "A", "content": "1.2.3.4" }
        # Replace endpoint and domain as needed
        response = make_porkbun_request("/dns/create/yourdomain.com", record_payload)
        print(json.dumps(response, indent=2))
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    ```
8.  Process the returned dictionary containing the API response as needed.

## Support

Please note that this repository is maintained primarily by autonomous AI agents. There is no guarantee that the human developer that created and owns this account will review your issues or pull requests.

An AI agent may review submitted issues and pull requests. However, there is no guarantee that the AI will choose to address them, nor that any AI-driven changes will be satisfactory.

The AI first screens all submissions for malicious intent or content. Malicious issues or pull requests will be reported to the various warranted channels.
