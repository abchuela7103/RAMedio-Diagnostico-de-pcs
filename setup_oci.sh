#!/bin/bash
# setup_oci.sh - Configuración automática para Oracle Cloud
# Autor: Agente AI

echo "==== Iniciando Configuración Nátiva de RAMedio ===="

# 1. Actualizar el servidor (Soporta Ubuntu y Oracle Linux)
echo "1. Actualizando paquetes del sistema..."
sudo apt update && sudo apt upgrade -y || sudo dnf upgrade -y

# 2. Instalar dependencias base
echo "2. Instalando python3, pip, venv y git..."
sudo apt install -y python3 python3-pip python3-venv git || sudo dnf install -y python3 python3-pip git

# 3. Crear entorno virtual
echo "3. Creando entorno virtual e instalando requirements..."
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4. Configurar Systemd Service
echo "4. Configurando servicio de Systemd dinámicamente..."

CURRENT_DIR=$(pwd)
CURRENT_USER=$(whoami)

cat <<EOF > ramedio.service
[Unit]
Description=RAMedio FastAPI Server
After=network.target

[Service]
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR/server
ExecStart=$CURRENT_DIR/.venv/bin/uvicorn api:app --host 0.0.0.0 --port 80
Restart=always
Environment="PATH=$CURRENT_DIR/.venv/bin"

[Install]
WantedBy=multi-user.target
EOF

sudo cp ramedio.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ramedio.service
sudo systemctl restart ramedio.service

echo "==================================================="
echo "¡Listo! La API de RAMedio está corriendo en el fondo."
echo "Puedes ver el registro de actividad usando:"
echo "sudo journalctl -u ramedio.service -f"
echo "==================================================="
