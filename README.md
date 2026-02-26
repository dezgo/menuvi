# MenuVi

A multi-restaurant digital menu platform. Customers scan a QR code, browse the menu on their phone, pick items they want, and show their selections to the waiter.

**Not an ordering system** — it's a beautiful, readable menu that works better than a paper menu in dim restaurant lighting.

## Features

- **Multi-restaurant support** — one deployment serves multiple restaurants, each with their own menu, branding, and admin users
- **Restaurant directory** — root page lists all restaurants
- **Per-restaurant URLs** — `/<slug>/menu/dining`, `/<slug>/admin/`, etc.
- **Category browsing** — tap through categories to see items
- **Item details** — name, description, price
- **My Picks** — shortlist items, then show the list to your waiter (big-font "Show Waiter" mode)
- **Search** — find items by name within a restaurant
- **Admin panel** — per-restaurant CRUD for categories and items, toggle availability, QR code generator
- **Superadmin panel** — manage restaurants, users, and branding at `/superadmin/`
- **User accounts** — email/password auth with owner and superadmin roles
- **Per-restaurant branding** — name, tagline, and accent colors stored in the database
- **SEO** — meta descriptions, Open Graph tags, sitemap.xml, robots.txt

## Quick Start

```bash
cd menuvi

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set your SECRET_KEY

# Seed the database with sample menu data (Jewel of India)
flask seed

# Create a superadmin user
flask create-superadmin

# Run the dev server
flask run
```

Open http://localhost:5000 to see the restaurant directory.
Open http://localhost:5000/jewel-of-india/ to see the sample restaurant menu.
Open http://localhost:5000/superadmin/ to manage restaurants and users.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `dev-secret-key-change-me` | Flask session signing key (change in production!) |
| `DATABASE_URL` | `sqlite:///instance/menuvi.db` | Database connection string |
| `MAX_UPLOAD_MB` | `10` | Max upload size in MB |

## Admin Panel

Each restaurant has its own admin panel at `/<slug>/admin/`:

1. Log in with your email and password
2. Create/edit/delete categories and items
3. Toggle item availability (e.g., "86'd" items)
4. Set menu type per category: `dining` or `beverages`
5. Control sort order for categories and items
6. Generate and download QR codes for tables

## Superadmin Panel

Manage the entire platform at `/superadmin/`:

1. Create and edit restaurants (name, slug, tagline, brand colors)
2. Create and manage user accounts (owner or superadmin roles)
3. Jump into any restaurant's admin panel

## QR Code Setup

Each restaurant's admin panel has a QR code generator. The QR code points to `/<slug>/` so customers land directly on that restaurant's menu.

## Running Tests

```bash
python -m pytest tests/ -v
```

## Deployment (Gunicorn + Nginx)

```bash
# First-time setup
bash deploy/setup.sh

# Create superadmin
FLASK_APP=menuvi .venv/bin/flask create-superadmin

# Ongoing deploys
bash deploy/update.sh
```

## Project Structure

```
menuvi/
├── menuvi/
│   ├── __init__.py          # App factory, Flask-Login, error handlers
│   ├── config.py            # Configuration from env vars
│   ├── models.py            # Restaurant, User, Category, MenuItem
│   ├── cli.py               # CLI commands (seed, create-superadmin)
│   ├── seed_data.py         # Sample menu data (Jewel of India)
│   ├── blueprints/
│   │   ├── public.py        # Customer routes (directory, menu, picks, SEO)
│   │   ├── admin.py         # Per-restaurant admin CRUD
│   │   └── superadmin.py    # Platform admin (restaurants, users)
│   ├── templates/
│   │   ├── base.html        # Base layout with SEO and branding
│   │   ├── public/          # Customer templates
│   │   ├── admin/           # Restaurant admin templates
│   │   ├── superadmin/      # Platform admin templates
│   │   └── errors/          # 404, 403, 500 pages
│   └── static/
│       ├── css/style.css    # Mobile-first dark theme
│       └── js/app.js        # Progressive enhancement for picks
├── tests/                   # pytest test suite (23 tests)
├── deploy/                  # systemd, nginx, setup/update scripts
├── instance/                # SQLite DB (gitignored)
├── requirements.txt
├── .env.example
└── README.md
```
