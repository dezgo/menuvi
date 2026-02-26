# Deploying MenuVi

## Quick deploy to Ubuntu/Debian server

```bash
# 1. Clone the repo on your server
cd /var/www
git clone https://github.com/dezgo/menuvi.git

# 2. Edit config
cp /var/www/menuvi/.env.example /var/www/menuvi/.env
nano /var/www/menuvi/.env
# Set: SECRET_KEY, ADMIN_PASSWORD, RESTAURANT_NAME, etc.

# 3. Run the setup script
sudo bash /var/www/menuvi/deploy/setup.sh

# 4. Set up HTTPS (optional but recommended)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d menuvi.appfoundry.cc
```

## What the setup script does

1. Installs Python 3, nginx
2. Creates a virtualenv at `/var/www/menuvi/.venv`
3. Installs pip dependencies
4. Creates `.env` from template with a random `SECRET_KEY`
5. Seeds the database
6. Installs and enables the systemd service (`menuvi.service`)
7. Installs and enables the nginx config

## Files

| File | Purpose |
|---|---|
| `menuvi.service` | systemd unit — runs gunicorn on port 8000 |
| `menuvi.nginx` | nginx reverse proxy — port 80/443 → 8000, serves static files |
| `setup.sh` | Automated setup script |

## Manual commands

```bash
# Check service status
sudo systemctl status menuvi

# View logs
sudo journalctl -u menuvi -f
tail -f /var/log/menuvi/error.log

# Restart after code changes
cd /var/www/menuvi && git pull
sudo systemctl restart menuvi

# Re-seed the database
cd /var/www/menuvi
sudo -u www-data FLASK_APP=menuvi .venv/bin/flask seed --drop
sudo systemctl restart menuvi
```

## Updating nginx domain

1. Edit `deploy/menuvi.nginx` — update `server_name` and SSL cert paths
2. Copy to server: `sudo cp deploy/menuvi.nginx /etc/nginx/sites-available/menuvi`
3. Test and reload: `sudo nginx -t && sudo systemctl reload nginx`
