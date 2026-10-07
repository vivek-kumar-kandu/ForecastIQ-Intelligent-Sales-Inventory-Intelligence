from flask import Blueprint, render_template, request, redirect, url_for, flash

from db import dbFetchAll, dbFetchOne, dbInsert, dbUpdate, dbQuery
from utils import login_required, verify_csrf

bp = Blueprint("suppliers", __name__)


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
            "status": "active",
        }
        if action == "add":
            last = dbFetchOne("SELECT supplier_code FROM suppliers ORDER BY id DESC LIMIT 1")
            num = (int(last["supplier_code"][3:]) + 1) if last else 1
            data["supplier_code"] = f"SUP{num:03d}"
            dbInsert("suppliers", data)
            flash("Supplier added.", "success")
        elif action == "edit":
            dbUpdate("suppliers", data, "id=?", (int(request.form.get("supplier_id")),))
            flash("Supplier updated.", "success")
        elif action == "delete":
            dbQuery("UPDATE suppliers SET status='inactive' WHERE id=?", (int(request.form.get("supplier_id")),))
            flash("Supplier removed.", "success")
        return redirect(url_for("suppliers.index"))

    search = request.args.get("search", "").strip()
    if search:
        suppliers = dbFetchAll(
            "SELECT * FROM suppliers WHERE status='active' AND (name LIKE ? OR email LIKE ?) ORDER BY name",
            (f"%{search}%", f"%{search}%"),
        )
    else:
        suppliers = dbFetchAll("SELECT * FROM suppliers WHERE status='active' ORDER BY name")

    for s in suppliers:
        cnt = dbFetchOne("SELECT COUNT(*) AS v FROM products WHERE supplier_id=? AND status='active'", (s["id"],))
        s["product_count"] = cnt["v"] if cnt else 0

    return render_template(
        "suppliers/index.html",
        page_title="Suppliers", active_menu="suppliers",
        suppliers=suppliers, search=search,
    )
