#!/usr/bin/env python3

"""
Web Blocker IP Resolver
A utility to dynamically resolve IP addresses for specified domains using public DNS servers with extended domain variations.
"""

import sys
import argparse
import requests
import dns.resolver
from concurrent.futures import ThreadPoolExecutor

# Default sites (used as a fallback in the Bash script)
DEFAULT_SITES = ["facebook.com", "twitter.com", "instagram.com"]

# Blocklist sources (for optional list fetching)
BLOCKLIST_URLS = {
    "easylist": "https://easylist.to/easylist/easylist.txt",
    "peterlowe": "https://pgl.yoyo.org/adservers/serverlist.php?format=hosts"
}

# Public DNS servers for resolution
PUBLIC_DNS = [
    "8.8.8.8", "8.8.4.4",        # Google Public DNS
    "1.1.1.1", "1.0.0.1",        # Cloudflare
    "9.9.9.9", "149.112.112.112",# Quad9
    "208.67.222.222", "208.67.220.220",  # OpenDNS (Cisco)
    "94.140.14.14", "94.140.15.15",      # AdGuard
    "4.2.2.1", "4.2.2.2"         # Level3 (CenturyLink)
]

def resolve_domain(domain, dns_server):
    """
    Resolve IP addresses for a given domain using a specific DNS server.

    Args:
        domain (str): Domain name to resolve.
        dns_server (str): DNS server IP to use.

    Returns:
        set: Set of resolved IP addresses.
    """
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [dns_server]
    ips = set()
    try:
        answers = resolver.resolve(domain, "A")
        for rdata in answers:
            ips.add(rdata.address)
    except Exception:
        # Silently ignore errors; we'll try other servers or variations
        pass
    return ips

def get_ips(sites):
    """
    Dynamically resolve IP addresses for given sites using public DNS servers with extended domain variations.

    Args:
        sites (list): List of domain names to resolve.

    Returns:
        set: Set of all resolved IP addresses.
    """
    all_ips = set()
    domains_to_check = set()

    # Add original sites and common variations
    common_prefixes = ["www", "api", "m", "svc"]  # Generic prefixes for many sites
    for site in sites:
        domains_to_check.add(site)
        for prefix in common_prefixes:
            domains_to_check.add(f"{prefix}.{site}")

    # Resolve IPs concurrently using public DNS servers
    with ThreadPoolExecutor(max_workers=15) as executor:  # Increased workers for more domains
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
                print(f"Warning: Could not resolve {domain} with {dns_server}: {e}", file=sys.stderr)

    if not all_ips:
        print("Error: No IPs resolved for any site. Check domain names or network connectivity.", file=sys.stderr)
        sys.exit(1)

    return all_ips

def fetch_blocklist(url):
    """
    Fetch and parse a blocklist from a given URL.

    Args:
        url (str): URL of the blocklist.

    Returns:
        list: List of domain names extracted from the blocklist.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return [line.split()[1] for line in response.text.splitlines() if line.startswith("127.0.0.1")]
    except Exception as e:
        print(f"Error fetching blocklist from {url}: {e}", file=sys.stderr)
        return []

def main():
    """Main function to handle command-line arguments and execute IP resolution or blocklist fetching."""
    parser = argparse.ArgumentParser(description="Web Blocker IP Resolver - Resolve IPs or fetch blocklists dynamically.")
    parser.add_argument("--get-ips", nargs="+", help="Resolve IP addresses for the specified domains.")
    parser.add_argument("--list", choices=BLOCKLIST_URLS.keys(), help="Fetch a predefined blocklist.")
    args = parser.parse_args()

    if args.get_ips:
        ips = get_ips(args.get_ips)
        print(" ".join(sorted(ips)))  # Sort for consistency
    elif args.list:
        sites = fetch_blocklist(BLOCKLIST_URLS[args.list])
        if sites:
            print("\n".join(sites))
        else:
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()