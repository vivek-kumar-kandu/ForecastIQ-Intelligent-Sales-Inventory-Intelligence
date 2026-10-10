# ForecastinQ — Team B

An intelligent sales forecasting and inventory management web application built with Flask and SQLite.

🌐 **Live Demo:** [https://forecastiq-teamb.onrender.com](https://forecastiq-teamb.onrender.com)

**Repository:** [ForecastIQ-TeamB](https://github.com/vivek-kumar-kandu/ForecastIQ-TeamB)

---

## Features

- 📊 **Executive Dashboard**: Sales summaries, KPI metrics, and visual revenue charts
- 💰 **Sales Recording & Invoicing**: Fast order logging, multi-item invoicing, and tax calculations
- 📦 **Inventory Tracking**: Stock levels, automated restocking triggers, and audit movements
- 🔔 **Real-Time Alerts**: Low stock notifications and system status updates
- 👥 **Customer & Supplier CRM**: Directory management, purchase history, and contact details
- 📈 **Sales Forecasting**: Statistical forecasting models (Moving Average, Linear Regression, Exponential Smoothing)
- 🔐 **Role-Based Access Control**: Multi-tier permissions (`Admin`, `Manager`, `Staff`)
- ⚙️ **System Configuration**: Currency, tax rate, and notification threshold settings

---

## Live Demo & Accounts

You can try the live application here:  
👉 **[https://forecastiq-teamb.onrender.com](https://forecastiq-teamb.onrender.com)**

Pre-seeded demo accounts (all use password `Admin@123`):

| Username | Role | Description |
| --- | --- | --- |
| `admin` | Admin | Full administrative access |
| `manager` | Manager | Operational and forecasting management |
| `staff` | Staff | Standard point-of-sale and inventory access |

*You can also create a new account using the **Register** page on the live website.*

---

## Technology Stack

- **Backend**: Python 3, Flask, SQLite3
- **WSGI / Server**: Gunicorn
- **Frontend**: HTML5, Vanilla CSS3, JavaScript (Chart.js)
- **Deployment**: Render / Docker container

---

## Local Setup & Development

Use Python 3.8 or newer.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vivek-kumar-kandu/ForecastIQ-TeamB.git
   cd ForecastIQ-TeamB
   ```

2. **Create and activate a virtual environment:**

   **Windows (PowerShell):**
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS / Linux:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database (seeds sample records):**
   ```bash
   python init_db.py
   ```

5. **Run local server:**
   ```bash
   python app.py
   ```
   Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## Project Structure

```text
.
├── app.py                # Flask application, factory & route registration
├── blueprints/           # Modular route controllers
│   ├── auth.py           # Authentication & registration
│   ├── dashboard.py      # Analytics & dashboard
│   ├── products.py       # Product catalog
│   ├── inventory.py      # Stock movements
│   ├── sales.py          # POS & order processing
│   ├── forecasting.py    # Predictive algorithms
│   ├── reports.py        # Analytics export (CSV)
│   ├── customers.py      # Customer management
│   ├── suppliers.py      # Supplier management
│   ├── users.py          # User administration
│   └── settings.py       # Global app settings
├── config.py             # Application & database settings
├── database/
│   └── schema.sql        # Database schema & initial seeds
├── db.py                 # SQLite database connection helpers
├── init_db.py            # Database initialization script
├── Dockerfile            # Container deployment specification
├── Procfile              # Render / WSGI process config
├── render.yaml           # Infrastructure-as-code blueprint
├── requirements.txt      # Python dependencies
├── static/               # CSS & JavaScript assets
├── templates/            # Jinja2 HTML templates
└── utils.py              # Security, CSRF, & calculation helpers
```

---

## Configuration & Environment Variables

Copy `.env.example` to `.env` for custom configuration:

| Variable | Default | Description |
| --- | --- | --- |
| `SECRET_KEY` | *(Random)* | Session encryption key (change in production) |
| `FLASK_DEBUG` | `False` | Debug mode toggle |
| `PORT` | `5000` | Port for the web server |
| `DATABASE_PATH` | `database/forecastinq.db` | Custom path for SQLite database |
| `SESSION_COOKIE_SECURE` | `True` | Enforce HTTPS cookies in production |

---

## License

This project is licensed under the [MIT License](LICENSE).
