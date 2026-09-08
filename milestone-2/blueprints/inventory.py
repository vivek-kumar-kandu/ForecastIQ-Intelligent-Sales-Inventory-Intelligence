from flask import Blueprint, render_template, request, redirect, url_for, flash

from db import dbFetchAll, dbFetchOne, dbInsert, dbUpdate
from utils import login_required, verify_csrf, get_current_user

bp = Blueprint("inventory", __name__)


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST" and verify_csrf(request.form.get("csrf_token", "")):
        product_id = int(request.form.get("product_id") or 0)
        qty = int(request.form.get("quantity") or 0)
        movement_type = request.form.get("movement_type", "in")
        notes = request.form.get("notes", "").strip()

        if product_id and qty > 0:
            product = dbFetchOne("SELECT * FROM products WHERE id=?", (product_id,))
            if product:
                if movement_type == "out":
                    new_qty = max(0, product["stock_quantity"] - qty)
                elif movement_type == "adjustment":
                    new_qty = qty
                    qty = abs(qty - product["stock_quantity"])
                else:
                    new_qty = product["stock_quantity"] + qty

                dbUpdate("products", {"stock_quantity": new_qty}, "id = ?", (product_id,))
                dbInsert("inventory", {
                    "product_id": product_id, "movement_type": movement_type,
                    "quantity": qty, "reference": "Manual Adjustment",
                    "notes": notes, "moved_by": get_current_user()["id"],
                })
                flash("Stock updated successfully.", "success")
        return redirect(url_for("inventory.index"))

    total_value = dbFetchOne("SELECT COALESCE(SUM(stock_quantity*cost_price),0) AS v FROM products WHERE status='active'")
    total_items = dbFetchOne("SELECT COALESCE(SUM(stock_quantity),0) AS v FROM products WHERE status='active'")
    fast_moving = dbFetchOne(
        "SELECT COUNT(DISTINCT product_id) AS v FROM sales_items si JOIN sales s ON s.id=si.sale_id "
        "WHERE s.sale_date >= date('now','-30 days')"
    )
    low_stock_cnt = dbFetchOne("SELECT COUNT(*) AS v FROM products WHERE stock_quantity <= min_stock_level AND status='active'")

    products = dbFetchAll(
        "SELECT p.*, c.name AS cat FROM products p LEFT JOIN categories c ON c.id=p.category_id "
        "WHERE p.status='active' ORDER BY p.stock_quantity ASC"
    )
    for p in products:
        pct = min(100, round(p["stock_quantity"] / p["min_stock_level"] * 100)) if p["min_stock_level"] else 100
        p["pct"] = pct
        if p["stock_quantity"] == 0:
            p["label"], p["cls"], p["color"] = "Out of Stock", "badge-out-stock", "#ef4444"
        elif p["stock_quantity"] <= 5:
            p["label"], p["cls"], p["color"] = "Critical", "badge-critical", "#ef4444"
        elif p["stock_quantity"] <= p["min_stock_level"]:
            p["label"], p["cls"], p["color"] = "Low Stock", "badge-low-stock", "#f59e0b"
        else:
            p["label"], p["cls"], p["color"] = "In Stock", "badge-in-stock", "#10b981"

    movements = dbFetchAll(
        """
        SELECT i.*, p.name AS product_name, p.product_code, u.full_name AS moved_by_name
        FROM inventory i
        JOIN products p ON p.id=i.product_id
        LEFT JOIN users u ON u.id=i.moved_by
        ORDER BY i.created_at DESC LIMIT 20
        """
    )
    for m in movements:
        m["type_color"] = "#10b981" if m["movement_type"] == "in" else ("#ef4444" if m["movement_type"] == "out" else "#f59e0b")
        m["type_icon"] = "↑" if m["movement_type"] == "in" else ("↓" if m["movement_type"] == "out" else "↔")

    all_products = dbFetchAll("SELECT id, name, product_code, stock_quantity FROM products WHERE status='active' ORDER BY name")

    return render_template(
        "inventory/index.html",
        page_title="Inventory", active_menu="inventory",
        total_value=total_value["v"], total_items=total_items["v"],
        fast_moving=fast_moving["v"], low_stock_cnt=low_stock_cnt["v"],
        products=products, movements=movements, all_products=all_products,
    )


@bp.route("/restocking")
@login_required
def restocking():
    need_restock = dbFetchAll(
        """
        SELECT p.*, c.name AS cat, s.name AS supplier_name, s.email AS supplier_email,
               COALESCE((
                   SELECT AVG(si.quantity)
                   FROM sales_items si JOIN sales sa ON sa.id=si.sale_id
                   WHERE si.product_id=p.id AND sa.sale_date >= date('now','-30 days')
               ),0) AS avg_monthly_sales
        FROM products p
        LEFT JOIN categories c ON c.id=p.category_id
        LEFT JOIN suppliers s ON s.id=p.supplier_id
        WHERE p.status='active' AND p.stock_quantity <= p.min_stock_level
        ORDER BY (p.stock_quantity * 1.0 / MAX(p.min_stock_level,1)) ASC
        """
    )
    for p in need_restock:
        suggested = max(p["reorder_quantity"], round(p["avg_monthly_sales"] * 2))
        p["suggested"] = suggested
        p["est_cost"] = suggested * p["cost_price"]
        if p["stock_quantity"] == 0:
            p["priority"], p["pcls"], p["pcol"] = "Critical", "badge-critical", "#ef4444"
        elif p["stock_quantity"] <= 5:
            p["priority"], p["pcls"], p["pcol"] = "High", "badge-critical", "#f97316"
        else:
            p["priority"], p["pcls"], p["pcol"] = "Medium", "badge-low-stock", "#f59e0b"
        p["pct"] = min(100, round(p["stock_quantity"] / p["min_stock_level"] * 100)) if p["min_stock_level"] else 0

    counts = {
        "critical": dbFetchOne("SELECT COUNT(*) AS v FROM products WHERE stock_quantity<=5 AND stock_quantity>0 AND status='active'")["v"],
        "low": dbFetchOne("SELECT COUNT(*) AS v FROM products WHERE stock_quantity>5 AND stock_quantity<=min_stock_level AND status='active'")["v"],
        "out": dbFetchOne("SELECT COUNT(*) AS v FROM products WHERE stock_quantity=0 AND status='active'")["v"],
    }

    return render_template(
        "inventory/restocking.html",
        page_title="Restocking", active_menu="restocking",
        need_restock=need_restock, counts=counts,
    )
