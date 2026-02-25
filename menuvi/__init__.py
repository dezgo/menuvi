from flask import Flask
from .config import Config
from .models import db


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

    # Create tables on first request
    with app.app_context():
        db.create_all()

    # Register blueprints
    from .blueprints.public import public_bp
    from .blueprints.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Register CLI commands
    from .cli import register_cli

    register_cli(app)

    # Inject branding into all templates
    @app.context_processor
    def inject_branding():
        return {
            "restaurant_name": app.config["RESTAURANT_NAME"],
            "restaurant_tagline": app.config["RESTAURANT_TAGLINE"],
            "brand_color": app.config["BRAND_COLOR"],
            "brand_color_dim": app.config["BRAND_COLOR_DIM"],
        }

    return app
