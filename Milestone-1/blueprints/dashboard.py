import json
from datetime import date, datetime

from flask import Blueprint, render_template

from db import dbFetchOne, dbFetchAll
from utils import login_required

bp = Blueprint("dashboard", __name__)


@bp.route("/")
@login_required
def index():
    today = date.today()
    today_iso = today.isoformat()
    month = today.month
    year = today.year

    total_sales = dbFetchOne("SELECT COALESCE(SUM(grand_total),0) AS v FROM sales WHERE status='completed'")
    today_sales = dbFetchOne(
        "SELECT COALESCE(SUM(grand_total),0) AS v FROM sales WHERE sale_date = ? AND status='completed'",
        (today_iso,),
    )
    month_revenue = dbFetchOne(
        "SELECT COALESCE(SUM(grand_total),0) AS v FROM sales "
        "WHERE strftime('%m', sale_date) = ? AND strftime('%Y', sale_date) = ? AND status='completed'",
        (f"{month:02d}", str(year)),
    )
    total_products = dbFetchOne("SELECT COUNT(*) AS v FROM products WHERE status='active'")
    inventory_val = dbFetchOne("SELECT COALESCE(SUM(stock_quantity*cost_price),0) AS v FROM products WHERE status='active'")
    out_of_stock = dbFetchOne("SELECT COUNT(*) AS v FROM products WHERE stock_quantity=0 AND status='active'")
    low_stock = dbFetchOne("SELECT COUNT(*) AS v FROM products WHERE stock_quantity>0 AND stock_quantity<=min_stock_level AND status='active'")
    total_users = dbFetchOne("SELECT COUNT(*) AS v FROM users WHERE status='active'")

    monthly_sales = dbFetchAll(
        """
        SELECT strftime('%Y-%m', sale_date) AS ym, SUM(grand_total) AS total
        FROM sales
        WHERE sale_date >= date('now', '-6 months') AND status='completed'
        GROUP BY ym ORDER BY ym ASC
        """
    )
    for row in monthly_sales:
        dt = datetime.strptime(row["ym"], "%Y-%m")
        row["month"] = dt.strftime("%b %Y")

    cat_perf = dbFetchAll(
        """
        SELECT c.name AS name, COALESCE(SUM(si.total_price),0) AS revenue
        FROM categories c
        LEFT JOIN products p ON p.category_id = c.id
        LEFT JOIN sales_items si ON si.product_id = p.id
        LEFT JOIN sales s ON s.id = si.sale_id AND s.status='completed'
        GROUP BY c.id, c.name
        ORDER BY revenue DESC LIMIT 5
        """
    )

    top_products = dbFetchAll(
        """
        SELECT p.name, p.selling_price, p.stock_quantity, p.min_stock_level,
               COALESCE(SUM(si.quantity),0) AS sold
        FROM products p
        LEFT JOIN sales_items si ON si.product_id = p.id
        LEFT JOIN sales s ON s.id = si.sale_id AND s.status='completed'
        WHERE p.status='active'
        GROUP BY p.id
        ORDER BY sold DESC LIMIT 8
        """
    )
    for p in top_products:
        pct = min(100, round(p["stock_quantity"] / p["min_stock_level"] * 100)) if p["min_stock_level"] else 100
        p["pct"] = pct
        if p["stock_quantity"] == 0:
            p["status_label"], p["status_cls"] = "Out", "badge-out-stock"
            p["bar_color"] = "#ef4444"
        elif p["stock_quantity"] <= p["min_stock_level"]:
            p["status_label"], p["status_cls"] = "Low", "badge-low-stock"
            p["bar_color"] = "#f59e0b"
        else:
            p["status_label"], p["status_cls"] = "In Stock", "badge-in-stock"
            p["bar_color"] = "#10b981"

    recent_sales = dbFetchAll(
        """
        SELECT s.sale_code, s.grand_total, s.sale_date, s.status, s.payment_method,
               c.name AS customer_name
        FROM sales s
        LEFT JOIN customers c ON c.id = s.customer_id
        ORDER BY s.created_at DESC LIMIT 6
        """
    )

    in_stock = dbFetchOne("SELECT COUNT(*) AS v FROM products WHERE stock_quantity > min_stock_level AND status='active'")
    low_stock_c = dbFetchOne("SELECT COUNT(*) AS v FROM products WHERE stock_quantity>0 AND stock_quantity<=min_stock_level AND status='active'")
    critical_c = dbFetchOne("SELECT COUNT(*) AS v FROM products WHERE stock_quantity>0 AND stock_quantity<=5 AND status='active'")
    out_stock_c = dbFetchOne("SELECT COUNT(*) AS v FROM products WHERE stock_quantity=0 AND status='active'")

    cards = [
        ("Total Revenue", f"₹{total_sales['v']:,.0f}", "bi-cash-coin", "#4f46e5", "rgba(79,70,229,0.1)", "↑ All time"),
        ("Today's Sales", f"₹{today_sales['v']:,.0f}", "bi-calendar-check", "#06b6d4", "rgba(6,182,212,0.1)", today.strftime("%d %b %Y")),
        ("Monthly Revenue", f"₹{month_revenue['v']:,.0f}", "bi-graph-up-arrow", "#10b981", "rgba(16,185,129,0.1)", today.strftime("%b %Y")),
        ("Total Products", total_products["v"], "bi-box-seam-fill", "#f59e0b", "rgba(245,158,11,0.1)", "Active items"),
        ("Inventory Value", f"₹{inventory_val['v']:,.0f}", "bi-archive-fill", "#8b5cf6", "rgba(139,92,246,0.1)", "Cost price"),
        ("Out of Stock", out_of_stock["v"], "bi-x-circle-fill", "#ef4444", "rgba(239,68,68,0.1)", "Needs restocking"),
        ("Low Stock", low_stock["v"], "bi-exclamation-triangle-fill", "#f97316", "rgba(249,115,22,0.1)", "Below minimum"),
        ("Active Users", total_users["v"], "bi-people-fill", "#3b82f6", "rgba(59,130,246,0.1)", "Team members"),
    ]

    chart_data = {
        "trend_labels": json.dumps([r["month"] for r in monthly_sales]),
        "trend_values": json.dumps([r["total"] for r in monthly_sales]),
        "cat_labels": json.dumps([r["name"] for r in cat_perf]),
        "cat_values": json.dumps([r["revenue"] for r in cat_perf]),
        "inv_values": json.dumps([in_stock["v"], low_stock_c["v"], critical_c["v"], out_stock_c["v"]]),
    }

    return render_template(
        "dashboard/index.html",
        page_title="Dashboard", active_menu="dashboard",
        cards=cards, top_products=top_products, recent_sales=recent_sales,
        chart_data=chart_data,
    )
