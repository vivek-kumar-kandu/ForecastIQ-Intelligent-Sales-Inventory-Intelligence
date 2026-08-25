# Milestone 1 — Project Setup, Database & Authentication

## What this milestone contains
A runnable Flask app with **only** these features:
- Project structure & app factory (`app.py`)
- Configuration (`config.py`)
- SQLite database layer (`db.py`, `database/schema.sql`, `init_db.py`)
- Login, Register, Logout (`blueprints/auth.py`)
- A working Dashboard as the landing page after login (`blueprints/dashboard.py`)

Everything else (Products, Inventory, Sales, Customers, Suppliers, Forecasting,
Reports, Notifications, Settings, Users) is **not included yet** — you will add
those in Milestones 2–4. The sidebar menu only shows the pages that exist in
this milestone, so the app feels complete even though it's a small slice of
the final project.

## Folder structure
```
Milestone-1/
├── app.py                 # Flask app factory, registers auth + dashboard only
├── config.py               # App config (secret key, DB path, upload folder)
├── db.py                   # SQLite connection helper (get_db, dbFetchOne, dbFetchAll, dbInsert, dbUpdate)
├── init_db.py               # Creates tables from schema.sql and seeds demo data
├── utils.py                 # Shared helpers: login_required, formatters, CSRF
├── requirements.txt
├── database/
│   └── schema.sql          # FULL schema for the whole project (all tables, created up front)
├── blueprints/
│   ├── auth.py
│   └── dashboard.py
├── templates/
│   ├── base.html            # Shared layout — nav auto-adjusts to ENABLED_MODULES
│   ├── auth/
│   └── dashboard/
└── static/
    ├── css/app.css
    └── js/app.js
```

> **Note on the schema:** `schema.sql` creates *every* table used by the final
> project (products, sales, customers, etc.), not just the ones this
> milestone touches. In real projects, database design is usually done
> up front, then features are built on top of it module by module — that's
> exactly what you'll be doing across Milestones 1–4.

## Setup steps
1. `cd Milestone-1`
2. Create and activate a virtual environment:
   - Windows: `python -m venv venv` then `venv\Scripts\activate`
   - macOS/Linux: `python3 -m venv venv` then `source venv/bin/activate`
3. `pip install -r requirements.txt`
4. `python init_db.py` (creates `database/forecastinq.db` with demo data)
5. `python app.py`
6. Open `http://localhost:5000`

**Demo login:** `admin` / `Admin@123` (also `manager` / `staff` with the same password)

## What to learn / do in this milestone
1. Trace how `app.py` uses the **application factory pattern** (`create_app()`)
   instead of a bare `Flask(__name__)`.
2. Read `db.py` — understand how a single SQLite connection is opened per
   request (`get_db`) and closed via `teardown_appcontext`.
3. Read `database/schema.sql` and sketch (on paper or a diagram tool) the
   relationships between `users`, `products`, `sales`, `sales_items`,
   `customers`, `suppliers`, `categories`.
4. Walk through `blueprints/auth.py`:
   - Why is there a `verify_csrf` check on every POST?
   - Where is the password checked? (`check_password_hash`)
   - What does `session.clear()` protect against?
5. Walk through `blueprints/dashboard.py` and see how it aggregates data with
   plain SQL (`SUM`, `GROUP BY`, `strftime`) instead of an ORM.
6. **Task:** Add a new field, e.g. `phone` validation on the register form,
   and show a friendly error message if it's missing.
7. **Task:** Change the session lifetime in `config.py` and confirm (by
   waiting or lowering it) that the user gets logged out automatically.

## Checklist before moving to Milestone 2
- [ ] App runs locally without errors
- [ ] Can register a new account
- [ ] Can log in / log out
- [ ] Dashboard loads and shows KPI cards + charts with demo data
- [ ] You can explain, in your own words, what `login_required` does
