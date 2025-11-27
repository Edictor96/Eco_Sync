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
        # (attendance, temp, weekday, special, servings actually cooked)
        records = [
            (100, 28, 1, 0, 95),
            (120, 30, 2, 0, 110),
            (80,  25, 3, 0, 76),
            (150, 27, 4, 1, 155),
            (95,  29, 5, 0, 90),
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

def _get_history(limit=60):
    """Fetch recent attendance records for training."""
    ensure_db()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "SELECT attendance,temp,weekday,special,servings "
        "FROM attendance_records ORDER BY id DESC LIMIT ?", (limit,)
    )
    rows = c.fetchall()
    conn.close()
    return rows

def _fit_attendance_regression(rows):
    """
    Fit y = a*x + b where:
      x = attendance
      y = servings actually taken
    Closed-form OLS using sums (no numpy / sklearn).
    Returns (a, b).
    """
    xs, ys = [], []
    for att, temp, wd, sp, srv in rows:
        if att is None or srv is None:
            continue
        if att <= 0:
            continue
        xs.append(float(att))
        ys.append(float(srv))

    n = len(xs)
    if n < 2:
        # Not enough data: default to ratio ~0.95 (people absent)
        return 0.95, 0.0

    sum_x = sum(xs)
    sum_y = sum(ys)
    sum_xy = sum(x*y for x, y in zip(xs, ys))
    sum_x2 = sum(x*x for x in xs)

    denom = n * sum_x2 - sum_x * sum_x
    if denom == 0:
        # fallback: simple average ratio
        ratios = [y/x for x, y in zip(xs, ys) if x]
        base_ratio = mean(ratios) if ratios else 0.95
        return base_ratio, 0.0

    a = (n * sum_xy - sum_x * sum_y) / denom
    b = (sum_y - a * sum_x) / n

    # Clamp to reasonable ranges so model doesn't go crazy
    if a < 0.7: a = 0.7
    if a > 1.1: a = 1.1
    if b < -30: b = -30
    if b > 30: b = 30

    return a, b

def predict_quantity(attendance, temp=25.0, weekday=0, special=0):
    """
    'Smart' predictor pipeline:
      1. Train linear regression on (attendance -> servings) from recent history.
      2. Apply weekday / temperature / special-event adjustments.
      3. Apply target waste buffer so we cook slightly less than predicted demand.
    """
    rows = _get_history()

    # 1) Learn a & b from history
    a, b = _fit_attendance_regression(rows)

    # Base demand purely from learned model
    base_demand = a * attendance + b
    if base_demand <= 0:
        base_demand = attendance * 0.95  # safety fallback

    # 2) Contextual adjustments
    # Temperature
    if temp > 32:
        temp_factor = 0.94   # very hot → people eat a bit less
    elif temp < 18:
        temp_factor = 1.06   # cold → eat slightly more
    else:
        temp_factor = 1.0

    # Weekday (0=Sun ... 6=Sat)
    if weekday in (5, 6):     # Sat/Sun
        weekday_factor = 1.08
    else:
        weekday_factor = 1.0

    # Special events
    special_factor = 1.15 if special else 1.0

    demand = base_demand * temp_factor * weekday_factor * special_factor

    # 3) Target waste buffer (we aim for ~5–8% buffer, not 0%)
    target_buffer = 0.93  # cook 93% of demand → rest is natural safety margin
    recommended = demand * target_buffer

    # Keep results sane: never exceed attendance by too much
    if recommended > attendance * 1.1:
        recommended = attendance * 1.1

    return max(0, int(ceil(recommended)))

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

    scored.sort(key=lambda x: x[1])
    top = [name for (name, _) in scored[:5]]
    return top
