import os
from pathlib import Path


class Config:
    BASE_DIR = Path(__file__).resolve().parent.parent
    INSTANCE_DIR = BASE_DIR / "instance"

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{INSTANCE_DIR / 'menuvi.db'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = str(INSTANCE_DIR / "uploads")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_UPLOAD_MB", 10)) * 1024 * 1024

    # ── branding (override per-restaurant via env vars) ──────────────────
    RESTAURANT_NAME = os.environ.get("RESTAURANT_NAME", "Jewel of India")
    RESTAURANT_TAGLINE = os.environ.get("RESTAURANT_TAGLINE", "Fine Indian Cuisine")
    BRAND_COLOR = os.environ.get("BRAND_COLOR", "#c9a84c")        # gold
    BRAND_COLOR_DIM = os.environ.get("BRAND_COLOR_DIM", "#a68939")
