"""
Initializes the SQLite database: creates all tables from schema.sql and
seeds sample data (users, categories, products, sample sales, etc.).

Run this once before starting the app:
    python init_db.py
"""
import os
import sqlite3
from datetime import date, timedelta
from werkzeug.security import generate_password_hash

import config

DEMO_PASSWORD = "Admin@123"


def build_database():
    os.makedirs(os.path.dirname(config.DATABASE_PATH), exist_ok=True)

    if os.path.exists(config.DATABASE_PATH):
        os.remove(config.DATABASE_PATH)

    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row

    with open(config.SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    # Inject a real password hash for the 3 demo users (all share the same demo password)
    password_hash = generate_password_hash(DEMO_PASSWORD)
    schema_sql = schema_sql.replace("__HASH__", password_hash)

    conn.executescript(schema_sql)
    conn.commit()

    _seed_sample_sales(conn)

    conn.commit()
    conn.close()
    print(f"Database created at: {config.DATABASE_PATH}")
    print("Demo accounts (username / password):")
    print("  admin   / Admin@123  (role: admin)")
    print("  manager / Admin@123  (role: manager)")
    print("  staff   / Admin@123  (role: staff)")


def _seed_sample_sales(conn):
    """Seed sales spread across the last 6 months so dashboard/forecast charts
    have realistic, always-current data (dates are relative to 'today')."""
    today = date.today()

    def months_ago(n, day=5):
        month = today.month - n
        year = today.year
        while month <= 0:
            month += 12
            year -= 1
        try:
            return date(year, month, day)
        except ValueError:
            return date(year, month, 28)

    sales = [
        # (customer_id, user_id, total, discount, tax, grand_total, payment, sale_date)
        (1, 2, 79999, 2000, 13860, 91859, "card", months_ago(5, 5)),
        (2, 3, 1499, 0, 270, 1769, "cash", months_ago(5, 8)),
        (3, 2, 55000, 1000, 9720, 63720, "online", months_ago(4, 15)),
        (4, 3, 12999, 500, 2250, 14749, "upi", months_ago(4, 1)),
        (5, 2, 89999, 3000, 15660, 102659, "card", months_ago(3, 10)),
        (1, 3, 499, 0, 90, 589, "cash", months_ago(2, 5)),
        (2, 2, 1999, 100, 342, 2241, "upi", months_ago(2, 20)),
        (3, 3, 1299, 0, 234, 1533, "cash", months_ago(1, 2)),
        (4, 2, 79999, 2000, 13860, 91859, "card", months_ago(1, 14)),
        (5, 3, 650, 0, 117, 767, "cash", months_ago(0, 3)),
    ]
    products_for_sale = [2, 4, 3, 8, 2, 6, 9, 5, 1, 10]  # matches sale index -> product_id

    for idx, (cust, user, total, disc, tax, grand, pay, sdate) in enumerate(sales, start=1):
        code = f"SALE-{sdate.year}-{idx:04d}"
        cur = conn.execute(
            """INSERT INTO sales
               (sale_code, customer_id, user_id, total_amount, discount, tax, grand_total,
                payment_method, status, sale_date)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'completed', ?)""",
            (code, cust, user, total, disc, tax, grand, pay, sdate.isoformat()),
        )
        sale_id = cur.lastrowid
        product_id = products_for_sale[idx - 1]
        conn.execute(
            """INSERT INTO sales_items (sale_id, product_id, quantity, unit_price, total_price)
               VALUES (?, ?, 1, ?, ?)""",
            (sale_id, product_id, total, total),
        )
        # bump customer's total_purchases
        conn.execute(
            "UPDATE customers SET total_purchases = total_purchases + ? WHERE id = ?",
            (grand, cust),
        )


if __name__ == "__main__":
    build_database()
