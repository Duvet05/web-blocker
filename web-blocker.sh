#!/bin/bash

# Verificar permisos de superusuario
if [ "$EUID" -ne 0 ]; then
    echo "Por favor, ejecuta este script como superusuario (sudo)."
    exit 1
fi

# Rutas y configuraciones
HOSTS_FILE="/etc/hosts"
CONFIG_FILE="/etc/web-blocker/sites.conf"
IPTABLES_RULES="/etc/iptables/rules.v4"
PYTHON_SCRIPT="/usr/lib/web-blocker/web-blocker.py"

# Lista de sitios por defecto (puede sobreescribirse con CONFIG_FILE)
SITES=("facebook.com" "twitter.com" "instagram.com")

# Función para bloquear en /etc/hosts
block_hosts() {
    echo "Bloqueando sitios en $HOSTS_FILE..."
    for site in "${SITES[@]}"; do
        if ! grep -q "$site" "$HOSTS_FILE"; then
            echo "127.0.0.1 $site" >> "$HOSTS_FILE"
            echo "127.0.0.1 www.$site" >> "$HOSTS_FILE"
        fi
    done
}

# Función para bloquear con iptables
block_iptables() {
    echo "Configurando reglas de iptables..."
    # Obtener IPs desde el script Python (simulado aquí)
    IPS=$("$PYTHON_SCRIPT" --get-ips "${SITES[@]}")
    for ip in $IPS; do
        iptables -A OUTPUT -d "$ip" -p tcp -j DROP
        iptables -A OUTPUT -d "$ip" -p udp -j DROP
    done
    # Guardar reglas
    iptables-save > "$IPTABLES_RULES"
}

# Función para bloquear con ufw (si está instalado)
block_ufw() {
    if command -v ufw >/dev/null 2>&1; then
        echo "Configurando reglas de ufw..."
        for site in "${SITES[@]}"; do
            ufw deny out to "$site"
        done
        ufw reload
    else
        echo "ufw no está instalado, omitiendo esta capa de bloqueo."
    fi
}

# Cargar sitios desde el archivo de configuración si existe
if [ -f "$CONFIG_FILE" ]; then
    mapfile -t SITES < "$CONFIG_FILE"
fi

# Ejecutar bloqueos
block_hosts
block_iptables
block_ufw

echo "Bloqueo completado. Sitios bloqueados: ${SITES[@]}"