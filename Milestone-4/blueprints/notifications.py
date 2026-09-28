from flask import Blueprint, render_template, request, redirect, url_for

from db import dbFetchAll, dbQuery
from utils import login_required, get_current_user

bp = Blueprint("notifications", __name__)


@bp.route("/")
@login_required
def index():
    user = get_current_user()

    if request.args.get("mark_all"):
        dbQuery("UPDATE notifications SET is_read=1 WHERE user_id=?", (user["id"],))
        return redirect(url_for("notifications.index"))

    notifications = dbFetchAll(
        "SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC", (user["id"],)
    )
    icon_map = {"low_stock": "⚠️", "out_of_stock": "🚨", "forecast": "📊", "sales_target": "🎯", "system": "🔔"}
    for n in notifications:
        n["icon"] = icon_map.get(n["type"], "🔔")

    return render_template(
        "notifications/index.html",
        page_title="Notifications", active_menu="notifications",
        notifications_list=notifications,
    )
