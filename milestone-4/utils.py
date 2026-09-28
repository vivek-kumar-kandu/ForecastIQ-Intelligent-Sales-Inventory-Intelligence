"""
Core helpers - Python equivalent of includes/functions.php
"""
import secrets
from functools import wraps
from datetime import datetime, date
from flask import session, redirect, url_for, flash, request, abort

from db import dbFetchOne, dbFetchAll


# ---- Session / Auth ----
def is_logged_in() -> bool:
    return bool(session.get("user_id"))


def get_current_user() -> dict:
    return {
        "id": session.get("user_id", 0),
        "name": session.get("user_name", ""),
        "email": session.get("user_email", ""),
        "role": session.get("user_role", ""),
        "username": session.get("username", ""),
    }


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not is_logged_in():
                return redirect(url_for("auth.login"))
            if get_current_user()["role"] not in roles:
                flash("You are not authorized to view that page.", "error")
                return redirect(url_for("dashboard.index"))
            return view(*args, **kwargs)
        return wrapped
    return decorator


# ---- CSRF ----
def generate_csrf() -> str:
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]


def verify_csrf(token: str) -> bool:
    return bool(token) and token == session.get("csrf_token")


def csrf_protect(view):
    """Decorator: for POST requests, aborts with 400 if the csrf_token is invalid."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if request.method == "POST":
            if not verify_csrf(request.form.get("csrf_token", "")):
                flash("Invalid request. Please try again.", "error")
                return redirect(request.path)
        return view(*args, **kwargs)
    return wrapped


# ---- Formatting ----
def format_currency(amount) -> str:
    try:
        return "\u20b9" + f"{float(amount):,.2f}"
    except (TypeError, ValueError):
        return "\u20b90.00"


def format_number(amount) -> str:
    try:
        return f"{float(amount):,.0f}"
    except (TypeError, ValueError):
        return "0"


def format_date(value) -> str:
    if not value:
        return ""
    dt = _to_datetime(value)
    return dt.strftime("%d %b %Y") if dt else str(value)


def format_datetime(value) -> str:
    if not value:
        return ""
    dt = _to_datetime(value)
    return dt.strftime("%d %b %Y, %I:%M %p") if dt else str(value)


def _to_datetime(value):
    if isinstance(value, (datetime, date)):
        return value
    if not isinstance(value, str):
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


# ---- Notifications ----
def get_unread_notifications():
    user = get_current_user()
    return dbFetchAll(
        "SELECT * FROM notifications WHERE user_id = ? AND is_read = 0 ORDER BY created_at DESC LIMIT 10",
        (user["id"],),
    )


def get_notification_count() -> int:
    user = get_current_user()
    row = dbFetchOne(
        "SELECT COUNT(*) AS cnt FROM notifications WHERE user_id = ? AND is_read = 0",
        (user["id"],),
    )
    return int(row["cnt"]) if row else 0


def get_low_stock_count() -> int:
    row = dbFetchOne(
        "SELECT COUNT(*) AS cnt FROM products WHERE stock_quantity <= min_stock_level AND status='active'"
    )
    return int(row["cnt"]) if row else 0


# ---- Forecasting Algorithms ----
def moving_average(data, period=3):
    result = []
    n = len(data)
    for i in range(period - 1, n):
        window = data[i - period + 1: i + 1]
        result.append(round(sum(window) / period, 2))
    last = data[-period:]
    result.append(round(sum(last) / period, 2))
    return result


def exponential_smoothing(data, alpha=0.3):
    if not data:
        return []
    result = [data[0]]
    for i in range(1, len(data)):
        result.append(round(alpha * data[i] + (1 - alpha) * result[i - 1], 2))
    last = result[-1]
    result.append(round(alpha * last + (1 - alpha) * last, 2))
    return result


def linear_regression(y):
    n = len(y)
    x = list(range(1, n + 1))
    sx = sum(x)
    sy = sum(y)
    sxy = sum(x[i] * y[i] for i in range(n))
    sxx = sum(x[i] * x[i] for i in range(n))
    denom = (n * sxx - sx * sx) or 1
    slope = (n * sxy - sx * sy) / denom
    intercept = (sy - slope * sx) / n if n else 0
    predicted = [round(slope * xi + intercept, 2) for xi in x]
    predicted.append(round(slope * (n + 1) + intercept, 2))
    return {"slope": round(slope, 4), "intercept": round(intercept, 4), "predicted": predicted}


def forecast_confidence(actual, predicted):
    n = min(len(actual), len(predicted))
    if n == 0:
        return 0.0
    errors = []
    for i in range(n):
        if actual[i] != 0:
            errors.append(abs((actual[i] - predicted[i]) / actual[i]))
    if not errors:
        return 95.0
    mape = (sum(errors) / len(errors)) * 100
    return round(max(0, 100 - mape), 2)
