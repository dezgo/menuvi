# MenuVi

A mobile-friendly digital menu web app for restaurants. Customers scan a QR code, browse the menu on their phone, pick items they want, and show their selections to the waiter.

**Not an ordering system** — it's a beautiful, readable menu that works better than a paper menu in dim restaurant lighting.

## Features

- **Landing page** — choose Dining or Beverages menu
- **Category browsing** — tap through categories to see items
- **Item details** — name, description, price
- **My Picks** — shortlist items, then show the list to your waiter (big-font "Show Waiter" mode)
- **Search** — find items by name
- **Admin panel** — full CRUD for categories and items, toggle availability, password-protected
- **Configurable branding** — restaurant name, tagline, and accent color via environment variables

## Quick Start

```bash
# Clone and enter the project
cd menuvi

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set your ADMIN_PASSWORD and SECRET_KEY

# Seed the database with sample menu data
flask seed

# Run the dev server
flask run
```

Open http://localhost:5000 to see the customer menu.
Open http://localhost:5000/admin to manage the menu.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `dev-secret-key-change-me` | Flask session signing key (change in production!) |
| `ADMIN_PASSWORD` | `admin` | Password for the /admin panel |
| `DATABASE_URL` | `sqlite:///instance/menuvi.db` | Database connection string |
| `RESTAURANT_NAME` | `Jewel of India` | Displayed on landing page and headers |
| `RESTAURANT_TAGLINE` | `Fine Indian Cuisine` | Subtitle on landing page |
| `BRAND_COLOR` | `#c9a84c` | Primary accent color (gold) |
| `BRAND_COLOR_DIM` | `#a68939` | Hover/secondary accent color |

## Admin Panel

1. Navigate to `/admin`
2. Log in with `ADMIN_PASSWORD`
3. Create/edit/delete categories and items
4. Toggle item availability (e.g., "86'd" items)
5. Set menu type per category: `dining` or `beverages`
6. Control sort order for categories and items

## QR Code Setup

Generate a QR code pointing to your deployed URL (e.g., `https://menu.yourrestaurant.com`). Place it on tables. Customers scan and land on the menu chooser.

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

## Deployment (Gunicorn + Nginx)

```bash
# Install gunicorn (already in requirements.txt)
pip install gunicorn

# Run with gunicorn
gunicorn "menuvi:create_app()" -b 0.0.0.0:8000 -w 2

# Seed on the server
FLASK_APP=menuvi flask seed
```

Nginx config (minimal):

```nginx
server {
    listen 80;
    server_name menu.yourrestaurant.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/menuvi/menuvi/static/;
        expires 7d;
    }
}
```

## Project Structure

```
menuvi/
├── menuvi/
│   ├── __init__.py          # App factory (create_app)
│   ├── config.py            # Configuration from env vars
│   ├── models.py            # SQLAlchemy models (Category, MenuItem)
│   ├── cli.py               # Flask CLI commands (seed)
│   ├── seed_data.py         # Seed data from Jewel of India menu
│   ├── blueprints/
│   │   ├── public.py        # Customer-facing routes
│   │   └── admin.py         # Admin CRUD routes
│   ├── templates/
│   │   ├── base.html        # Base layout with branding
│   │   ├── public/          # Customer templates
│   │   └── admin/           # Admin templates
│   └── static/
│       ├── css/style.css    # Mobile-first dark theme
│       └── js/app.js        # Progressive enhancement for picks
├── tests/                   # pytest test suite
├── instance/                # SQLite DB (gitignored)
├── requirements.txt
├── .env.example
└── README.md
```
