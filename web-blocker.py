#!/usr/bin/env python3

"""
Web Blocker IP Resolver
A utility to dynamically resolve IP addresses for specified domains using public DNS and HTTP probing.
"""

import sys
import argparse
import requests
import dns.resolver
from concurrent.futures import ThreadPoolExecutor

# Public DNS servers for resolution
PUBLIC_DNS = [
    "8.8.8.8", "8.8.4.4",        # Google Public DNS
    "1.1.1.1", "1.0.0.1",        # Cloudflare
    "9.9.9.9", "149.112.112.112",# Quad9
    "208.67.222.222", "208.67.220.220",  # OpenDNS
    "94.140.14.14", "94.140.15.15",      # AdGuard
    "4.2.2.1", "4.2.2.2"         # Level3
]

def resolve_domain(domain, dns_server):
    """Resolve IP addresses for a domain using a specific DNS server."""
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [dns_server]
    ips = set()
    try:
        answers = resolver.resolve(domain, "A")
        for rdata in answers:
            ips.add(rdata.address)
    except Exception:
        pass
    return ips

def probe_domain(domain):
    """Probe a domain via HTTP HEAD request to capture additional IPs."""
    ips = set()
    try:
        response = requests.head(f"https://{domain}", timeout=5, allow_redirects=True)
        ip = response.raw._connection.sock.getpeername()[0]
        ips.add(ip)
    except Exception:
        pass
    return ips

def get_ips(sites):
    """Resolve IP addresses for sites using DNS and HTTP probing dynamically."""
    all_ips = set()
    domains_to_check = set()

    # Generic common prefixes for subdomains
    common_prefixes = ["www", "api", "m", "svc", "media", "gateway"]
    for site in sites:
        domains_to_check.add(site)
        # Add common subdomain variations dynamically
        for prefix in common_prefixes:
            domains_to_check.add(f"{prefix}.{site}")

    # Step 1: Resolve IPs via DNS
    with ThreadPoolExecutor(max_workers=15) as executor:
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

    # Step 2: Probe domains via HTTP
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_probe = {
            executor.submit(probe_domain, domain): domain
            for domain in domains_to_check
        }
        for future in future_to_probe:
            try:
                ips = future.result()
                all_ips.update(ips)
            except Exception as e:
                domain = future_to_probe[future]
                print(f"Warning: Could not probe {domain}: {e}", file=sys.stderr)

    if not all_ips:
        print("Error: No IPs resolved for any site.", file=sys.stderr)
        sys.exit(1)

    return all_ips

def main():
    """Main function to handle command-line arguments."""
    parser = argparse.ArgumentParser(description="Web Blocker IP Resolver")
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