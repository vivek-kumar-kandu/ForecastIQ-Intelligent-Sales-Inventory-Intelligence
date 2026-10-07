# ForecastinQ (Python / Flask + SQLite Edition)

This is a full conversion of the original **ForecastinQ** PHP + MySQL
inventory & sales-forecasting app to **Python (Flask) + SQLite**.
All the original modules, pages, and functionality (dashboard, products,
inventory, restocking, sales, customers, suppliers, forecasting, reports,
notifications, settings, and user management) have been reproduced —
same look & feel (Bootstrap 5 UI, charts, dark/light theme), same
business logic (forecasting algorithms, stock alerts, CSV exports, etc.),
now running on a Python backend with a SQLite database instead of PHP/MySQL.

## Requirements

- Python 3.9 or newer
- pip

No MySQL/XAMPP/Apache needed — SQLite is a single file, built into Python.

## 1. Install dependencies

Open a terminal in this folder and run:

```bash
pip install -r requirements.txt
```

(If you use a virtual environment, create/activate it first:
`python -m venv venv && source venv/bin/activate` on macOS/Linux, or
`venv\Scripts\activate` on Windows.)

## 2. Create the database

This creates `database/forecastinq.db` and seeds it with the same demo
data as the original project (users, categories, products, sample sales).

```bash
python init_db.py
```

Run this again any time you want to reset the database back to the
original demo data (it will delete and recreate the .db file).

## 3. Run the app

```bash
python app.py
```

Then open your browser at:

```
http://localhost:5000
```

## Demo login credentials

| Username  | Password   | Role    |
|-----------|-----------|---------|
| admin     | Admin@123 | admin   |
| manager   | Admin@123 | manager |
| staff     | Admin@123 | staff   |

(You can also register a new account from the login screen.)

## Project structure

```
ForecastinQ-Flask/
├── app.py                 # Flask app factory / entry point
├── config.py               # App configuration (paths, secret key, etc.)
├── db.py                    # SQLite connection + query helpers
├── utils.py                 # Auth, CSRF, formatting, forecasting algorithms
├── init_db.py                # Creates & seeds the SQLite database
├── requirements.txt
├── database/
│   ├── schema.sql            # SQLite schema (converted from the original MySQL schema)
│   └── forecastinq.db        # The SQLite database file (created by init_db.py)
├── blueprints/                # One Flask Blueprint per module (mirrors the original /modules folder)
│   ├── auth.py                 (login / register / logout)
│   ├── dashboard.py
│   ├── products.py
│   ├── inventory.py             (stock levels + restocking)
│   ├── sales.py
│   ├── customers.py
│   ├── suppliers.py
│   ├── forecasting.py            (moving average / exponential smoothing / linear regression)
│   ├── reports.py                (sales & inventory reports + CSV export)
│   ├── notifications.py
│   ├── settings.py
│   └── users.py                  (admin-only user management)
├── templates/                 # Jinja2 templates (one folder per module, plus base.html)
└── static/
    ├── css/app.css             # Original stylesheet (unchanged)
    ├── js/app.js                # Original JS (sidebar, theme toggle, Chart.js helpers — unchanged)
    └── images/uploads/
```

## Notes on the conversion

- **Database**: MySQL `ENUM`/`AUTO_INCREMENT` types were converted to SQLite
  `CHECK` constraints / `INTEGER PRIMARY KEY AUTOINCREMENT`. All tables,
  relationships, and sample data are preserved.
- **Passwords**: the original PHP demo hashes were bcrypt (PHP-specific).
  `init_db.py` generates fresh Werkzeug password hashes for the same demo
  accounts/password (`Admin@123`), so login works identically.
- **Sessions/CSRF**: Flask's server-side session + a custom CSRF token
  (matching the original hand-rolled PHP CSRF approach) are used instead
  of PHP sessions.
- **Front-end**: The Bootstrap 5 markup, custom CSS (`app.css`) and
  JavaScript (`app.js`, including the Chart.js helper functions) are
  reused unchanged — only the templating language changed from PHP to
  Jinja2.
- **Business logic**: all forecasting algorithms (moving average,
  exponential smoothing, linear regression, confidence scoring), stock
  adjustment logic, sale recording (with automatic inventory deduction),
  and CSV report exports were ported line-for-line into Python.

## Resetting demo data

```bash
python init_db.py
```

This wipes and recreates the database with the original seed data
(useful after testing add/edit/delete operations).
