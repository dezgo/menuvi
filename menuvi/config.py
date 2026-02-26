import os
from pathlib import Path


class Config:
    BASE_DIR = Path(__file__).resolve().parent.parent
    INSTANCE_DIR = BASE_DIR / "instance"

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{INSTANCE_DIR / 'menuvi.db'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = str(INSTANCE_DIR / "uploads")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_UPLOAD_MB", 10)) * 1024 * 1024
