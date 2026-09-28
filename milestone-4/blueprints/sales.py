import json
from datetime import date

from flask import Blueprint, render_template, request, redirect, url_for, flash

from db import dbFetchAll, dbFetchOne, dbInsert, dbUpdate, get_db
from utils import login_required, verify_csrf, get_current_user

bp = Blueprint("sales", __name__)


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST" and verify_csrf(request.form.get("csrf_token", "")):
        customer_id = int(request.form.get("customer_id") or 0) or None
        discount = float(request.form.get("discount") or 0)
        tax = float(request.form.get("tax") or 0)
        payment = request.form.get("payment_method", "cash")
        sale_date = request.form.get("sale_date") or date.today().isoformat()
        notes = request.form.get("notes", "").strip()
        product_ids = request.form.getlist("product_ids[]")
        quantities = request.form.getlist("quantities[]")
        prices = request.form.getlist("prices[]")

        if product_ids:
            total = 0.0
            for k in range(len(product_ids)):
                qty = int(quantities[k] or 0)
                price = float(prices[k] or 0)
                total += price * qty
            grand_total = total - discount + tax

            last = dbFetchOne("SELECT sale_code FROM sales ORDER BY id DESC LIMIT 1")
            num = (int(last["sale_code"][-4:]) + 1) if last else 1
            code = f"SALE-{date.today().year}-{num:04d}"

            sale_id = dbInsert("sales", {
                "sale_code": code, "customer_id": customer_id,
                "user_id": get_current_user()["id"], "total_amount": total,
                "discount": discount, "tax": tax, "grand_total": grand_total,
                "payment_method": payment, "status": "completed",
                "sale_date": sale_date, "notes": notes,
            })

            for k, pid in enumerate(product_ids):
                pid = int(pid) if pid else 0
                qty = int(quantities[k] or 0)
                price = float(prices[k] or 0)
                if pid and qty > 0:
                    dbInsert("sales_items", {
                        "sale_id": sale_id, "product_id": pid, "quantity": qty,
                        "unit_price": price, "total_price": price * qty,
                    })
                    prod = dbFetchOne("SELECT stock_quantity FROM products WHERE id=?", (pid,))
                    new_qty = max(0, (prod["stock_quantity"] if prod else 0) - qty)
                    dbUpdate("products", {"stock_quantity": new_qty}, "id=?", (pid,))
                    dbInsert("inventory", {
                        "product_id": pid, "movement_type": "out", "quantity": qty,
                        "reference": code, "moved_by": get_current_user()["id"],
                    })

            if customer_id:
                db = get_db()
                db.execute(
                    "UPDATE customers SET total_purchases = total_purchases + ? WHERE id = ?",
                    (grand_total, customer_id),
                )
                db.commit()

            flash(f"Sale {code} recorded successfully.", "success")
            return redirect(url_for("sales.index"))
        else:
            flash("Please add at least one product.", "error")

    date_from = request.args.get("from") or date.today().replace(day=1).isoformat()
    date_to = request.args.get("to") or date.today().isoformat()
    page = max(1, int(request.args.get("page") or 1))
    per_page = 10
    offset = (page - 1) * per_page

    sales = dbFetchAll(
        """
        SELECT s.*, c.name AS customer_name, u.full_name AS staff_name
        FROM sales s
        LEFT JOIN customers c ON c.id=s.customer_id
        LEFT JOIN users u ON u.id=s.user_id
        WHERE s.sale_date BETWEEN ? AND ?
        ORDER BY s.created_at DESC LIMIT ? OFFSET ?
        """,
        (date_from, date_to, per_page, offset),
    )
    for s in sales:
        item_count = dbFetchOne("SELECT COUNT(*) AS v FROM sales_items WHERE sale_id=?", (s["id"],))
        s["item_count"] = item_count["v"] if item_count else 0

    total_count = dbFetchOne("SELECT COUNT(*) AS v FROM sales WHERE sale_date BETWEEN ? AND ?", (date_from, date_to))
    total_revenue = dbFetchOne(
        "SELECT COALESCE(SUM(grand_total),0) AS v FROM sales WHERE status='completed' AND sale_date BETWEEN ? AND ?",
        (date_from, date_to),
    )
    total_pages = (total_count["v"] + per_page - 1) // per_page if total_count["v"] else 0

    customers = dbFetchAll("SELECT * FROM customers WHERE status='active' ORDER BY name")
    products = dbFetchAll("SELECT id, name, selling_price, stock_quantity FROM products WHERE status='active' AND stock_quantity>0 ORDER BY name")

    avg_order = (total_revenue["v"] / total_count["v"]) if total_count["v"] else 0

    products_json = json.dumps([
        {"id": p["id"], "name": p["name"], "price": p["selling_price"], "stock": p["stock_quantity"]}
        for p in products
    ])

    return render_template(
        "sales/index.html",
        page_title="Sales", active_menu="sales",
        sales=sales, total_count=total_count["v"], total_revenue=total_revenue["v"],
        avg_order=avg_order, total_pages=total_pages, page=page,
        date_from=date_from, date_to=date_to,
        customers=customers, products=products, products_json=products_json,
    )
