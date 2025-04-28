#!/usr/bin/env python3

# #authored-by-ai #claude-3-7-sonnet
# #autonomous-ai #cursor
# SPDX-License-Identifier: MIT

"""
Script to verify nameserver propagation globally after changing to Cloudflare nameservers.
A companion to 14_change_name_servers_to_cloudflare.py that provides a visual dashboard
of propagation status across global DNS servers.

Ensure your virtual environment is active.
Usage: ./15_verify_name_server_propagation.py yourdomain.com [interval] [timeout]
    interval: Optional. Check every N seconds (default: 0 - single check)
    timeout: Optional. Timeout for each DNS query in seconds (default: 5)
"""

import sys
import subprocess
import json
import time
import datetime
from concurrent.futures import ThreadPoolExecutor
import random
import os

# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    GRAY = "\033[37m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    
# Cloudflare's nameservers - ** MUST MATCH THOSE IN 14_change_name_servers_to_cloudflare.py **
CLOUDFLARE_NS = [
    "kellen.ns.cloudflare.com", # Cloudflare's nameservers - ** MUST MATCH THOSE IN 14_change_name_servers_to_cloudflare.py **
    "melina.ns.cloudflare.com" # Cloudflare's nameservers - ** MUST MATCH THOSE IN 14_change_name_servers_to_cloudflare.py **
]

# Primary DNS servers to query
PRIMARY_DNS_SERVERS = {
    "North America": [
        {"name": "Cloudflare", "ip": "1.1.1.1"},
        {"name": "Google", "ip": "8.8.8.8"},
        {"name": "OpenDNS US", "ip": "208.67.222.222"},
        {"name": "Quad9", "ip": "9.9.9.9"}
    ],
    "Europe": [
        {"name": "France DNS", "ip": "212.27.40.240"},
        {"name": "Germany DNS", "ip": "194.150.168.168"},
        {"name": "UK DNS", "ip": "156.154.70.1"}
    ],
    "Asia": [
        {"name": "Singapore DNS", "ip": "202.136.162.11"},
        {"name": "Japan DNS", "ip": "203.112.2.4"},
        {"name": "Hong Kong DNS", "ip": "205.252.144.228"}
    ],
    "Oceania": [
        {"name": "Australia DNS", "ip": "61.8.0.113"}
    ],
    "South America": [
        {"name": "Brazil DNS", "ip": "200.221.11.101"}
    ]
}

# Backup DNS servers to try if primary servers are not responsive
BACKUP_DNS_SERVERS = {
    "North America": [
        {"name": "Level3", "ip": "4.2.2.2"},
        {"name": "Verisign", "ip": "64.6.64.6"},
        {"name": "Comodo", "ip": "8.26.56.26"},
        {"name": "AT&T", "ip": "68.94.156.1"}
    ],
    "Europe": [
        {"name": "Swiss DNS", "ip": "77.109.138.45"},
        {"name": "Dutch DNS", "ip": "195.46.39.39"},
        {"name": "Italy DNS", "ip": "193.70.152.25"}
    ],
    "Asia": [
        {"name": "India DNS", "ip": "210.5.56.108"}, 
        {"name": "Taiwan DNS", "ip": "101.101.101.101"},
        {"name": "Korea DNS", "ip": "164.124.101.2"}
    ],
    "Oceania": [
        {"name": "NZ DNS", "ip": "219.88.200.63"},
        {"name": "AU Telstra", "ip": "61.9.133.1"}
    ],
    "South America": [
        {"name": "Argentina DNS", "ip": "200.69.193.1"},
        {"name": "Colombia DNS", "ip": "200.116.213.240"}
    ]
}

def run_dig_command(domain, record_type, dns_server, timeout=5):
    """
    Run a dig command against the specified DNS server for the domain and record type.
    
    Args:
        domain (str): Domain name to query
        record_type (str): DNS record type (A, MX, TXT, CNAME, NS, etc)
        dns_server (dict): Dictionary with DNS server info (name and ip)
        timeout (int): Timeout for the query in seconds
        
    Returns:
        dict: Result with server info and dig output
    """
    server_ip = dns_server["ip"]
    server_name = dns_server["name"]
    
    # Build dig command
    dig_cmd = ["dig", "@" + server_ip, domain, record_type, "+short", f"+time={timeout}"]
    
    try:
        # Run dig command and capture output
        result = subprocess.run(dig_cmd, capture_output=True, text=True, timeout=timeout+1)
        
        # Parse the output
        output = result.stdout.strip()
        success = result.returncode == 0
        
        # Format the result
        if output:
            lines = output.split('\n')
            answers = lines
        else:
            answers = []
            
        return {
            "server": server_name,
            "server_ip": server_ip,
            "region": next((region for region, servers in PRIMARY_DNS_SERVERS.items() 
                           if any(s["ip"] == server_ip for s in servers)), 
                          next((region for region, servers in BACKUP_DNS_SERVERS.items() 
                               if any(s["ip"] == server_ip for s in servers)), "Unknown")),
            "success": success,
            "answers": answers,
            "error": result.stderr.strip() if result.stderr else None,
            "is_backup": not any(s["ip"] == server_ip for region, servers in PRIMARY_DNS_SERVERS.items() for s in servers)
        }
        
    except subprocess.TimeoutExpired:
        return {
            "server": server_name,
            "server_ip": server_ip,
            "region": next((region for region, servers in PRIMARY_DNS_SERVERS.items() 
                           if any(s["ip"] == server_ip for s in servers)), 
                          next((region for region, servers in BACKUP_DNS_SERVERS.items() 
                               if any(s["ip"] == server_ip for s in servers)), "Unknown")),
            "success": False,
            "answers": [],
            "error": "Timeout querying DNS server",
            "is_backup": not any(s["ip"] == server_ip for region, servers in PRIMARY_DNS_SERVERS.items() for s in servers)
        }
    except Exception as e:
        return {
            "server": server_name,
            "server_ip": server_ip,
            "region": next((region for region, servers in PRIMARY_DNS_SERVERS.items() 
                           if any(s["ip"] == server_ip for s in servers)), 
                          next((region for region, servers in BACKUP_DNS_SERVERS.items() 
                               if any(s["ip"] == server_ip for s in servers)), "Unknown")),
            "success": False,
            "answers": [],
            "error": str(e),
            "is_backup": not any(s["ip"] == server_ip for region, servers in PRIMARY_DNS_SERVERS.items() for s in servers)
        }

def check_command_exists(command):
    """Check if a command exists on the system."""
    try:
        subprocess.run(["which", command], capture_output=True, check=True)
        return True
    except:
        return False

def verify_nameserver_propagation(domain, timeout=5):
    """
    Verify nameserver propagation by querying multiple global DNS servers.
    Try backup servers for regions with failed primary servers.
    
    Args:
        domain (str): Domain name to check
        timeout (int): Timeout for each query in seconds
        
    Returns:
        list: Results from all DNS servers
    """
    # First, gather all primary servers
    all_primary_servers = []
    for region, servers in PRIMARY_DNS_SERVERS.items():
        all_primary_servers.extend(servers)
    
    # Use ThreadPoolExecutor to query all primary DNS servers in parallel
    with ThreadPoolExecutor(max_workers=min(20, len(all_primary_servers))) as executor:
        primary_results = list(executor.map(
            lambda server: run_dig_command(domain, "NS", server, timeout),
            all_primary_servers
        ))
    
    # Group primary results by region to identify which regions need backup servers
    primary_by_region = {}
    for result in primary_results:
        region = result["region"]
        if region not in primary_by_region:
            primary_by_region[region] = []
        primary_by_region[region].append(result)
    
    # Determine which regions need backup servers
    backup_servers_to_try = []
    for region, results in primary_by_region.items():
        # If all servers in the region failed or had no answers, try a backup
        if not any(r["success"] and r["answers"] for r in results):
            if region in BACKUP_DNS_SERVERS and BACKUP_DNS_SERVERS[region]:
                # Choose a random backup server from this region
                backup_servers_to_try.append(random.choice(BACKUP_DNS_SERVERS[region]))
    
    # Query backup servers if needed
    backup_results = []
    if backup_servers_to_try:
        with ThreadPoolExecutor(max_workers=min(10, len(backup_servers_to_try))) as executor:
            backup_results = list(executor.map(
                lambda server: run_dig_command(domain, "NS", server, timeout),
                backup_servers_to_try
            ))
    
    # Combine results and sort by region
    all_results = primary_results + backup_results
    all_results.sort(key=lambda x: (x["region"], x["server"]))
    
    return all_results

def is_cloudflare_nameserver(nameserver):
    """Check if a nameserver is a Cloudflare nameserver."""
    nameserver = nameserver.lower().rstrip('.')
    return any(ns.lower() == nameserver for ns in CLOUDFLARE_NS)

def display_nameserver_dashboard(results, domain, start_time=None, check_count=1):
    """
    Display a dashboard of nameserver propagation status with colors and visual indicators.
    
    Args:
        results (list): DNS query results
        domain (str): Domain being checked
        start_time (float): When the first check started (for continuous monitoring)
        check_count (int): Number of checks performed so far
    """
    # Clear the screen for better dashboard view (only if not the first run)
    if check_count > 1 and sys.stdout.isatty():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elapsed = f" (monitoring for {int(time.time() - start_time)} seconds)" if start_time else ""
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== NAMESERVER PROPAGATION DASHBOARD ===={Colors.RESET}")
    print(f"{Colors.BOLD}Domain:{Colors.RESET} {domain}")
    print(f"{Colors.BOLD}Time:{Colors.RESET} {current_time}{elapsed}")
    print(f"{Colors.BOLD}Check #{Colors.RESET} {check_count}\n")
    
    # Group results by region
    by_region = {}
    for result in results:
        region = result["region"]
        if region not in by_region:
            by_region[region] = []
        by_region[region].append(result)
    
    # Propagation counters
    cloudflare_propagated = 0
    total_responsive_servers = 0
    
    # Display results by region
    for region, region_results in by_region.items():
        print(f"{Colors.BOLD}== {region} =={Colors.RESET}")
        
        for res in region_results:
            # Count responsive servers
            if res["success"]:
                total_responsive_servers += 1
            
            # Determine status indicators and colors
            if not res["success"]:
                status_color = Colors.RED
                status_icon = "✗"
                status_text = "ERROR"
            elif not res["answers"]:
                status_color = Colors.YELLOW
                status_icon = "?"
                status_text = "NO DATA"
            else:
                # Check if any answer is a Cloudflare nameserver
                has_cloudflare = any(is_cloudflare_nameserver(answer) for answer in res["answers"])
                if has_cloudflare:
                    cloudflare_propagated += 1
                    status_color = Colors.GREEN
                    status_icon = "✓"
                    status_text = "CLOUDFLARE"
                else:
                    status_color = Colors.PURPLE
                    status_icon = "!"
                    status_text = "OLD NS"
            
            # Mark backup servers
            backup_indicator = f" {Colors.BLUE}[BACKUP]{Colors.RESET}" if res.get("is_backup") else ""
            
            # Print the server status line
            print(f"{status_color}{status_icon} {res['server']} ({res['server_ip']}){backup_indicator} - {status_text}{Colors.RESET}")
            
            # Print the answers or error
            if res["success"]:
                if res["answers"]:
                    for answer in res["answers"]:
                        ns_color = Colors.GREEN if is_cloudflare_nameserver(answer) else Colors.GRAY
                        print(f"  └─ {ns_color}{answer}{Colors.RESET}")
                else:
                    print(f"  └─ {Colors.GRAY}No records returned{Colors.RESET}")
            else:
                print(f"  └─ {Colors.GRAY}Error: {res['error']}{Colors.RESET}")
    
    # Calculate propagation percentage
    if total_responsive_servers > 0:
        propagation_pct = (cloudflare_propagated / total_responsive_servers) * 100
    else:
        propagation_pct = 0
    
    # Display progress bar
    bar_width = 50
    filled_width = int(bar_width * propagation_pct / 100)
    bar = "█" * filled_width + "░" * (bar_width - filled_width)
    
    print(f"\n{Colors.BOLD}=== PROPAGATION SUMMARY ==={Colors.RESET}")
    print(f"{Colors.BOLD}Cloudflare NS detected:{Colors.RESET} {cloudflare_propagated}/{total_responsive_servers} servers ({propagation_pct:.1f}%)")
    print(f"{Colors.BOLD}Progress:{Colors.RESET} |{Colors.GREEN}{bar}{Colors.RESET}| {propagation_pct:.1f}%")
    
    # Estimate completion
    if 0 < propagation_pct < 100:
        # Very rough estimate based on typical propagation times
        if propagation_pct < 30:
            est_hours = "24-48"
        elif propagation_pct < 60:
            est_hours = "12-24"
        elif propagation_pct < 90:
            est_hours = "4-12"
        else:
            est_hours = "1-4"
            
        print(f"{Colors.BOLD}Estimated completion:{Colors.RESET} Approximately {est_hours} hours remaining")
    elif propagation_pct >= 100:
        print(f"{Colors.BOLD}Status:{Colors.RESET} {Colors.GREEN}PROPAGATION COMPLETE!{Colors.RESET}")
    else:
        print(f"{Colors.BOLD}Status:{Colors.RESET} {Colors.YELLOW}No propagation detected yet{Colors.RESET}")
    
    # Some tips
    if propagation_pct < 100:
        print(f"\n{Colors.YELLOW}NOTE:{Colors.RESET} DNS changes can take up to 48 hours to fully propagate worldwide.")
        print(f"      Some ISPs and DNS services cache results longer than others.")
        print(f"      Run this script periodically to track progress.")
    
    return cloudflare_propagated, total_responsive_servers

if __name__ == "__main__":
    # Check if dig is installed
    if not check_command_exists("dig"):
        print(f"{Colors.RED}Error: The 'dig' command is not installed or not found in PATH.{Colors.RESET}")
        print("Please install dig (usually part of the 'dnsutils' or 'bind-utils' package).")
        sys.exit(1)
        
    # Parse command line arguments
    if len(sys.argv) < 2:
        print(f"{Colors.BOLD}Usage:{Colors.RESET} {sys.argv[0]} <domain> [interval] [timeout]")
        print(f"  domain: Domain to check nameserver propagation for")
        print(f"  interval: Optional. Check every N seconds (default: 0 - single check)")
        print(f"  timeout: Optional. Timeout for each DNS query in seconds (default: 5)")
        print(f"\n{Colors.BOLD}Examples:{Colors.RESET}")
        print(f"  ./15_verify_name_server_propagation.py example.com")
        print(f"  ./15_verify_name_server_propagation.py example.com 300")
        print(f"  ./15_verify_name_server_propagation.py example.com 300 3")
        sys.exit(1)
    
    domain = sys.argv[1]
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    timeout = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    
    print(f"{Colors.BOLD}Verifying nameserver propagation for {domain}...{Colors.RESET}")
    print(f"Checking if {Colors.GREEN}Cloudflare nameservers{Colors.RESET} have propagated worldwide...")
    
    # Start tracking with timestamps for continuous monitoring
    start_time = time.time() if interval > 0 else None
    check_count = 1
    
    try:
        while True:
            # Clear the screen after the first run for better dashboard display
            if check_count > 1 and sys.stdout.isatty():
                os.system('cls' if os.name == 'nt' else 'clear')
                
            # Start tracking
            check_start_time = time.time()
            results = verify_nameserver_propagation(domain, timeout)
            elapsed_time = time.time() - check_start_time
            
            # Display dashboard 
            cloudflare_count, total_count = display_nameserver_dashboard(
                results, domain, start_time, check_count
            )
            
            print(f"\nCheck completed in {elapsed_time:.2f} seconds.")
            
            # If no interval or propagation is complete, exit
            if interval <= 0 or (total_count > 0 and cloudflare_count == total_count):
                break
                
            # Show next check time
            next_check = datetime.datetime.now() + datetime.timedelta(seconds=interval)
            print(f"\n{Colors.BOLD}Next check at:{Colors.RESET} {next_check.strftime('%H:%M:%S')}")
            print(f"Press Ctrl+C to stop monitoring...")
            
            # Wait for next interval
            time.sleep(interval)
            check_count += 1
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Monitoring stopped by user.{Colors.RESET}")
        
    # Final message
    if cloudflare_count == total_count and total_count > 0:
        print(f"\n{Colors.GREEN}SUCCESS: Cloudflare nameservers are fully propagated!{Colors.RESET}")
    elif cloudflare_count > 0:
        print(f"\n{Colors.YELLOW}IN PROGRESS: Cloudflare nameservers are partially propagated.{Colors.RESET}")
        print(f"Run this script again later to check progress.")
    else:
        print(f"\n{Colors.RED}NOT STARTED: Cloudflare nameservers have not propagated yet.{Colors.RESET}")
        print(f"Make sure you've run 14_change_name_servers_to_cloudflare.py successfully.") 