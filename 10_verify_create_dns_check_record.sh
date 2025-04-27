#!/bin/bash
# #authored-by-ai #gemini-2.5-pro
# #autonomous-ai #cursor
# SPDX-License-Identifier: MIT

# Script to verify DNS propagation for a specific record.
# Reads record details from 08_dns_check_record_text.txt and takes domain as argument.
# Usage: ./10_verify_create_dns_check_record.sh yourdomain.com

# --- Configuration ---
CONFIG_FILE="08_dns_check_record_text.txt"
DNS_SERVERS=("8.8.8.8" "1.1.1.1" "9.9.9.9") # Google, Cloudflare, Quad9
MAX_ATTEMPTS=5 # 5 attempts
SLEEP_DURATION=60 # 60 seconds between attempts (Total ~5 minutes)
# --- End Configuration ---

# --- Argument Parsing ---
if [ -z "$1" ]; then
  echo "Usage: $0 <yourdomain.com>"
  exit 1
fi
DOMAIN=$1
# --- End Argument Parsing ---

# --- Load Config --- Function to load config from file
source_config() {
    if [ ! -f "$1" ]; then
        echo "Error: Config file not found at $1"
        exit 1
    fi
    # Source the file to load variables
    # Important: Ensure the config file uses bash-compatible variable assignments
    # e.g., KEY="value" (no spaces around =)
    source "$1"

    # Validate required variables are set
    if [ -z "$RECORD_NAME" ] || [ -z "$RECORD_TYPE" ] || [ -z "$RECORD_CONTENT" ]; then
        echo "Error: Config file $1 is missing required variables (RECORD_NAME, RECORD_TYPE, RECORD_CONTENT)."
        exit 1
    fi
}

# Load the configuration
source_config "$CONFIG_FILE"

# Construct the full record name to check
# Handle root domain case where name might be empty
if [ -z "$RECORD_NAME" ]; then
    FQDN="$DOMAIN"
else
    FQDN="${RECORD_NAME}.${DOMAIN}"
fi
# --- End Load Config ---

echo "--- DNS Propagation Check ---"
echo "Domain:        $DOMAIN"
echo "Record Name:   $FQDN"
echo "Record Type:   $RECORD_TYPE"
echo "Expected Data: $RECORD_CONTENT"
echo "Checking against servers: ${DNS_SERVERS[*]}"
echo "Max attempts: $MAX_ATTEMPTS, Delay: ${SLEEP_DURATION}s"
echo "-----------------------------"

# Get the number of servers
num_servers=${#DNS_SERVERS[@]}

# Initialize server status array (parallel to DNS_SERVERS)
# 0 = Pending, 1 = Success, 2 = Failed (Query Error), 3 = Failed (No Match)
server_status=()
for (( i=0; i<num_servers; i++ )); do
    server_status[$i]=0 # Pending
done

found_count=0
attempts=0

while [ $attempts -lt $MAX_ATTEMPTS ] && [ $found_count -lt $num_servers ]; do
    attempts=$((attempts + 1))
    echo -e "\nAttempt $attempts of $MAX_ATTEMPTS..."

    for (( i=0; i<num_servers; i++ )); do
        server=${DNS_SERVERS[$i]}
        status=${server_status[$i]}

        # Skip if already found on this server in a previous attempt
        if [[ $status -eq 1 ]]; then # Success
            echo "  [✓] Server $server: Already confirmed."
            continue
        fi

        echo "  [?] Querying $server for $FQDN ($RECORD_TYPE)..."
        # Use +short for cleaner output, redirect stderr to /dev/null
        # Use timeout to prevent hanging on unresponsive servers
        query_result=$(timeout 5 dig @"$server" "$FQDN" "$RECORD_TYPE" +short 2>/dev/null)
        dig_exit_code=$?

        # Check if dig command succeeded and result matches
        # Note: Use == for string comparison in bash
        if [[ $dig_exit_code -eq 0 && "$query_result" == "$RECORD_CONTENT" ]]; then
            echo "      --> Success: Found matching record."
            server_status[$i]=1 # Success
        elif [[ $dig_exit_code -ne 0 ]]; then
             echo "      --> Failed: Query timed out or dig error on $server (Exit Code: $dig_exit_code)."
             server_status[$i]=2 # Failed (Query Error)
        else
            echo "      --> Failed: Record not found or mismatch on $server."
            echo "          Expected: $RECORD_CONTENT"
            echo "          Got:      $query_result"
            server_status[$i]=3 # Failed (No Match)
        fi
    done

    # Recalculate found_count based on current success statuses
    current_found_count=0
    for (( i=0; i<num_servers; i++ )); do
        if [[ ${server_status[$i]} -eq 1 ]]; then # Success
            current_found_count=$((current_found_count + 1))
        fi
    done
    found_count=$current_found_count

    if [ $found_count -eq $num_servers ]; then
        echo -e "\nAll servers confirmed the record!"
        break
    fi

    if [ $attempts -lt $MAX_ATTEMPTS ]; then
        echo -e "\nRecord not yet confirmed on all servers ($found_count / $num_servers). Waiting ${SLEEP_DURATION}s before next attempt..."
        sleep $SLEEP_DURATION
    fi
done

echo -e "\n--- Final Status (${attempts}/${MAX_ATTEMPTS} attempts) ---"
final_success_count=0
for (( i=0; i<num_servers; i++ )); do
    server=${DNS_SERVERS[$i]}
    status_code=${server_status[$i]}
    status_msg="Unknown"
    icon="[?]"

    case $status_code in
        0) status_msg="Pending (Not Checked/Reached)"; icon="[?]" ;;
        1) status_msg="Success"; icon="[✓]"; final_success_count=$((final_success_count + 1)) ;;
        2) status_msg="Failed (Query Error)"; icon="[✗]" ;;
        3) status_msg="Failed (No Match)"; icon="[✗]" ;;
    esac

    echo "$icon Server $server: $status_msg"
done
echo "-----------------------------"

if [ $final_success_count -eq $num_servers ]; then
    echo "Success: Record '$FQDN' ($RECORD_TYPE) with content '$RECORD_CONTENT' confirmed on all servers."
    exit 0
else
    echo "Failed: Record '$FQDN' ($RECORD_TYPE) not confirmed on all servers after $attempts attempts."
    exit 1
fi 