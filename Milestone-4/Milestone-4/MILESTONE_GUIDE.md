# Milestone 4 — Forecasting, Settings & User Management (Final Project)

## What's new since Milestone 3
Everything from Milestones 1–3 **plus**:
- `blueprints/forecasting.py` — sales forecasting (Moving Average,
  Exponential Smoothing, Linear Regression — all implemented from scratch in
  `utils.py`, no external ML library required)
- `blueprints/settings.py` — app settings (admin only)
- `blueprints/users.py` — user management (admin only)

This is now the **complete ForecastIQ project**, identical in functionality
to the original app you were given at the start.

## Folder structure changes
```
blueprints/
├── ...(Milestones 1–3 files)
├── forecasting.py    # NEW
├── settings.py        # NEW
└── users.py           # NEW

templates/
├── ...(Milestones 1–3 folders)
├── forecasting/       # NEW
├── settings/           # NEW
└── users/              # NEW
```

The Admin nav section (User Management, Settings) now appears — but only for
users whose role is `admin` (check `current_user.role == 'admin'` in
`templates/base.html`).

## Setup steps
Same pattern, run inside `Milestone-4/`:
1. `python -m venv venv` → activate
2. `pip install -r requirements.txt`
3. `python init_db.py`
4. `python app.py` → `http://localhost:5000`

## What to learn / do in this milestone
1. Open `utils.py` and study the three forecasting functions:
   - `moving_average(values, window)`
   - `exponential_smoothing(values, alpha)`
   - `linear_regression(values)`
   These are plain Python (loops, sums) — no `scikit-learn`/`numpy` needed.
   Trace how `blueprints/forecasting.py` calls all three and blends them into
   an `ensemble` prediction.
2. Read `forecast_confidence()` — how does it turn prediction error into a
   confidence percentage?
3. Read `blueprints/settings.py` and `blueprints/users.py`: notice the
   `role_required("admin")` decorator (in `utils.py`) — how is it different
   from the plain `login_required` used everywhere else?
4. **Task:** Add a fourth, simple forecasting method (e.g. naive "same as
   last period") and include it in the ensemble average.
5. **Task:** Add a Settings option (e.g. currency symbol or low-stock
   threshold) that's read from the `settings` table and actually changes
   behavior elsewhere in the app.
6. **Task:** As an admin, deactivate a user from User Management and confirm
   that user can no longer log in.
7. **Stretch task:** Swap one of the hand-written forecasting functions for
   an equivalent `scikit-learn` model (e.g. `LinearRegression` from
   `sklearn.linear_model`) and compare the predictions.

## Final checklist — full project review
- [ ] Auth: login / register / logout
- [ ] Dashboard: KPIs and charts reflect real data
- [ ] Products, Inventory, Restocking
- [ ] Customers, Suppliers
- [ ] Sales (multi-item transactions), stock deduction
- [ ] Notifications
- [ ] Reports + CSV export
- [ ] Forecasting (3-method ensemble)
- [ ] Settings (admin only)
- [ ] User Management (admin only)

Congratulations — at this point you've rebuilt the entire ForecastIQ project
one milestone at a time and understand every module end to end.
