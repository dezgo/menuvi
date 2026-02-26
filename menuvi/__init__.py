from flask import Flask, g
from flask_login import LoginManager

from .config import Config
from .models import db, User

login_manager = LoginManager()


def create_app(config_class=Config):
    app = Flask(
        __name__,
        instance_relative_config=True,
        instance_path=str(Config.INSTANCE_DIR),
    )
    app.config.from_object(config_class)

    # Ensure instance directories exist
    from pathlib import Path

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)

    # Flask-Login setup
    login_manager.init_app(app)
    login_manager.login_view = None  # handled per-blueprint

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import request, redirect, url_for
        # Try to extract slug from the URL to redirect to the right login page
        path_parts = request.path.strip("/").split("/")
        if len(path_parts) >= 2 and path_parts[1] == "admin":
            slug = path_parts[0]
            return redirect(url_for("admin.login", slug=slug, next=request.url))
        return redirect(url_for("superadmin.login", next=request.url))

    # Create tables on first request
    with app.app_context():
        db.create_all()

    # Register blueprints
    from .blueprints.public import public_bp
    from .blueprints.admin import admin_bp
    from .blueprints.superadmin import superadmin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(superadmin_bp, url_prefix="/superadmin")

    # Register CLI commands
    from .cli import register_cli

    register_cli(app)

    # Inject restaurant branding into all templates
    @app.context_processor
    def inject_branding():
        restaurant = getattr(g, "restaurant", None)
        if restaurant:
            return {
                "restaurant_name": restaurant.name,
                "restaurant_tagline": restaurant.tagline,
                "brand_color": restaurant.brand_color,
                "brand_color_dim": restaurant.brand_color_dim,
                "restaurant_slug": restaurant.slug,
            }
        return {
            "restaurant_name": "MenuVi",
            "restaurant_tagline": "Digital Menus",
            "brand_color": "#c9a84c",
            "brand_color_dim": "#a68939",
            "restaurant_slug": "",
        }

    return app
