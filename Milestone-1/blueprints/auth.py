import time
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash

from db import dbFetchOne, dbUpdate, dbInsert
from utils import is_logged_in, verify_csrf, generate_csrf

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if is_logged_in():
        return redirect(url_for("dashboard.index"))

    error = None

    if request.method == "POST":
        if not verify_csrf(request.form.get("csrf_token", "")):
            error = "Invalid request. Please try again."
        else:
            login_id = request.form.get("login_id", "").strip()
            password = request.form.get("password", "")

            if not login_id or not password:
                error = "Please fill in all fields."
            else:
                user = dbFetchOne(
                    "SELECT * FROM users WHERE (email = ? OR username = ?) AND status = 'active'",
                    (login_id, login_id),
                )
                if user and check_password_hash(user["password_hash"], password):
                    session.clear()
                    session["user_id"] = user["id"]
                    session["user_name"] = user["full_name"]
                    session["user_email"] = user["email"]
                    session["user_role"] = user["role"]
                    session["username"] = user["username"]
                    dbUpdate("users", {"last_login": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                              "id = ?", (user["id"],))
                    return redirect(url_for("dashboard.index"))
                else:
                    error = "Invalid credentials. Please try again."
                    time.sleep(1)  # brute-force mitigation

    return render_template("auth/login.html", error=error)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if is_logged_in():
        return redirect(url_for("dashboard.index"))

    error = None
    success = None
    form = {}

    if request.method == "POST":
        form = request.form
        if not verify_csrf(request.form.get("csrf_token", "")):
            error = "Invalid request."
        else:
            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip()
            username = request.form.get("username", "").strip()
            phone = request.form.get("phone", "").strip()
            role = request.form.get("role", "staff")
            password = request.form.get("password", "")
            confirm = request.form.get("confirm_password", "")

            if not all([full_name, email, username, password, confirm]):
                error = "All required fields must be filled."
            elif "@" not in email or "." not in email.split("@")[-1]:
                error = "Invalid email address."
            elif len(password) < 6:
                error = "Password must be at least 6 characters."
            elif password != confirm:
                error = "Passwords do not match."
            elif role not in ("admin", "manager", "staff"):
                error = "Invalid role selected."
            else:
                exists = dbFetchOne(
                    "SELECT id FROM users WHERE email = ? OR username = ?", (email, username)
                )
                if exists:
                    error = "Email or username already exists."
                else:
                    dbInsert("users", {
                        "full_name": full_name, "email": email, "username": username,
                        "phone": phone, "password_hash": generate_password_hash(password),
                        "role": role,
                    })
                    success = "Account created! You can now log in."

    return render_template("auth/register.html", error=error, success=success, form=form)


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
