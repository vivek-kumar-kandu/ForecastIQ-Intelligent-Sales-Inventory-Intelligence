from flask import Blueprint, render_template, request, redirect, url_for, flash

from db import dbFetchAll, dbFetchOne, dbInsert, dbUpdate, dbQuery
from utils import login_required, verify_csrf, get_current_user

bp = Blueprint("products", __name__)


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        if not verify_csrf(request.form.get("csrf_token", "")):
            flash("Invalid request.", "error")
            return redirect(url_for("products.index"))

        action = request.form.get("action", "")

        if action in ("add", "edit"):
            data = {
                "name": request.form.get("name", "").strip(),
                "category_id": int(request.form.get("category_id") or 0) or None,
                "brand": request.form.get("brand", "").strip(),
                "supplier_id": int(request.form.get("supplier_id") or 0) or None,
                "cost_price": float(request.form.get("cost_price") or 0),
                "selling_price": float(request.form.get("selling_price") or 0),
                "stock_quantity": int(request.form.get("stock_quantity") or 0),
                "min_stock_level": int(request.form.get("min_stock_level") or 10),
                "reorder_quantity": int(request.form.get("reorder_quantity") or 50),
                "description": request.form.get("description", "").strip(),
            }
            if not data["name"]:
                flash("Product name is required.", "error")
                return redirect(url_for("products.index"))

            if action == "add":
                last = dbFetchOne("SELECT product_code FROM products ORDER BY id DESC LIMIT 1")
                num = (int(last["product_code"][3:]) + 1) if last else 1
                data["product_code"] = f"PRD{num:03d}"
                new_id = dbInsert("products", data)
                if data["stock_quantity"] > 0:
                    dbInsert("inventory", {
                        "product_id": new_id, "movement_type": "in",
                        "quantity": data["stock_quantity"], "reference": "Initial Stock",
                        "moved_by": get_current_user()["id"],
                    })
                flash("Product added successfully.", "success")
            else:
                pid = int(request.form.get("product_id") or 0)
                dbUpdate("products", data, "id = ?", (pid,))
                flash("Product updated successfully.", "success")
            return redirect(url_for("products.index"))

        if action == "delete":
            pid = int(request.form.get("product_id") or 0)
            dbQuery("UPDATE products SET status='inactive' WHERE id=?", (pid,))
            flash("Product deleted.", "success")
            return redirect(url_for("products.index"))

    search = request.args.get("search", "").strip()
    cat_filter = int(request.args.get("category") or 0)
    page = max(1, int(request.args.get("page") or 1))
    per_page = 10
    offset = (page - 1) * per_page

    where = "WHERE p.status='active'"
    params = []
    if search:
        where += " AND p.name LIKE ?"
        params.append(f"%{search}%")
    if cat_filter:
        where += " AND p.category_id=?"
        params.append(cat_filter)

    total = dbFetchOne(f"SELECT COUNT(*) AS v FROM products p {where}", tuple(params))
    products = dbFetchAll(
        f"""SELECT p.*, c.name AS category_name, s.name AS supplier_name
            FROM products p
            LEFT JOIN categories c ON c.id=p.category_id
            LEFT JOIN suppliers s ON s.id=p.supplier_id
            {where} ORDER BY p.created_at DESC LIMIT ? OFFSET ?""",
        tuple(params) + (per_page, offset),
    )
    for p in products:
        if p["stock_quantity"] == 0:
            p["badge"], p["label"] = "badge-out-stock", "Out of Stock"
        elif p["stock_quantity"] <= p["min_stock_level"]:
            p["badge"], p["label"] = "badge-low-stock", "Low Stock"
        else:
            p["badge"], p["label"] = "badge-in-stock", "In Stock"

    categories = dbFetchAll("SELECT * FROM categories ORDER BY name")
    suppliers = dbFetchAll("SELECT * FROM suppliers WHERE status='active' ORDER BY name")
    total_pages = (total["v"] + per_page - 1) // per_page if total["v"] else 0

    return render_template(
        "products/index.html",
        page_title="Products", active_menu="products",
        products=products, categories=categories, suppliers=suppliers,
        total=total["v"], total_pages=total_pages, page=page,
        search=search, cat_filter=cat_filter,
    )
