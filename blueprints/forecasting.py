import json
from datetime import date, timedelta

from flask import Blueprint, render_template

from db import dbFetchAll
from utils import (
    login_required, moving_average, exponential_smoothing,
    linear_regression, forecast_confidence,
)

bp = Blueprint("forecasting", __name__)


def _add_months(d: date, months: int) -> date:
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day, 28)
    return date(year, month, day)


@bp.route("/")
@login_required
def index():
    historical = dbFetchAll(
        """
        SELECT strftime('%Y-%m', sale_date) AS month_key, COALESCE(SUM(grand_total),0) AS total
        FROM sales
        WHERE status='completed' AND sale_date >= date('now','-12 months')
        GROUP BY month_key ORDER BY month_key ASC
        """
    )
    hist_map = {r["month_key"]: r["total"] for r in historical}

    today = date.today()
    months, actuals = [], []
    for i in range(11, -1, -1):
        d = _add_months(today, -i)
        key = d.strftime("%Y-%m")
        months.append(d.strftime("%b %Y"))
        actuals.append(float(hist_map.get(key, 0)))

    ma_predicted = moving_average(actuals, 3)
    es_predicted = exponential_smoothing(actuals, 0.3)
    lr_result = linear_regression(actuals)
    lr_predicted = lr_result["predicted"]

    ma_next = ma_predicted[-1] if ma_predicted else 0
    es_next = es_predicted[-1] if es_predicted else 0
    lr_next = lr_predicted[-1] if lr_predicted else 0
    ensemble = round((ma_next + es_next + lr_next) / 3, 2)

    ma_conf = forecast_confidence(actuals[-6:], ma_predicted[-7:-1] if len(ma_predicted) >= 7 else ma_predicted[:-1])
    es_conf = forecast_confidence(actuals[-6:], es_predicted[-7:-1] if len(es_predicted) >= 7 else es_predicted[:-1])
    lr_conf = forecast_confidence(actuals[-6:], lr_predicted[-7:-1] if len(lr_predicted) >= 7 else lr_predicted[:-1])

    product_forecasts = dbFetchAll(
        """
        SELECT p.id, p.name, p.product_code, p.stock_quantity, p.selling_price,
               COALESCE(SUM(si.quantity),0) AS total_sold,
               COALESCE(AVG(si.quantity),0) AS avg_monthly
        FROM products p
        LEFT JOIN sales_items si ON si.product_id = p.id
        LEFT JOIN sales s ON s.id = si.sale_id AND s.status='completed' AND s.sale_date >= date('now','-3 months')
        WHERE p.status='active'
        GROUP BY p.id
        ORDER BY total_sold DESC LIMIT 10
        """
    )
    for pf in product_forecasts:
        predicted = round(pf["avg_monthly"] * 1.1)
        coverage = round(pf["stock_quantity"] / max(predicted, 1), 1) if predicted > 0 else 99
        pf["predicted"] = predicted
        pf["coverage"] = coverage
        pf["need_restock"] = pf["stock_quantity"] < predicted

    next_week = (today + timedelta(days=7)).strftime("%d %b")
    next_month = _add_months(today, 1).strftime("%b %Y")
    nq = _add_months(today, 3)
    next_quarter = f"{nq.strftime('%b')}\u2013{nq.strftime('%b %Y')}"
    next_year = str(today.year + 1)

    algos = [
        ("Moving Average (3-period)", ma_next, ma_conf, "#4f46e5",
         "Smooths out short-term fluctuations using the average of 3 recent periods."),
        ("Exponential Smoothing (\u03b1=0.3)", es_next, es_conf, "#10b981",
         "Gives more weight to recent data with exponential decay factor."),
        ("Linear Regression", lr_next, lr_conf, "#f59e0b",
         "Fits a trend line and extrapolates into the future."),
    ]

    chart_data = {
        "months": json.dumps(months),
        "actuals": json.dumps(actuals),
        "ma": json.dumps(ma_predicted[:len(months)]),
        "es": json.dumps(es_predicted[:len(months)]),
        "lr": json.dumps(lr_predicted[:len(months)]),
    }

    return render_template(
        "forecasting/index.html",
        page_title="Sales Forecasting", active_menu="forecasting",
        ensemble=ensemble, next_week=next_week, next_month=next_month,
        next_quarter=next_quarter, next_year=next_year,
        algos=algos, product_forecasts=product_forecasts,
        chart_data=chart_data,
    )
