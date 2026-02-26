#!/usr/bin/env bash
#
# MenuVi server setup script
# Run as root or with sudo on a fresh Ubuntu/Debian server
#
set -euo pipefail

APP_DIR="/var/www/menuvi"
APP_USER="www-data"
LOG_DIR="/var/log/menuvi"

echo "==> Installing system packages"
apt-get update -qq
apt-get install -y -qq python3 python3-venv python3-pip nginx

echo "==> Creating log directory"
mkdir -p "$LOG_DIR"
chown "$APP_USER:$APP_USER" "$LOG_DIR"

echo "==> Setting up app directory"
if [ ! -d "$APP_DIR/.venv" ]; then
    python3 -m venv "$APP_DIR/.venv"
fi

echo "==> Installing Python dependencies"
"$APP_DIR/.venv/bin/pip" install --quiet -r "$APP_DIR/requirements.txt"

echo "==> Creating .env if missing"
if [ ! -f "$APP_DIR/.env" ]; then
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    # Generate a random secret key
    SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "s/change-me-to-a-random-string/$SECRET/" "$APP_DIR/.env"
fi

echo "==> Ensuring instance directory exists"
mkdir -p "$APP_DIR/instance"
chown -R "$APP_USER:$APP_USER" "$APP_DIR/instance"

echo "==> Seeding database"
cd "$APP_DIR"
sudo -u "$APP_USER" FLASK_APP=menuvi "$APP_DIR/.venv/bin/flask" seed

echo "==> Installing systemd service"
cp "$APP_DIR/deploy/menuvi.service" /etc/systemd/system/menuvi.service
systemctl daemon-reload
systemctl enable menuvi
systemctl restart menuvi

echo "==> Installing nginx config"
cp "$APP_DIR/deploy/menuvi.nginx" /etc/nginx/sites-available/menuvi
ln -sf /etc/nginx/sites-available/menuvi /etc/nginx/sites-enabled/menuvi
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo ""
echo "==> Done!"
echo "    App running at http://$(hostname -I | awk '{print $1}')"
echo ""
echo "    Next steps:"
echo "    1. Create a superadmin user:"
echo "       sudo -u $APP_USER FLASK_APP=menuvi $APP_DIR/.venv/bin/flask create-superadmin"
echo "    2. For HTTPS: sudo certbot --nginx -d menuvi.appfoundry.cc"
