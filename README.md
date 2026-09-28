# ForecastIQ

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0.3-000000?logo=flask)
![Database](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)

ForecastIQ is a sales forecasting and inventory management app built with Flask and SQLite. The repository follows the project through four milestones; **`milestone-4/` is the complete application** and the best place to start.

## Features

- Dashboard with sales and inventory indicators
- Product, customer, supplier, and inventory management
- Multi-item sales with stock updates
- Low-stock notifications and restocking views
- Reports with CSV export
- Sales forecasts using moving average, exponential smoothing, and linear regression, combined into an ensemble
- Admin-only settings and user management
- Login, role-based access, and seeded demo data

## Run Locally

Python 3 and pip are required. From the repository root:

```powershell
cd milestone-4
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python init_db.py
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser. On macOS or Linux, activate the environment with `source .venv/bin/activate` instead.

> **Database reset:** `python init_db.py` recreates the SQLite database and removes any existing local data in that milestone. Run it for initial setup or when you intentionally want to reset the demo database.

## Demo Accounts

The initialized database includes these local demo users. All use the password `Admin@123`.

| Username | Role |
| --- | --- |
| `admin` | Admin |
| `manager` | Manager |
| `staff` | Staff |

## Milestones

| Folder | Includes |
| --- | --- |
| [`milestone-1/`](milestone-1/) | Authentication and dashboard foundations |
| [`milestone-2/`](milestone-2/) | Products, inventory, customers, and suppliers |
| [`milestone-3/`](milestone-3/) | Sales, notifications, reports, and CSV export |
| [`milestone-4/`](milestone-4/) | Forecasting, admin settings, and user management |

Each milestone is a standalone Flask app with its own `requirements.txt` and SQLite schema. Run the setup commands from inside the milestone folder you want to explore. `ForecastIQ-GitHub/` contains an earlier copy of the first two milestones for comparison.

## Security

This project is intended for local learning and demonstration. The demo accounts and development secret key are not suitable for deployment. Set a strong `SECRET_KEY` environment variable and review the app's debug settings before exposing it to a network.