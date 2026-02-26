#!/usr/bin/env bash
#
# Pull latest code, install deps, restart menuvi
# Files are owned by www-data in prod, so we temporarily chown to deploy
#
set -euo pipefail

APP_DIR="/var/www/menuvi"
APP_USER="www-data"
DEPLOY_USER="derek"

cd "$APP_DIR"

echo "==> Temporarily owning files for deploy"
sudo chown -R "$DEPLOY_USER:$DEPLOY_USER" "$APP_DIR"

echo "==> Pulling latest code"
git pull

echo "==> Installing dependencies"
.venv/bin/pip install --quiet -r requirements.txt

echo "==> Restoring ownership to $APP_USER"
sudo chown -R "$APP_USER:$APP_USER" "$APP_DIR"

echo "==> Restarting menuvi"
sudo systemctl restart menuvi

echo "==> Done!"
