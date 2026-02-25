"""Flask CLI commands."""

import click
from flask import Flask


def register_cli(app: Flask):
    @app.cli.command("seed")
    @click.option("--drop", is_flag=True, help="Drop existing data before seeding.")
    def seed_db(drop):
        """Populate the database with the Jewel of India menu."""
        from .models import db, Category, MenuItem
        from .seed_data import MENU

        if drop:
            click.echo("Dropping existing menu data...")
            MenuItem.query.delete()
            Category.query.delete()
            db.session.commit()

        cat_order = 0
        for cat_name, items in MENU.items():
            cat = Category.query.filter_by(name=cat_name).first()
            if not cat:
                cat = Category(name=cat_name, sort_order=cat_order)
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
        click.echo(f"Seeded {total} menu items across {Category.query.count()} categories.")
