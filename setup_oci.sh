#!/bin/bash
# setup_oci.sh - Configuración automática para Oracle Cloud
# Autor: Agente AI

echo "==== Iniciando Configuración Nátiva de RAMedio ===="

# 1. Actualizar el servidor (Soporta Ubuntu y Oracle Linux)
echo "1. Actualizando paquetes del sistema..."
sudo apt update && sudo apt upgrade -y || sudo dnf upgrade -y

# 2. Instalar dependencias base
echo "2. Instalando python3, pip, venv y git..."
sudo apt install -y python3 python3-pip python3-venv git nginx python3-certbot-nginx || sudo dnf install -y python3 python3-pip git nginx certbot python3-certbot-nginx

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
ExecStart=$CURRENT_DIR/.venv/bin/uvicorn api:app --host 127.0.0.1 --port 8000
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

echo "5. Configurando Nginx y obteniendo Certificado SSL (Let's Encrypt)..."
cat <<'EOF_NGINX' > ramedio.nginx
server {
    server_name ramedio.duckdns.org;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF_NGINX

sudo cp ramedio.nginx /etc/nginx/sites-available/ramedio
sudo ln -sf /etc/nginx/sites-available/ramedio /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx
sudo certbot --nginx -d ramedio.duckdns.org --non-interactive --agree-tos -m dancep.ramos@gmail.com || echo "/!\ Hubo un problema al procesar el SSL. Puede que el DNS no haya propagado aún."

echo "==================================================="
