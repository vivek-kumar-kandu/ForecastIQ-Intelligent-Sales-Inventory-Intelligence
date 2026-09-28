import csv
import io
import json
from datetime import date

from flask import Blueprint, render_template, request, Response

from db import dbFetchAll, dbFetchOne
from utils import login_required

bp = Blueprint("reports", __name__)


@bp.route("/")
@login_required
def index():
    type_ = request.args.get("type", "sales")
    from_ = request.args.get("from") or date.today().replace(day=1).isoformat()
    to_ = request.args.get("to") or date.today().isoformat()

    sales_data = dbFetchAll(
        """
        SELECT sale_date AS label, COUNT(*) AS orders, SUM(grand_total) AS revenue, SUM(discount) AS total_discount
        FROM sales
        WHERE status='completed' AND sale_date BETWEEN ? AND ?
        GROUP BY sale_date ORDER BY sale_date ASC
        """,
        (from_, to_),
    )
    for r in sales_data:
        try:
            from datetime import datetime as _dt
            r["label"] = _dt.strptime(r["label"], "%Y-%m-%d").strftime("%d %b %Y")
        except Exception:
            pass

    sales_summary = dbFetchOne(
        "SELECT COUNT(*) AS orders, COALESCE(SUM(grand_total),0) AS revenue, COALESCE(SUM(discount),0) AS discount "
        "FROM sales WHERE status='completed' AND sale_date BETWEEN ? AND ?",
        (from_, to_),
    )

    inventory_report = dbFetchAll(
        """
        SELECT p.product_code, p.name, c.name AS category, p.stock_quantity,
               p.cost_price, p.selling_price, (p.stock_quantity*p.cost_price) AS inv_value,
               p.min_stock_level,
               CASE WHEN p.stock_quantity=0 THEN 'Out of Stock'
                    WHEN p.stock_quantity<=p.min_stock_level THEN 'Low Stock'
                    ELSE 'In Stock' END AS stock_status
        FROM products p LEFT JOIN categories c ON c.id=p.category_id
        WHERE p.status='active' ORDER BY inv_value DESC
        """
    )
    inv_summary = dbFetchOne(
        "SELECT COUNT(*) AS total, COALESCE(SUM(stock_quantity*cost_price),0) AS total_value FROM products WHERE status='active'"
    )

    top_products = dbFetchAll(
        """
        SELECT p.name, p.product_code, SUM(si.quantity) AS qty_sold, SUM(si.total_price) AS revenue
        FROM sales_items si
        JOIN products p ON p.id=si.product_id
        JOIN sales s ON s.id=si.sale_id AND s.status='completed' AND s.sale_date BETWEEN ? AND ?
        GROUP BY p.id ORDER BY qty_sold DESC LIMIT 10
        """,
        (from_, to_),
    )

    out_count = sum(1 for r in inventory_report if r["stock_status"] == "Out of Stock")
    low_count = sum(1 for r in inventory_report if r["stock_status"] == "Low Stock")

    avg_order = (sales_summary["revenue"] / sales_summary["orders"]) if sales_summary["orders"] else 0

    revenue_labels = json.dumps([r["label"] for r in sales_data])
    revenue_values = json.dumps([r["revenue"] for r in sales_data])

    return render_template(
        "reports/index.html",
        page_title="Reports", active_menu="reports",
        type=type_, from_=from_, to_=to_,
        sales_data=sales_data, sales_summary=sales_summary, avg_order=avg_order,
        inventory_report=inventory_report, inv_summary=inv_summary,
        out_count=out_count, low_count=low_count, top_products=top_products,
        revenue_labels=revenue_labels, revenue_values=revenue_values,
    )


@bp.route("/export")
@login_required
def export():
    type_ = request.args.get("type", "sales")
    from_ = request.args.get("from") or date.today().replace(day=1).isoformat()
    to_ = request.args.get("to") or date.today().isoformat()

    output = io.StringIO()
    writer = csv.writer(output)
    filename = f"{type_}_{date.today().strftime('%Y%m%d')}.csv"

    if type_ == "sales":
        data = dbFetchAll(
            """
            SELECT s.sale_code, c.name AS customer, s.total_amount, s.discount, s.tax, s.grand_total,
                   s.payment_method, s.status, s.sale_date, u.full_name AS staff
            FROM sales s
            LEFT JOIN customers c ON c.id=s.customer_id
            LEFT JOIN users u ON u.id=s.user_id
            WHERE s.sale_date BETWEEN ? AND ? ORDER BY s.sale_date ASC
            """,
            (from_, to_),
        )
        writer.writerow(["Sale Code", "Customer", "Subtotal", "Discount", "Tax", "Grand Total", "Payment", "Status", "Date", "Staff"])
        for r in data:
            writer.writerow([r["sale_code"], r["customer"] or "Walk-in", r["total_amount"], r["discount"],
                              r["tax"], r["grand_total"], r["payment_method"], r["status"], r["sale_date"], r["staff"] or ""])

    elif type_ == "inventory":
        data = dbFetchAll(
            """
            SELECT p.product_code, p.name, c.name AS category, p.stock_quantity,
                   p.cost_price, p.selling_price, (p.stock_quantity*p.cost_price) AS inv_value,
                   CASE WHEN p.stock_quantity=0 THEN 'Out of Stock' WHEN p.stock_quantity<=p.min_stock_level THEN 'Low Stock' ELSE 'In Stock' END AS status
            FROM products p LEFT JOIN categories c ON c.id=p.category_id WHERE p.status='active'
            """
        )
        writer.writerow(["Code", "Product", "Category", "Stock", "Cost Price", "Selling Price", "Inventory Value", "Status"])
        for r in data:
            writer.writerow([r["product_code"], r["name"], r["category"] or "", r["stock_quantity"],
                              r["cost_price"], r["selling_price"], r["inv_value"], r["status"]])

    elif type_ == "products":
        data = dbFetchAll(
            """
            SELECT p.product_code, p.name, c.name AS cat, p.brand, p.cost_price, p.selling_price,
                   p.stock_quantity, p.min_stock_level
            FROM products p LEFT JOIN categories c ON c.id=p.category_id WHERE p.status='active'
            """
        )
        writer.writerow(["Code", "Name", "Category", "Brand", "Cost Price", "Selling Price", "Stock", "Min Stock"])
        for r in data:
            writer.writerow([r["product_code"], r["name"], r["cat"] or "", r["brand"] or "",
                              r["cost_price"], r["selling_price"], r["stock_quantity"], r["min_stock_level"]])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
