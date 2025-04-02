#!/usr/bin/env python3

"""
Web Blocker IP Resolver
A utility to resolve IP addresses for specified domains using an external DNS server.
"""

import sys
import argparse
import requests
import dns.resolver

# Default sites (used as a fallback in the Bash script)
DEFAULT_SITES = ["facebook.com", "twitter.com", "instagram.com"]

# Blocklist sources (for optional list fetching)
BLOCKLIST_URLS = {
    "easylist": "https://easylist.to/easylist/easylist.txt",
    "peterlowe": "https://pgl.yoyo.org/adservers/serverlist.php?format=hosts"
}

def get_ips(sites):
    """
    Resolve IP addresses for given sites using an external DNS server.

    Args:
        sites (list): List of domain names to resolve.

    Returns:
        set: Set of resolved IP addresses.
    """
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ["8.8.8.8"]  # Use Google's DNS server
    ips = set()
    for site in sites:
        try:
            answers = resolver.resolve(site, "A")
            for rdata in answers:
                ips.add(rdata.address)
        except Exception as e:
            print(f"Error: Could not resolve IP for {site}: {e}", file=sys.stderr)
    return ips

def fetch_blocklist(url):
    """
    Fetch and parse a blocklist from a given URL.

    Args:
        url (str): URL of the blocklist.

    Returns:
        list: List of domain names extracted from the blocklist.
    """
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return [line.split()[1] for line in response.text.splitlines() if line.startswith("127.0.0.1")]

def main():
    """Main function to handle command-line arguments and execute IP resolution or blocklist fetching."""
    parser = argparse.ArgumentParser(description="Web Blocker IP Resolver - Resolve IPs or fetch blocklists.")
    parser.add_argument("--get-ips", nargs="+", help="Resolve IP addresses for the specified domains.")
    parser.add_argument("--list", choices=BLOCKLIST_URLS.keys(), help="Fetch a predefined blocklist.")
    args = parser.parse_args()

    if args.get_ips:
        ips = get_ips(args.get_ips)
        print(" ".join(ips))
    elif args.list:
        sites = fetch_blocklist(BLOCKLIST_URLS[args.list])
        print("\n".join(sites))
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()