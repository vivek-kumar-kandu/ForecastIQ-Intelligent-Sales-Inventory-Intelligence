from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash

from db import dbFetchAll, dbInsert, dbUpdate, dbQuery
from utils import login_required, role_required, verify_csrf, get_current_user

bp = Blueprint("users", __name__)


@bp.route("/", methods=["GET", "POST"])
@login_required
@role_required("admin")
def index():
    if request.method == "POST" and verify_csrf(request.form.get("csrf_token", "")):
        action = request.form.get("action", "")

        if action in ("add", "edit"):
            data = {
                "full_name": request.form.get("full_name", "").strip(),
                "email": request.form.get("email", "").strip(),
                "username": request.form.get("username", "").strip(),
                "phone": request.form.get("phone", "").strip(),
                "role": request.form.get("role", "staff"),
                "status": request.form.get("status", "active"),
            }
            if action == "add":
                pw = request.form.get("password") or "Admin@123"
                data["password_hash"] = generate_password_hash(pw)
                dbInsert("users", data)
                flash("User created.", "success")
            else:
                uid = int(request.form.get("user_id"))
                if request.form.get("password"):
                    data["password_hash"] = generate_password_hash(request.form.get("password"))
                dbUpdate("users", data, "id=?", (uid,))
                flash("User updated.", "success")

        elif action == "delete":
            uid = int(request.form.get("user_id"))
            if uid != get_current_user()["id"]:
                dbQuery("UPDATE users SET status='inactive' WHERE id=?", (uid,))
                flash("User deactivated.", "success")
            else:
                flash("Cannot deactivate yourself.", "error")

        return redirect(url_for("users.index"))

    users = dbFetchAll("SELECT * FROM users ORDER BY created_at DESC")
    for u in users:
        u["role_cls"] = "bg-danger" if u["role"] == "admin" else ("bg-warning text-dark" if u["role"] == "manager" else "bg-secondary")

    return render_template(
        "users/index.html",
        page_title="User Management", active_menu="users",
        users=users,
    )
