import os
from flask import Flask, redirect, url_for, session

import config
import db as db_module
from utils import (
    is_logged_in, get_current_user, get_unread_notifications,
    get_notification_count, get_low_stock_count, generate_csrf,
    format_currency, format_number, format_date, format_datetime,
)

from blueprints.auth import bp as auth_bp
from blueprints.dashboard import bp as dashboard_bp

# Modules that are "built" as of this milestone. The shared base.html
# template uses this set to decide which sidebar/topbar links to show,
# so students never see a link to a page that does not exist yet.
ENABLED_MODULES = {"auth", "dashboard"}


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    app.secret_key = config.SECRET_KEY
    app.config["PERMANENT_SESSION_LIFETIME"] = config.SESSION_LIFETIME

    db_module.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

    @app.route("/")
    def index():
        if is_logged_in():
            return redirect(url_for("dashboard.index"))
        return redirect(url_for("auth.login"))

    @app.context_processor
    def inject_globals():
        if is_logged_in():
            notifications = get_unread_notifications() if "notifications" in ENABLED_MODULES else []
            notif_count = get_notification_count() if "notifications" in ENABLED_MODULES else 0
            low_stock_count = get_low_stock_count() if "inventory" in ENABLED_MODULES else 0
            user = get_current_user()
        else:
            notifications, notif_count, low_stock_count, user = [], 0, 0, {}
        return dict(
            current_user=user,
            notifications=notifications,
            notif_count=notif_count,
            low_stock_count=low_stock_count,
            csrf_token=generate_csrf,
            app_name=config.APP_NAME,
            app_version=config.APP_VERSION,
            fmt_currency=format_currency,
            fmt_number=format_number,
            fmt_date=format_date,
            fmt_datetime=format_datetime,
            enabled=ENABLED_MODULES,
        )

    return app


app = create_app()

if __name__ == "__main__":
    if not os.path.exists(config.DATABASE_PATH):
        print("Database not found - run `python init_db.py` first.")
    app.run(debug=True, host="0.0.0.0", port=5000)
