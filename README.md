# ForecastIQ — Intelligent Sales Forecasting & Inventory Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-SQLite3-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Chart.js](https://img.shields.io/badge/Charts-Chart.js-FF6384?logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/vivek-kumar-kandu/ForecastIQ-Intelligent-Sales-Inventory-Intelligence/pulls)

> **ForecastIQ** is an end-to-end, AI-powered sales forecasting and inventory intelligence platform built with Python (Flask) and SQLite. It delivers predictive demand forecasting, automated reorder recommendations, real-time stock-out anomaly prevention, multi-item point-of-sale (POS) processing, and role-based access control.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Forecasting Engine & Mathematics](#-forecasting-engine--mathematics)
- [Repository Structure & Milestones](#-repository-structure--milestones)
- [Quickstart & Local Installation](#-quickstart--local-installation)
- [Demo Credentials](#-demo-credentials)
- [Database Architecture](#-database-architecture)
- [Application Blueprint Routes](#-application-blueprint-routes)
- [Security & Production Readiness](#-security--production-readiness)
- [Contributing & License](#-contributing--license)

---

## 🚀 Overview

ForecastIQ transforms raw transaction logs into actionable inventory insights. Designed with a clean **Application Factory** pattern and modular Flask blueprints, the system eliminates bulky external ML dependencies by implementing core time-series algorithms in optimized, native Python.

Whether tracking fast-moving items, calculating optimal safety stock levels, or preventing costly over-stock and stock-out scenarios, ForecastIQ equips retail and supply chain teams with the exact tools needed to optimize working capital.

---

## ✨ Key Features

### 📊 1. Executive Intelligence Dashboard
- **Real-Time KPIs**: Total revenue, daily sales velocity, monthly turnover, total active SKUs, and inventory valuation calculated at cost basis.
- **Interactive Visualizations**: 6-month historical revenue trend lines, product category share breakdowns, and real-time inventory health status gauges powered by Chart.js.
- **Actionable Alerts**: Highlights out-of-stock items, critical thresholds, and low-stock warnings at a glance.

### 📈 2. Triple-Algorithm Sales Forecasting Engine
- **Moving Average (3-Period)**: Smooths short-term demand variations to reveal fundamental baseline trajectory.
- **Exponential Smoothing (α = 0.3)**: Employs geometric weight decay, giving higher relevance to recent sales surges.
- **Linear Regression (OLS)**: Fits least-squares trend lines to project forward-looking growth or decline trends.
- **Ensemble Model**: Blends all three methodologies to deliver a consensus projection with reduced model variance.
- **Accuracy Confidence Scoring**: Computes dynamic confidence scores using Mean Absolute Percentage Error (MAPE):
  $$\text{Confidence Score} = \max(0, 100 - \text{MAPE})$$
- **SKU Demand Run-Out Projections**: Calculates expected monthly unit demand, stock coverage ratios, and restock urgency flags.

### 📦 3. Inventory Management & Smart Restocking
- **Color-Coded Status Tracking**: Dynamic badges for `In Stock`, `Low Stock`, `Critical` (≤ 5 units), and `Out of Stock` (0 units).
- **Movement Audit Ledger**: Complete historical tracking of stock adjustments (`in`, `out`, and `adjustment`) with user attribution and timestamping.
- **Intelligent Restocking Workbench**: Suggests reorder quantities based on recent 30-day sales run rates:
  $$\text{Suggested Reorder} = \max(\text{Reorder Quantity}, \text{round}(\text{Avg Monthly Sales} \times 2))$$
  *(Implementation: `max(reorder_quantity, round(avg_monthly_sales * 2))`)*
- **Capital Requirement Estimates**: Automatically computes the purchase cost required to restock each low-inventory SKU.

### 🛒 4. Point of Sale (POS) & Sales Execution
- **Multi-Line Item Checkout**: Dynamic client-side order builder supporting multi-product cart additions with instant subtotal and tax calculation.
- **Automatic Stock Deduction**: Automatically deducts quantities from the warehouse and records movement audit entries upon checkout completion.
- **Customer Lifetime Value Tracking**: Updates customer purchase totals in real-time.
- **Flexible Payment Methods**: Full support for Cash, Card, UPI, and Online payments.

### 👥 5. Master Data Management
- **Products**: Manage product SKU code, name, category, brand, supplier, cost price, selling price, safety stock levels, and reorder units.
- **Customers**: Directory of customer contact details, addresses, and cumulative order metrics.
- **Suppliers**: Vendor database with active catalog counts and direct supplier contact info.
- **Categories**: Dynamic category groupings with revenue contribution tracking.

### 📑 6. Reports & Instant CSV Data Export
- Comprehensive date-filtered sales summaries, order totals, and discount breakdowns.
- Inventory valuation reports with stock levels and total asset value.
- High-speed streaming CSV data exports for:
  - `sales_YYYYMMDD.csv`
  - `inventory_YYYYMMDD.csv`
  - `products_YYYYMMDD.csv`

### 🛡️ 7. Security & Role-Based Access Control (RBAC)
- Three permission levels:
  - **Admin**: Full access including user provisioning, password resets, and system configuration.
  - **Manager**: Operations, inventory, restock orders, sales, forecasting, and analytics.
  - **Staff**: POS checkout, product lookup, and customer directory access.
- Secure password hashing via Werkzeug (`scrypt` / `pbkdf2`).
- Custom CSRF protection on all state-altering POST requests.
- Brute-force throttling delays on failed authentication attempts.

---

## 🧮 Forecasting Engine & Mathematics

ForecastIQ implements time-series models from scratch in `utils.py` without external ML dependencies. The table below outlines each model, mathematical formulation, hyperparameter configuration, and operational characteristics:

| Model | Classification | Mathematical Formulation | Parameters & Tuning | Sensitivity & Dynamics | Best Suited For |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Simple Moving Average (SMA)** | Time-Series | $\hat{y}_{t+1} = \frac{y_t + y_{t-1} + y_{t-2}}{3}$ | Window $k = 3$ | Equal weights across trailing window; filters short-term transaction noise | Stable demand items with consistent replenishment run-rates |
| **Exponential Smoothing (SES)** | Time-Series | $\hat{y}_{t+1} = \alpha y_t + (1 - \alpha) S_{t-1}$ | Alpha $\alpha = 0.3$ | Geometric decay; weights recent sales velocity over distant history | Fast-moving SKUs with seasonal shifts or promotional demand spikes |
| **Linear Regression (OLS)** | Econometric | $\hat{y} = mx + b$ <br> $m = \frac{n\sum xy - \sum x \sum y}{n\sum x^2 - (\sum x)^2}$ | Slope $m$, Intercept $b$ | Extrapolates multi-month directional growth or contraction | Growing or declining product categories across 6–12 months |
| **Ensemble Consensus** | Hybrid Meta-Model | $\hat{y}_{\text{final}} = \frac{\text{MA} + \text{ES} + \text{LR}}{3}$ | Equal weights ($w_i = \frac{1}{3}$) | Blends baseline, recency, and trend models to minimize prediction variance | Store-wide executive demand and revenue forecasting |
| **Confidence Scoring** | Validation Metric | $\text{Score} = \max(0, 100 - \text{MAPE})$ | $\text{MAPE} = \frac{100}{n} \sum \frac{\text{abs}(y - \hat{y})}{y}$ | Trailing 6-month backtesting against actual closed transactions | Automated restock risk scoring and inventory safety buffer sizing |

### 🛠️ Algorithmic Implementation (`utils.py`)

```python
# Moving Average: trailing k-period mean + 1-step forward extrapolation
def moving_average(data, period=3):
    return [round(sum(data[i-period+1:i+1]) / period, 2) for i in range(period-1, len(data))] + [round(sum(data[-period:]) / period, 2)]

# Exponential Smoothing: recency-weighted geometric decay (alpha = 0.3)
def exponential_smoothing(data, alpha=0.3):
    res = [data[0]]
    for x in data[1:]: res.append(round(alpha * x + (1 - alpha) * res[-1], 2))
    return res + [round(alpha * res[-1] + (1 - alpha) * res[-1], 2)]

# Linear Regression: Ordinary Least Squares (OLS) slope & intercept
def linear_regression(y):
    n, x = len(y), list(range(1, len(y) + 1))
    m = (n * sum(x[i]*y[i] for i in range(n)) - sum(x)*sum(y)) / ((n * sum(xi**2 for xi in x) - sum(x)**2) or 1)
    b = (sum(y) - m * sum(x)) / n if n else 0
    return {"slope": round(m, 4), "intercept": round(b, 4), "predicted": [round(m*xi + b, 2) for xi in range(1, n+2)]}
```

---

## 📂 Repository Structure & Milestones

The repository offers both the **complete integrated production application** and an **incremental milestone curriculum**:

```text
ForecastIQ/
├── ForecastIQ-Complete/       # Complete production application (all modules integrated)
├── milestone-4/               # Milestone 4: Complete app with Forecasting & Administration
├── milestone-3/               # Milestone 3: Sales, Notifications, and CSV Reports
├── milestone-2/               # Milestone 2: Products, Inventory, Customers & Suppliers
├── milestone-1/               # Milestone 1: Authentication & Dashboard Foundation
├── ForecastIQ-GitHub/         # Historical milestone archive
├── README.md                  # Project documentation & guides
└── .gitignore                 # Repository ignore rules
```

### Module Breakdown (Inside `milestone-4/` or `ForecastIQ-Complete/`)

```text
├── app.py                     # Flask application factory and context processors
├── config.py                  # Environment and database configuration
├── db.py                      # SQLite connection pooling & query abstractions
├── init_db.py                 # Schema migration & rolling 6-month seed generator
├── requirements.txt           # Minimal dependencies (Flask 3.0.3, Werkzeug 3.0.3)
├── utils.py                   # Math algorithms, auth decorators, and formatters
├── database/
│   ├── schema.sql             # Full DDL schema with relational constraints
│   └── forecastinq.db         # SQLite runtime database (generated by init_db.py)
├── blueprints/
│   ├── auth.py                # Login, registration, session termination
│   ├── dashboard.py           # Metrics aggregation and Chart.js feeds
│   ├── products.py            # Product catalog CRUD & threshold configurations
│   ├── inventory.py           # Stock movements and automated restock logic
│   ├── sales.py               # POS checkout and inventory deduction
│   ├── forecasting.py         # Time-series forecasting and confidence scoring
│   ├── reports.py             # Analytics reporting and CSV export streaming
│   ├── customers.py           # Customer profiles and purchase volumes
│   ├── suppliers.py           # Supplier registry and catalog links
│   ├── notifications.py       # Notification dispatch and read-state management
│   ├── settings.py            # Global company and store settings (Admin only)
│   └── users.py               # User account administration (Admin only)
├── templates/                 # Modular Jinja2 HTML templates
└── static/
    ├── css/app.css            # Responsive custom styles and theme variables
    └── js/app.js              # Sidebar toggle, dark mode, Chart.js renderers
```

---

## 💻 Quickstart & Local Installation

### Prerequisites
- **Python 3.9+**
- **pip**

### 1. Clone the Repository
```bash
git clone https://github.com/vivek-kumar-kandu/ForecastIQ-Intelligent-Sales-Inventory-Intelligence.git
cd ForecastIQ-Intelligent-Sales-Inventory-Intelligence
```

### 2. Navigate to the Complete App (or Desired Milestone)
```bash
cd milestone-4
# Alternatively: cd ForecastIQ-Complete
```

### 3. Create & Activate a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Initialize & Seed the Database
```bash
python init_db.py
```
> **Note:** `init_db.py` creates the SQLite database and seeds 6 months of historical transactions relative to the current date so that all dashboard charts and forecasting models display immediate, meaningful data.

### 6. Launch the Server
```bash
python app.py
```

Open your browser and navigate to:
```
http://localhost:5000
```

---

## 🔑 Demo Credentials

The pre-seeded database includes three ready-to-use accounts with different access tiers:

| Username | Role | Password | Access Privileges |
| :--- | :--- | :--- | :--- |
| **`admin`** | Administrator | `Admin@123` | Full access: Settings, User Management, Forecasting, Inventory, Sales, Reports |
| **`manager`** | Store Manager | `Admin@123` | Operations access: Forecasting, Restocking, Products, Sales, Reports |
| **`staff`** | Sales Staff | `Admin@123` | Frontline access: POS Checkout, Product Catalog, Customer Directory |

*(New accounts can also be self-registered directly from the `/auth/register` page.)*

---

## 🗄️ Database Architecture & Relational Schema

The SQLite relational database (`database/forecastinq.db`) is structured with standard third-normal form normalization, foreign key integrity (`PRAGMA foreign_keys = ON`), cascade lifecycle policies, and strict `CHECK` constraints defined in `database/schema.sql`:

| Module / Domain | Table Name | Primary Key | Foreign Relationships | Key Attributes | Integrity Rules & Business Logic |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Identity & Access** | **`users`** | `id` (AUTO) | None | `full_name`, `email`, `username`, `phone`, `password_hash`, `role`, `status` | `email` & `username` UNIQUE; `CHECK(role IN ('admin','manager','staff'))`; `CHECK(status IN ('active','inactive'))` |
| **Catalog Master** | **`categories`** | `id` (AUTO) | None | `name`, `description` | Parent taxonomy classification for product catalog |
| **Catalog Master** | **`suppliers`** | `id` (AUTO) | None | `supplier_code`, `name`, `email`, `phone`, `address`, `city`, `country`, `status` | `supplier_code` UNIQUE (e.g. `SUP001`); Active/inactive vendor directory |
| **Catalog Master** | **`products`** | `id` (AUTO) | `category_id` → `categories.id` *(SET NULL)*<br>`supplier_id` → `suppliers.id` *(SET NULL)* | `product_code`, `name`, `brand`, `cost_price`, `selling_price`, `stock_quantity`, `min_stock_level`, `reorder_quantity` | `product_code` UNIQUE (e.g. `PRD001`); Tracks profit margins, automated reorder triggers, and safety stock levels |
| **Customer Master** | **`customers`** | `id` (AUTO) | None | `customer_code`, `name`, `email`, `phone`, `address`, `city`, `total_purchases` | `customer_code` UNIQUE (e.g. `CUST001`); Real-time cumulative order volume and lifetime spend tracking |
| **Sales & POS** | **`sales`** | `id` (AUTO) | `customer_id` → `customers.id` *(SET NULL)*<br>`user_id` → `users.id` *(SET NULL)* | `sale_code`, `total_amount`, `discount`, `tax`, `grand_total`, `payment_method`, `status`, `sale_date` | `sale_code` UNIQUE (`SALE-YYYY-XXXX`); `CHECK(payment_method IN ('cash','card','online','upi'))`; `CHECK(status IN ('completed','pending','cancelled'))` |
| **Sales & POS** | **`sales_items`** | `id` (AUTO) | `sale_id` → `sales.id` *(CASCADE)*<br>`product_id` → `products.id` *(CASCADE)* | `quantity`, `unit_price`, `total_price` | Multi-line checkout items; Deleting a sale cascades items; Triggers automated inventory deduction |
| **Inventory Ledger** | **`inventory`** | `id` (AUTO) | `product_id` → `products.id` *(CASCADE)*<br>`moved_by` → `users.id` *(SET NULL)* | `movement_type`, `quantity`, `reference`, `notes`, `created_at` | `CHECK(movement_type IN ('in','out','adjustment'))`; Immutable audit trail for warehouse inward, sales outward, and stock calibrations |
| **Predictive Analytics** | **`forecasts`** | `id` (AUTO) | `product_id` → `products.id` *(SET NULL)*<br>`generated_by` → `users.id` *(SET NULL)* | `forecast_type`, `algorithm`, `forecast_date`, `predicted_sales`, `actual_sales`, `confidence_score` | `CHECK(forecast_type IN ('weekly','monthly','quarterly','yearly'))`; `CHECK(algorithm IN ('linear_regression','moving_average','exponential_smoothing'))` |
| **Alerts & Operations**| **`notifications`**| `id` (AUTO) | `user_id` → `users.id` *(CASCADE)* | `type`, `title`, `message`, `is_read`, `created_at` | `CHECK(type IN ('low_stock','out_of_stock','forecast','sales_target','system'))`; In-app alert queue with unread badge counter |
| **Analytics Archive** | **`reports`** | `id` (AUTO) | `generated_by` → `users.id` *(SET NULL)* | `report_type`, `parameters`, `file_path`, `created_at` | Historical CSV export registry with date-range filter parameter tracking |
| **Store Configuration**| **`settings`** | `id` (AUTO) | None | `setting_key`, `setting_value`, `updated_at` | `setting_key` UNIQUE; Admin-controlled store metadata, default currency (`₹`), tax rates, and safety thresholds |

---

## 🌐 Application Blueprint Routes

| Blueprint | Route Prefix | Primary Endpoints | Access Level |
| :--- | :--- | :--- | :--- |
| **Auth** | `/auth` | `/login`, `/register`, `/logout` | Public |
| **Dashboard** | `/dashboard` | `/` (KPIs, Charts, Recent Activity) | Logged-in |
| **Products** | `/products` | `/` (CRUD, Search, Filter by Category) | Logged-in |
| **Inventory** | `/inventory` | `/` (Stock Ledger, Manual Adjustments), `/restocking` | Logged-in |
| **Sales** | `/sales` | `/` (POS Multi-Item Checkout, Transaction History) | Logged-in |
| **Forecasting**| `/forecasting` | `/` (Model Outputs, Ensemble Predictions, SKU Analysis) | Logged-in |
| **Reports** | `/reports` | `/` (Sales & Inventory Summaries), `/export` (CSV) | Logged-in |
| **Customers** | `/customers` | `/` (Customer List, Add, Edit, Delete) | Logged-in |
| **Suppliers** | `/suppliers` | `/` (Supplier Directory, Product Associations) | Logged-in |
| **Notifications**| `/notifications`| `/` (Alerts Feed, Mark All Read) | Logged-in |
| **Settings** | `/settings` | `/` (Company Info, Tax Rate, Low Stock Thresholds) | **Admin Only** |
| **Users** | `/users` | `/` (User Provisioning, Role Assignment, Deactivation)| **Admin Only** |

---

## 🔒 Security & Production Readiness

- **Secret Key**: Set `SECRET_KEY` via environment variable in production environments.
- **Database Backups**: As SQLite is a serverless single-file database (`forecastinq.db`), backup simply involves copying the database file during quiet periods or utilizing the SQLite backup API.
- **CSRF Protection**: All POST endpoints validate session-bound CSRF tokens to block cross-site request forgery attacks.
- **SQL Injection Prevention**: All queries in `db.py` use parameterized queries (`?` placeholders).

---

## 🤝 Contributing

Contributions, feature requests, and improvements are welcome!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is open-source software licensed under the [MIT License](LICENSE).

---

<p align="center">
  <b>Developed & Maintained by <a href="https://github.com/vivek-kumar-kandu">Vivek Kumar Kandu</a></b>
</p>
