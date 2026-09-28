# Milestone 3 — Sales, Notifications & Reports

## What's new since Milestone 2
Everything from Milestones 1–2 **plus**:
- `blueprints/sales.py` — create sales, sale line items, sale status
- `blueprints/notifications.py` — low-stock / system notifications
- `blueprints/reports.py` — report views + CSV export (`reports.export`)

Dashboard's "View All" (Sales) link now works, and the bell icon in the
topbar starts showing real notifications.

## Folder structure changes
```
blueprints/
├── ...(Milestone 1 & 2 files)
├── sales.py            # NEW
├── notifications.py    # NEW
└── reports.py          # NEW

templates/
├── ...(Milestone 1 & 2 folders)
├── sales/               # NEW
├── notifications/       # NEW
└── reports/             # NEW
```

## Setup steps
Same pattern, run inside `Milestone-3/`:
1. `python -m venv venv` → activate
2. `pip install -r requirements.txt`
3. `python init_db.py`
4. `python app.py` → `http://localhost:5000`

## What to learn / do in this milestone
1. Read `blueprints/sales.py`: a sale involves **two tables** at once
   (`sales` and `sales_items`). Trace how a single form submission results
   in one `INSERT` into `sales` and multiple `INSERT`s into `sales_items`
   inside the same request — this is your first taste of a multi-table
   transaction.
2. Notice how completing a sale affects `products.stock_quantity` — find
   where that update happens.
3. Read `blueprints/notifications.py`: how are notifications marked as
   read/unread, and how does `utils.get_unread_notifications()` feed the
   topbar bell?
4. Read `blueprints/reports.py` and its `export` route: how is a CSV file
   streamed back to the browser instead of rendering HTML?
5. **Task:** Add a new sale status (e.g. `refunded`) and make sure it's
   handled consistently in the sales list, dashboard KPIs, and reports.
6. **Task:** Trigger a notification automatically whenever a product drops
   below its minimum stock level (if not already fully wired up, extend it).
7. **Task:** Add a date-range filter to the Reports page and make sure the
   CSV export respects the same filter.

## Checklist before moving to Milestone 4
- [ ] Can create a sale with multiple line items
- [ ] Stock quantity decreases correctly after a completed sale
- [ ] Notifications list shows relevant alerts
- [ ] Reports page renders and CSV export downloads correctly
- [ ] Dashboard "View All" (Sales) link now works
