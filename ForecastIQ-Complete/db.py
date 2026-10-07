"""
Database helpers (SQLite) - Python equivalent of includes/functions.php's
dbQuery / dbFetchAll / dbFetchOne / dbInsert / dbUpdate.
"""
import sqlite3
from flask import g, current_app


def get_db():
    """Return a request-scoped SQLite connection (rows behave like dicts)."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)


def _row_to_dict(row):
    return dict(row) if row is not None else None


def dbFetchAll(sql, params=()):
    """Run a SELECT and return a list of dicts."""
    cur = get_db().execute(sql, params)
    return [dict(r) for r in cur.fetchall()]


def dbFetchOne(sql, params=()):
    """Run a SELECT and return a single dict (or None)."""
    cur = get_db().execute(sql, params)
    row = cur.fetchone()
    return _row_to_dict(row)


def dbQuery(sql, params=()):
    """Run any statement (INSERT/UPDATE/DELETE) and commit."""
    db = get_db()
    cur = db.execute(sql, params)
    db.commit()
    return cur


def dbInsert(table, data: dict):
    """Insert a row into `table` from a dict of {column: value}. Returns new row id."""
    cols = ", ".join(data.keys())
    marks = ", ".join(["?"] * len(data))
    sql = f"INSERT INTO {table} ({cols}) VALUES ({marks})"
    cur = dbQuery(sql, tuple(data.values()))
    return cur.lastrowid


def dbUpdate(table, data: dict, where: str, where_params=()):
    """Update rows in `table`. `where` uses '?' placeholders, params supplied via where_params."""
    set_clause = ", ".join(f"{k} = ?" for k in data.keys())
    sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
    params = tuple(data.values()) + tuple(where_params)
    return dbQuery(sql, params)
