# MenuVi - Multi-Restaurant Digital Menu Platform

## Status: Live - Deployed

**URL:** https://menuvi.appfoundry.cc

## Architecture

MenuVi is a multi-restaurant digital menu platform. Each restaurant gets its own branded menu at `/<slug>/`. Customers scan a QR code on the table, choose between Dining and Beverages, browse the menu, and shortlist items they want to order. When ready, they show their picks to the waiter. No customer accounts, no ordering, no payments — just a beautiful readable menu that works better than paper in dim restaurant lighting.

### Key Flows
```
Customer scans QR -> /<slug>/ (landing) -> choose Dining or Beverages -> browse categories -> tap items -> "My Picks" -> show waiter
Restaurant admin -> /<slug>/admin/login -> manage categories, items, availability -> download QR code
Superadmin -> /superadmin/ -> manage restaurants, users, branding
```

### Key Design Decision
This is NOT online ordering. The app assists the customer-waiter interaction, not replaces it. Customers browse at their own pace, build a shortlist, and show the waiter when ready. Dark theme matches restaurant ambience. Each restaurant has its own branding (name, tagline, colors) stored in the database.

### Key Components
- **menuvi/__init__.py** - App factory, Flask-Login setup, error handlers, branding context processor
- **menuvi/config.py** - Config from env vars (SECRET_KEY, DATABASE_URL)
- **menuvi/models.py** - Restaurant, User, Category, MenuItem
- **menuvi/cli.py** - `flask seed` and `flask create-superadmin` commands
- **menuvi/seed_data.py** - Jewel of India menu extracted from original HTML/PDF

### Route Blueprints
- **public** - Customer-facing: restaurant directory (/), per-restaurant landing (/<slug>/), menu by type, category listing, item detail, search, shortlist, robots.txt, sitemap.xml
- **admin** - Per-restaurant admin at /<slug>/admin/: email+password login, dashboard, category CRUD, item CRUD, toggle availability, QR code generator
- **superadmin** - Platform admin at /superadmin/: restaurant CRUD, user CRUD (owner/superadmin roles)

### Data Model
```
Restaurant (id, name, slug, tagline, brand_color, brand_color_dim)
  ├── User (id, email, password_hash, role [owner|superadmin], restaurant_id nullable)
  └── Category (id, restaurant_id, name, menu_type [dining|beverages], sort_order)
        └── MenuItem (id, category_id, name, description, price_cents nullable, available, sort_order)
```

- `slug` is used in all URLs for tenant routing
- `role` is either "owner" (scoped to one restaurant) or "superadmin" (platform-wide)
- `menu_type` splits categories between the two menu screens
- `price_cents` stored as integer (2290 = $22.90), nullable for unpriced items
- `available` toggle lets admin 86 items without deleting them
- `sort_order` controls display order in both admin and customer views

### Session / Shortlist
- Shortlist stored in Flask signed cookie session (no customer accounts)
- Session contains list of MenuItem IDs
- "Show Waiter" mode: big-font view, hides remove buttons, clean display for staff
- Progressive enhancement: pick buttons use fetch() for snappy UX, fall back to form POST

### SEO
- Per-page meta descriptions and Open Graph tags
- Canonical URLs, theme-color meta tag
- Auto-generated /sitemap.xml with all restaurants and categories
- /robots.txt with sitemap reference

## Tech Stack
- Flask 3.1, Flask-SQLAlchemy, Flask-Login
- SQLite (instance/menuvi.db)
- Jinja2 templates, vanilla CSS (no frameworks), vanilla JS
- qrcode[pil] for server-side QR generation
- Gunicorn behind nginx with Cloudflare proxy
- 23 pytest tests (models, public routes, picks, admin)

## Dependencies
- No external APIs
- No external database — SQLite only
- No JS frameworks — vanilla JS for progressive enhancement only

## Deployment
- **Domain:** menuvi.appfoundry.cc (Cloudflare proxied, Full Strict SSL)
- **Repo:** git@github-personal:dezgo/menuvi.git
- **Server:** DigitalOcean personal droplet (209.38.91.37)
- **Path:** /var/www/menuvi
- **Stack:** Gunicorn (port 8010) → nginx → Cloudflare
- **Config:** `.env` file with `SECRET_KEY` (branding now stored in DB per restaurant)
- **Update:** `bash deploy/update.sh` (git pull, pip install, restart gunicorn)
- **Seed data:** `flask seed` (Jewel of India restaurant + menu), `flask seed --drop` to reset
- **Create admin:** `flask create-superadmin` (prompts for email + password)

### Deploy Files
- `deploy/menuvi.service` — systemd unit (gunicorn on 127.0.0.1:8010, www-data user)
- `deploy/menuvi.nginx` — nginx reverse proxy + static files + SSL (certbot-managed)
- `deploy/setup.sh` — first-time server provisioning
- `deploy/update.sh` — ongoing deploys (pull, install, restart)

## TODO
- [ ] Beverages menu content — seed data only has food, beverages need to be added via admin
- [ ] "Ready to order" button — customers can signal they're ready, staff get notified
- [ ] PWA support — service worker + manifest for "Add to Home Screen"
- [ ] Table numbers — QR per table so staff know which table the picks come from
- [ ] Item images — photo upload per menu item
- [ ] Daily specials — time-limited items that auto-hide
- [ ] Allergen/dietary tags — vegan, gluten-free, nut-free, spice level indicators
- [ ] Multi-language support — toggle between English and other languages

## Done
- [x] Core MVP: landing page, dining/beverages split, category browsing, item detail
- [x] My Picks shortlist with session storage, add/remove/clear
- [x] "Show Waiter" big-font mode on picks page
- [x] Search by item name
- [x] Admin panel with full CRUD for categories and items
- [x] Toggle item availability
- [x] QR code generator in admin panel (view + download PNG)
- [x] Dark theme with mobile-first responsive CSS
- [x] Seed data from Jewel of India menu (64 items, 10 categories)
- [x] Deploy to DigitalOcean with systemd + nginx + Cloudflare SSL
- [x] deploy/update.sh for one-command deploys
- [x] Multi-restaurant support with URL slug routing
- [x] User accounts with Flask-Login (owner + superadmin roles)
- [x] Superadmin panel for managing restaurants and users
- [x] Restaurant directory page at root
- [x] Per-restaurant branding stored in database
- [x] SEO: meta descriptions, Open Graph tags, sitemap.xml, robots.txt
- [x] Custom error pages (404, 403, 500)
- [x] 23 pytest tests (models, public routes, picks, admin)
