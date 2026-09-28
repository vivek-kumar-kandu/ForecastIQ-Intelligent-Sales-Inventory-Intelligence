import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# ---- App ----
APP_NAME = "ForecastinQ"
APP_VERSION = "1.0.0"
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
SESSION_LIFETIME = 3600  # seconds

# ---- Database (SQLite) ----
DATABASE_PATH = os.path.join(BASE_DIR, "database", "forecastinq.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")

# ---- Uploads ----
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "images", "uploads")
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

# ---- Misc ----
TIMEZONE = "Asia/Kolkata"
