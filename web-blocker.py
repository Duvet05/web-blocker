#!/usr/bin/env python3

"""
Web Blocker IP Resolver (Alternative)
Dynamically resolve IPs using DNS and real traffic capture.
"""

import sys
import argparse
import subprocess
import dns.resolver
from concurrent.futures import ThreadPoolExecutor
import re
import time

# Public DNS servers
PUBLIC_DNS = [
    "8.8.8.8", "8.8.4.4", "1.1.1.1", "1.0.0.1", "9.9.9.9", "149.112.112.112",
    "208.67.222.222", "208.67.220.220", "94.140.14.14", "94.140.15.15", "4.2.2.1", "4.2.2.2"
]

def resolve_domain(domain, dns_server):
    """Resolve IPs using a DNS server."""
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [dns_server]
    ips = set()
    try:
        answers = resolver.resolve(domain, "A")
        for rdata in answers:
            ips.add(rdata.address)
    except Exception as e:
        print(f"Debug: DNS resolution failed for {domain} with {dns_server}: {e}", file=sys.stderr)
    return ips

def capture_traffic(domain, duration=5):
    """Capture outgoing traffic IPs for a domain using tcpdump."""
    ips = set()
    interface = "any"  # Adjust if you know your specific interface (e.g., wlan0, eth0)
    cmd = [
        "tcpdump", "-i", interface, "-n", "-c", "100", f"host {domain}"
    ]
    print(f"Debug: Capturing traffic for {domain}. Please open https://{domain} in your browser now.", file=sys.stderr)
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(duration)  # Give time to capture traffic
        process.terminate()
        output, error = process.communicate()
        if error:
            print(f"Debug: tcpdump error: {error.decode()}", file=sys.stderr)
        # Extract IPs from tcpdump output (e.g., "IP 192.168.1.1 > 199.232.133.140")
        ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
        for line in output.decode().splitlines():
            matches = re.findall(ip_pattern, line)
            for ip in matches:
                # Exclude local IPs (e.g., 192.168.x.x, 10.x.x.x)
                if not ip.startswith("192.168.") and not ip.startswith("10.") and not ip.startswith("172."):
                    ips.add(ip)
    except Exception as e:
        print(f"Debug: Traffic capture failed for {domain}: {e}", file=sys.stderr)
    return ips

def get_ips(sites):
    """Resolve IPs dynamically with DNS and traffic capture."""
    all_ips = set()
    domains_to_check = set()

    # Generic subdomain prefixes
    common_prefixes = ["www", "api", "m", "svc"]
    for site in sites:
        domains_to_check.add(site)
        for prefix in common_prefixes:
            domains_to_check.add(f"{prefix}.{site}")

    # Step 1: DNS Resolution
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_domain = {
            executor.submit(resolve_domain, domain, dns_server): (domain, dns_server)
            for domain in domains_to_check
            for dns_server in PUBLIC_DNS
        }
        for future in future_to_domain:
            try:
                ips = future.result()
                all_ips.update(ips)
            except Exception as e:
                domain, dns_server = future_to_domain[future]
                print(f"Debug: DNS future failed for {domain} with {dns_server}: {e}", file=sys.stderr)

    # Step 2: Traffic Capture
    for site in sites:
        traffic_ips = capture_traffic(site)
        all_ips.update(traffic_ips)

    if not all_ips:
        print("Error: No IPs resolved.", file=sys.stderr)
        sys.exit(1)

    return all_ips

def main():
    """Handle command-line arguments."""
    parser = argparse.ArgumentParser(description="Web Blocker IP Resolver (Traffic-Based)")
    parser.add_argument("--get-ips", nargs="+", help="Resolve IPs for domains.")
    args = parser.parse_args()

    if args.get_ips:
        ips = get_ips(args.get_ips)
        print(" ".join(sorted(ips)))
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()