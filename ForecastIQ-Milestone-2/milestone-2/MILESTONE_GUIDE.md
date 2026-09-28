# Milestone 2 — Core Master Data (Products, Inventory, Customers, Suppliers)

## What's new since Milestone 1
Everything from Milestone 1 (setup, auth, dashboard) **plus**:
- `blueprints/products.py` — product catalog CRUD
- `blueprints/inventory.py` — stock levels + a "Restocking" view
- `blueprints/customers.py` — customer list
- `blueprints/suppliers.py` — supplier list

The Dashboard now fully lights up: its "View All" links to Products and
(later) Sales become visible, and stock-related KPIs are meaningful because
the Inventory module now exists.

## Folder structure changes
```
blueprints/
├── auth.py, dashboard.py        # from Milestone 1
├── products.py                  # NEW
├── inventory.py                 # NEW
├── customers.py                 # NEW
└── suppliers.py                 # NEW

templates/
├── auth/, dashboard/            # from Milestone 1
├── products/                    # NEW
├── inventory/                   # NEW (index.html + restocking.html)
├── customers/                   # NEW
└── suppliers/                   # NEW
```

`app.py` now registers four extra blueprints under `/products`, `/inventory`,
`/customers`, `/suppliers`. Compare it side-by-side with Milestone 1's
`app.py` to see exactly what changed — that diff *is* the lesson.

## Setup steps
Same as Milestone 1, run inside `Milestone-2/`:
1. `python -m venv venv` → activate
2. `pip install -r requirements.txt`
3. `python init_db.py`
4. `python app.py` → `http://localhost:5000`

## What to learn / do in this milestone
1. Compare `Milestone-1/app.py` and `Milestone-2/app.py`. Notice that adding
   a feature to a Flask app is mostly: **write a blueprint → register it with
   a URL prefix → add its templates.**
2. Read `blueprints/products.py`: how does it handle Create, Read, Update,
   Delete (CRUD) using plain SQL and `request.form`?
3. Read `blueprints/inventory.py` and `templates/inventory/restocking.html`:
   how is "low stock" calculated, and how does that number reach the sidebar
   badge in `base.html` (`low_stock_count`)?
4. **Task:** Add a new column to `products` (e.g. `brand`) — update
   `database/schema.sql`, the product form, and the product list table.
5. **Task:** Add simple search/filter to the Customers or Suppliers list
   (filter by name using a SQL `LIKE` query).
6. **Task:** Add validation so a product's `selling_price` can't be lower
   than its `cost_price`.

## Checklist before moving to Milestone 3
- [ ] Can add/edit/delete a product
- [ ] Inventory page shows correct stock status (in stock / low / out)
- [ ] Restocking page lists products needing reorder
- [ ] Can add/view a customer and a supplier
- [ ] Dashboard's "View All" (Products) link now works
