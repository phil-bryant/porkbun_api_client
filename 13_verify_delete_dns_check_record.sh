#!/bin/bash
# #authored-by-ai #gemini-2.5-pro
# #autonomous-ai #cursor
# SPDX-License-Identifier: MIT

# Script to verify DNS propagation for the *deletion* of a specific record.
# Reads record details from 08_dns_check_record_text.txt and takes domain as argument.
# Usage: ./13_verify_delete_dns_check_record.sh yourdomain.com

# --- Configuration ---
CONFIG_FILE="08_dns_check_record_text.txt"
DNS_SERVERS=("8.8.8.8" "1.1.1.1" "9.9.9.9") # Google, Cloudflare, Quad9
MAX_ATTEMPTS=3
SLEEP_DURATION=600 # 10 minutes between attempts
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
    source "$1"
    # Validate required variables are set
    if [ -z "$RECORD_NAME" ] || [ -z "$RECORD_TYPE" ]; then
        echo "Error: Config file $1 is missing required variables (RECORD_NAME, RECORD_TYPE)."
        exit 1
    fi
}

# Load the configuration
source_config "$CONFIG_FILE"

# Construct the full record name to check
if [ -z "$RECORD_NAME" ]; then
    FQDN="$DOMAIN"
else
    FQDN="${RECORD_NAME}.${DOMAIN}"
fi
# --- End Load Config ---

echo "--- DNS Deletion Verification ---"
echo "Domain:        $DOMAIN"
echo "Record Name:   $FQDN"
echo "Record Type:   $RECORD_TYPE"
echo "Verifying record is DELETED from servers: ${DNS_SERVERS[*]}"
echo "Max attempts: $MAX_ATTEMPTS, Delay: ${SLEEP_DURATION}s"
echo "-----------------------------------"

# Get the number of servers
num_servers=${#DNS_SERVERS[@]}

# Initialize server status array (parallel to DNS_SERVERS)
# 0 = Pending, 1 = Confirmed Deleted, 2 = Still Found, 3 = Query Error
server_status=()
for (( i=0; i<num_servers; i++ )); do
    server_status[$i]=0 # Pending
done

confirmed_deleted_count=0
attempts=0

while [ $attempts -lt $MAX_ATTEMPTS ] && [ $confirmed_deleted_count -lt $num_servers ]; do
    attempts=$((attempts + 1))
    echo -e "\nAttempt $attempts of $MAX_ATTEMPTS..."

    for (( i=0; i<num_servers; i++ )); do
        server=${DNS_SERVERS[$i]}
        status=${server_status[$i]}

        # Skip if already confirmed deleted on this server
        if [[ $status -eq 1 ]]; then # Confirmed Deleted
            echo "  [✓] Server $server: Already confirmed deleted."
            continue
        fi

        echo "  [?] Querying $server for $FQDN ($RECORD_TYPE) - expecting NOT FOUND..."
        # Use +short for cleaner output, redirect stderr to /dev/null
        # Use timeout to prevent hanging
        query_result=$(timeout 5 dig @"$server" "$FQDN" "$RECORD_TYPE" +short 2>/dev/null)
        dig_exit_code=$?

        # Check if dig command finished and the result is empty (record not found)
        # A non-zero exit code from dig (like NXDOMAIN) also indicates not found.
        # If exit code is 0 but result is empty, that also means not found.
        if [[ $dig_exit_code -ne 0 || ( $dig_exit_code -eq 0 && -z "$query_result" ) ]]; then
            echo "      --> Success: Record NOT FOUND as expected."
            server_status[$i]=1 # Confirmed Deleted
        elif [[ $dig_exit_code -eq 0 && -n "$query_result" ]]; then
             echo "      --> Failed: Record IS STILL FOUND on $server."
             echo "          Got: $query_result"
             server_status[$i]=2 # Still Found
        else # Should not happen, treat as query error just in case
             echo "      --> Warning: Query potentially failed or gave unexpected output on $server (Exit: $dig_exit_code)."
             server_status[$i]=3 # Query Error / Unexpected
        fi
    done

    # Recalculate confirmed_deleted_count
    current_confirmed_deleted_count=0
    for (( i=0; i<num_servers; i++ )); do
        if [[ ${server_status[$i]} -eq 1 ]]; then # Confirmed Deleted
            current_confirmed_deleted_count=$((current_confirmed_deleted_count + 1))
        fi
    done
    confirmed_deleted_count=$current_confirmed_deleted_count

    if [ $confirmed_deleted_count -eq $num_servers ]; then
        echo -e "\nAll servers confirmed the record is deleted!"
        break
    fi

    if [ $attempts -lt $MAX_ATTEMPTS ]; then
        echo -e "\nRecord still found or query errors on some servers ($confirmed_deleted_count / $num_servers confirmed deleted). Waiting ${SLEEP_DURATION}s..."
        sleep $SLEEP_DURATION
    fi
done

echo -e "\n--- Final Status (${attempts}/${MAX_ATTEMPTS} attempts) ---"
final_success_count=0 # Count servers where deletion is confirmed
any_still_found=0

for (( i=0; i<num_servers; i++ )); do
    server=${DNS_SERVERS[$i]}
    status_code=${server_status[$i]}
    status_msg="Unknown"
    icon="[?]"

    case $status_code in
        0) status_msg="Pending (Not Checked/Reached)"; icon="[?]" ;;
        1) status_msg="Confirmed Deleted"; icon="[✓]"; final_success_count=$((final_success_count + 1)) ;;
        2) status_msg="Failed: Record STILL FOUND"; icon="[✗]"; any_still_found=1 ;; # Flag if any server still has it
        3) status_msg="Warning: Query Error/Unexpected"; icon="[!]" ;;
    esac

    echo "$icon Server $server: $status_msg"
done
echo "-----------------------------------"

if [ $final_success_count -eq $num_servers ]; then
    echo "Success: Record '$FQDN' ($RECORD_TYPE) confirmed DELETED on all servers."
    exit 0
elif [ $any_still_found -eq 1 ]; then
     echo "Failed: Record '$FQDN' ($RECORD_TYPE) was still found on at least one server after $attempts attempts."
     exit 1
else
    echo "Warning: Deletion could not be fully confirmed on all servers due to query errors after $attempts attempts."
    exit 2 # Different exit code for uncertainty
fi 