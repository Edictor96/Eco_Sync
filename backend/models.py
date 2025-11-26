# backend/models.py
import os
import sqlite3
from math import ceil
from statistics import mean

DB = os.path.join(os.path.dirname(__file__), 'db.sqlite')

def ensure_db():
    """Create tables if they don't exist."""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS attendance_records (
            id INTEGER PRIMARY KEY,
            attendance INTEGER,
            temp REAL,
            weekday INTEGER,
            special INTEGER,
            servings REAL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS waste_logs (
            id INTEGER PRIMARY KEY,
            date TEXT,
            dish TEXT,
            cooked REAL,
            consumed REAL,
            wasted REAL
        )
    """)
    conn.commit()
    conn.close()

def seed_demo():
    """Seed a small demo dataset if tables are empty."""
    ensure_db()
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Seed attendance history
    c.execute("SELECT COUNT(*) FROM attendance_records")
    if c.fetchone()[0] == 0:
        records = [
            (100, 28, 1, 0, 100),
            (120, 30, 2, 0, 120),
            (80,  25, 3, 0, 80),
            (150, 27, 4, 1, 150),
            (95,  29, 5, 0, 95),
        ]
        for r in records:
            c.execute(
                "INSERT INTO attendance_records(attendance,temp,weekday,special,servings) "
                "VALUES (?,?,?,?,?)", r
            )

    # Seed waste logs
    c.execute("SELECT COUNT(*) FROM waste_logs")
    if c.fetchone()[0] == 0:
        sample = [
            ('2025-11-10', 'Rice',  10,  8,  2),
            ('2025-11-10', 'Dal',   8,  7.5,0.5),
            ('2025-11-11', 'Rice',  12, 10, 2),
        ]
        for s in sample:
            c.execute(
                "INSERT INTO waste_logs(date,dish,cooked,consumed,wasted) "
                "VALUES (?,?,?,?,?)", s
            )

    conn.commit()
    conn.close()

def _get_history():
    """Fetch up to 60 most recent attendance records."""
    ensure_db()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "SELECT attendance,temp,weekday,special,servings "
        "FROM attendance_records ORDER BY id DESC LIMIT 60"
    )
    rows = c.fetchall()
    conn.close()
    return rows

def predict_quantity(attendance, temp=25.0, weekday=0, special=0):
    """
    Simple 'learning' predictor:
    - Uses average servings/attendance ratio from history
    - Adjusts by weekday, temperature and special events
    """
    rows = _get_history()

    # Global base ratio
    if not rows:
        base_ratio = 1.0
    else:
        ratios = [srv/att for (att, t, wd, sp, srv) in rows if att]
        base_ratio = mean(ratios) if ratios else 1.0

    # Weekday-specific adjustment
    weekday_ratios = [srv/att for (att, t, wd, sp, srv) in rows if att and wd == weekday]
    if weekday_ratios:
        weekday_factor = (mean(weekday_ratios) / base_ratio) if base_ratio else 1.0
    else:
        weekday_factor = 1.0

    # Temperature buckets
    if temp > 32:
        temp_factor = 0.93  # hot day, people eat slightly less
    elif temp < 18:
        temp_factor = 1.07  # cold day, people eat slightly more
    else:
        temp_factor = 1.0

    # Special event factor
    special_factor = 1.15 if special else 1.0

    predicted = attendance * base_ratio * weekday_factor * temp_factor * special_factor

    # Round up to next integer
    return max(0, int(ceil(predicted)))

def optimize_menu_logic(dishes_list):
    """
    Menu optimizer:
    - If a list is provided from frontend: use that.
    - If empty: fallback to aggregated waste_logs (per dish).
    - Returns up to 5 dishes with lowest waste ratio.
    """
    ensure_db()

    # Fallback to DB aggregation if nothing supplied
    if not dishes_list:
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute(
            "SELECT dish, SUM(cooked) as s, SUM(wasted) as w "
            "FROM waste_logs GROUP BY dish"
        )
        rows = c.fetchall()
        conn.close()
        dishes_list = [
            {'dish': d, 'served': s, 'waste': w}
            for (d, s, w) in rows
        ]

    if not dishes_list:
        return []

    scored = []
    for d in dishes_list:
        name = d.get('dish', 'Unknown')
        served = float(d.get('served', 0) or 0)
        waste = float(d.get('waste', 0) or 0)
        ratio = waste / served if served else 0.0
        scored.append((name, ratio))

    # Sort by lowest waste ratio
    scored.sort(key=lambda x: x[1])
    top = [name for (name, _) in scored[:5]]
    return top
