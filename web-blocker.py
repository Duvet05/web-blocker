#!/usr/bin/env python3

import sys
import socket
import argparse
import requests

# Lista de sitios por defecto
DEFAULT_SITES = ["facebook.com", "twitter.com", "instagram.com"]

# Fuentes de listas de bloqueo (ejemplo)
BLOCKLIST_URLS = {
    "easylist": "https://easylist.to/easylist/easylist.txt",
    "peterlowe": "https://pgl.yoyo.org/adservers/serverlist.php?format=hosts"
}

def get_ips(sites):
    """Resuelve las IPs de los sitios dados."""
    ips = set()
    for site in sites:
        try:
            ip = socket.gethostbyname(site)
            ips.add(ip)
        except socket.gaierror:
            print(f"No se pudo resolver la IP de {site}", file=sys.stderr)
    return ips

def fetch_blocklist(url):
    """Descarga y parsea una lista de bloqueo desde una URL."""
    response = requests.get(url)
    response.raise_for_status()
    # Simplificación: asumimos que cada línea tiene un dominio después de '127.0.0.1'
    return [line.split()[1] for line in response.text.splitlines() if line.startswith("127.0.0.1")]

def main():
    parser = argparse.ArgumentParser(description="Herramienta para bloquear sitios web.")
    parser.add_argument("--get-ips", nargs="+", help="Obtener IPs de los sitios dados")
    parser.add_argument("--list", choices=BLOCKLIST_URLS.keys(), help="Descargar una lista de bloqueo")
    args = parser.parse_args()

    if args.get_ips:
        ips = get_ips(args.get_ips)
        print(" ".join(ips))
    elif args.list:
        sites = fetch_blocklist(BLOCKLIST_URLS[args.list])
        print("\n".join(sites))

if __name__ == "__main__":
    main()