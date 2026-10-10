import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# ---- App ----
APP_NAME = "ForecastinQ"
APP_VERSION = "1.0.0"
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
SESSION_LIFETIME = int(os.environ.get("SESSION_LIFETIME", 3600))  # seconds

# ---- Session & Security Cookies ----
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() in ("true", "1", "yes")

# ---- Database (SQLite) ----
DATABASE_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "database", "forecastinq.db"))
SCHEMA_PATH = os.environ.get("SCHEMA_PATH", os.path.join(BASE_DIR, "database", "schema.sql"))

# Ensure database directory exists
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

# ---- Uploads ----
UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", os.path.join(BASE_DIR, "static", "images", "uploads"))
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---- Misc ----
TIMEZONE = os.environ.get("TIMEZONE", "Asia/Kolkata")
