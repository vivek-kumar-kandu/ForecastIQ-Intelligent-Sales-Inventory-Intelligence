from flask import Blueprint, render_template, request, redirect, url_for, flash

from db import dbFetchAll, dbFetchOne, dbInsert, dbUpdate, dbQuery
from utils import login_required, verify_csrf

bp = Blueprint("customers", __name__)


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST" and verify_csrf(request.form.get("csrf_token", "")):
        action = request.form.get("action", "")
        data = {
            "name": request.form.get("name", "").strip(),
            "email": request.form.get("email", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "address": request.form.get("address", "").strip(),
            "city": request.form.get("city", "").strip(),
            "country": request.form.get("country", "India").strip(),
        }
        if action == "add":
            last = dbFetchOne("SELECT customer_code FROM customers ORDER BY id DESC LIMIT 1")
            num = (int(last["customer_code"][4:]) + 1) if last else 1
            data["customer_code"] = f"CUST{num:03d}"
            dbInsert("customers", data)
            flash("Customer added.", "success")
        elif action == "edit":
            dbUpdate("customers", data, "id=?", (int(request.form.get("customer_id")),))
            flash("Customer updated.", "success")
        elif action == "delete":
            dbQuery("UPDATE customers SET status='inactive' WHERE id=?", (int(request.form.get("customer_id")),))
            flash("Customer removed.", "success")
        return redirect(url_for("customers.index"))

    search = request.args.get("search", "").strip()
    if search:
        customers = dbFetchAll(
            "SELECT * FROM customers WHERE status='active' AND (name LIKE ? OR email LIKE ?) ORDER BY name",
            (f"%{search}%", f"%{search}%"),
        )
    else:
        customers = dbFetchAll("SELECT * FROM customers WHERE status='active' ORDER BY name")

    return render_template(
        "customers/index.html",
        page_title="Customers", active_menu="customers",
        customers=customers, search=search,
    )
