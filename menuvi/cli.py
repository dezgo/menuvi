"""Flask CLI commands."""

import click
from flask import Flask


def register_cli(app: Flask):
    @app.cli.command("seed")
    @click.option("--drop", is_flag=True, help="Drop existing data before seeding.")
    def seed_db(drop):
        """Populate the database with the Jewel of India menu."""
        from .models import db, Restaurant, Category, MenuItem
        from .seed_data import MENU

        if drop:
            click.echo("Dropping existing menu data...")
            MenuItem.query.delete()
            Category.query.delete()
            Restaurant.query.delete()
            db.session.commit()

        # Create or get the restaurant
        restaurant = Restaurant.query.filter_by(slug="jewel-of-india").first()
        if not restaurant:
            restaurant = Restaurant(
                name="Jewel of India",
                slug="jewel-of-india",
                tagline="Fine Indian Cuisine",
                brand_color="#c9a84c",
                brand_color_dim="#a68939",
            )
            db.session.add(restaurant)
            db.session.flush()

        cat_order = 0
        for cat_name, items in MENU.items():
            cat = Category.query.filter_by(
                restaurant_id=restaurant.id, name=cat_name,
            ).first()
            if not cat:
                cat = Category(
                    restaurant_id=restaurant.id,
                    name=cat_name,
                    sort_order=cat_order,
                )
                db.session.add(cat)
                db.session.flush()

            item_order = 0
            for name, desc, price_cents in items:
                exists = MenuItem.query.filter_by(
                    category_id=cat.id, name=name
                ).first()
                if not exists:
                    db.session.add(MenuItem(
                        category_id=cat.id,
                        name=name,
                        description=desc,
                        price_cents=price_cents,
                        sort_order=item_order,
                    ))
                item_order += 1
            cat_order += 1

        db.session.commit()
        total = MenuItem.query.count()
        click.echo(
            f"Seeded {total} menu items across "
            f"{Category.query.filter_by(restaurant_id=restaurant.id).count()} categories "
            f"for '{restaurant.name}'."
        )

    @app.cli.command("create-superadmin")
    @click.option("--email", prompt=True, help="Superadmin email address.")
    @click.option("--password", prompt=True, hide_input=True,
                  confirmation_prompt=True, help="Superadmin password.")
    def create_superadmin(email, password):
        """Create a superadmin user."""
        from .models import db, User

        existing = User.query.filter_by(email=email).first()
        if existing:
            click.echo(f"User '{email}' already exists.")
            return

        user = User(email=email, role="superadmin")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f"Superadmin '{email}' created.")
