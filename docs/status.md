# MenuVi - Digital Restaurant Menu

## Status: Live - Deployed

**URL:** https://menuvi.appfoundry.cc

## Architecture

MenuVi is a mobile-first digital menu for restaurants. Customers scan a QR code on the table, choose between Dining and Beverages, browse the menu, and shortlist items they want to order. When ready, they show their picks to the waiter. No accounts, no ordering, no payments — just a beautiful readable menu that works better than paper in dim restaurant lighting.

### Key Flows
```
Customer scans QR -> / (landing) -> choose Dining or Beverages -> browse categories -> tap items -> "My Picks" -> show waiter
Admin logs in -> /admin -> manage categories, items, availability -> download QR code
```

### Key Design Decision
This is NOT online ordering. The app assists the customer-waiter interaction, not replaces it. Customers browse at their own pace, build a shortlist, and show the waiter when ready. Dark theme matches restaurant ambience. Branding is fully configurable via env vars so any restaurant can use it.

### Key Components
- **menuvi/__init__.py** - App factory, blueprint registration, branding context processor
- **menuvi/config.py** - Config from env vars (branding, admin password, DB, upload limits)
- **menuvi/models.py** - Category (with menu_type: dining/beverages), MenuItem (name, description, price_cents, available, sort_order)
- **menuvi/cli.py** - `flask seed` command to populate from seed data
- **menuvi/seed_data.py** - Jewel of India menu extracted from original HTML/PDF

### Route Blueprints
- **public** - Customer-facing: landing page, menu by type (dining/beverages), category listing, item detail, search, shortlist (add/remove/clear), "My Picks" page with "Show Waiter" mode
- **admin** - Password-protected: login/logout, dashboard with category table, category CRUD, item CRUD, toggle availability, QR code generator with PNG download

### Data Model
```
Category (id, name, menu_type [dining|beverages], sort_order)
  └── MenuItem (id, category_id, name, description, price_cents nullable, available, sort_order)
```

- `menu_type` splits categories between the two menu screens
- `price_cents` stored as integer (2290 = $22.90), nullable for unpriced items
- `available` toggle lets admin 86 items without deleting them
- `sort_order` controls display order in both admin and customer views

### Session / Shortlist
- Shortlist stored in Flask signed cookie session (no user accounts)
- Session contains list of MenuItem IDs
- "Show Waiter" mode: big-font view, hides remove buttons, clean display for staff
- Progressive enhancement: pick buttons use fetch() for snappy UX, fall back to form POST

## Tech Stack
- Flask 3.1, Flask-SQLAlchemy
- SQLite (instance/menuvi.db)
- Jinja2 templates, vanilla CSS (no frameworks), vanilla JS
- qrcode[pil] for server-side QR generation
- Gunicorn behind nginx with Cloudflare proxy
- 22 pytest tests (models, public routes, picks, admin)

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
- **Config:** `.env` file with `SECRET_KEY`, `ADMIN_PASSWORD`, `RESTAURANT_NAME`, `RESTAURANT_TAGLINE`, `BRAND_COLOR`, `BRAND_COLOR_DIM`
- **Update:** `bash deploy/update.sh` (git pull, pip install, restart gunicorn)
- **Seed data:** `flask seed` (Jewel of India menu), `flask seed --drop` to reset

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

### Potential Ideas
- Multiple restaurant support — single instance serving different menus by subdomain or slug
- Item images — photo upload per menu item
- Daily specials — time-limited items that auto-hide
- Allergen/dietary tags — vegan, gluten-free, nut-free, spice level indicators
- Multi-language support — toggle between English and other languages

## Done
- [x] Core MVP: landing page, dining/beverages split, category browsing, item detail
- [x] My Picks shortlist with session storage, add/remove/clear
- [x] "Show Waiter" big-font mode on picks page
- [x] Search by item name
- [x] Admin panel with password auth, full CRUD for categories and items
- [x] Toggle item availability
- [x] QR code generator in admin panel (view + download PNG)
- [x] Configurable branding via env vars (restaurant name, tagline, colors)
- [x] Dark theme with mobile-first responsive CSS
- [x] Seed data from Jewel of India menu (64 items, 10 categories)
- [x] Deploy to DigitalOcean with systemd + nginx + Cloudflare SSL
- [x] deploy/update.sh for one-command deploys
- [x] 22 pytest tests (models, public routes, picks, admin)
