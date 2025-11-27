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
    Uses regression coefficients trained in Google Colab (scikit-learn)
    + contextual multipliers + waste-reduction buffer.
    """

    # === 1) Coefficients learned from your Colab notebook ===
    # servings ≈ a_att*attendance + a_temp*temp + a_weekday*weekday + a_special*special + b
    a_att     = 0.904785
    a_temp    = -0.238449
    a_weekday = 1.120050
    a_special = 13.181931
    b         = 6.799092

    # Base predicted demand from the trained model
    demand = (
        a_att * float(attendance) +
        a_temp * float(temp) +
        a_weekday * float(weekday) +
        a_special * float(special) +
        b
    )

    # Safety fallback if something weird happens
    if demand <= 0:
        demand = float(attendance) * 0.9

    # === 2) Extra contextual tweaks (optional but good to explain in viva) ===
    # Hot / cold adjustment
    if temp > 32:
        temp_factor = 0.95        # very hot → slightly less appetite
    elif temp < 18:
        temp_factor = 1.05        # cold → slightly more food
    else:
        temp_factor = 1.0

    # Weekend bump (0=Sun … 6=Sat; adjust as per your convention)
    if weekday in (5, 6):         # Sat/Sun
        weekday_factor = 1.08
    else:
        weekday_factor = 1.0

    demand *= temp_factor * weekday_factor

    # === 3) Waste-reduction buffer ===
    # We intentionally cook a bit less than raw demand to reduce overcooking.
    target_buffer = 0.93          # cook ~93% of predicted demand
    recommended = demand * target_buffer

    # Hard sanity limit: don't go way above attendance
    max_allowed = float(attendance) * 1.10
    if recommended > max_allowed:
        recommended = max_allowed

    from math import ceil
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
