#!/usr/bin/env bash
#
# Pull latest code, install deps, restart menuvi
#
set -euo pipefail

APP_DIR="/var/www/menuvi"
APP_USER="www-data"

cd "$APP_DIR"

echo "==> Pulling latest code"
git pull

echo "==> Installing dependencies"
.venv/bin/pip install --quiet -r requirements.txt

echo "==> Restarting menuvi"
sudo systemctl restart menuvi

echo "==> Done!"
