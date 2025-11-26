# backend/models.py
import os
import sqlite3
from math import ceil

DB = os.path.join(os.path.dirname(__file__), 'db.sqlite')

def ensure_db():
    if not os.path.exists(DB):
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS attendance_records(
            id INTEGER PRIMARY KEY, attendance INTEGER, temp REAL, weekday INTEGER, special INTEGER, servings REAL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS waste_logs(
            id INTEGER PRIMARY KEY, date TEXT, dish TEXT, cooked REAL, consumed REAL, wasted REAL)''')
        conn.commit()
        conn.close()

def seed_demo():
    ensure_db()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # Check existing
    c.execute("SELECT COUNT(*) FROM attendance_records")
    if c.fetchone()[0] > 0:
        conn.close()
        return
    records = [
        (100,28,1,0,100),
        (120,30,2,0,120),
        (80,25,3,0,80),
        (150,27,4,1,150),
        (95,29,5,0,95)
    ]
    for r in records:
        c.execute('INSERT INTO attendance_records(attendance,temp,weekday,special,servings) VALUES (?,?,?,?,?)', r)
    sample = [
        ('2025-11-10','Rice',10,8,2),
        ('2025-11-10','Dal',8,7.5,0.5),
        ('2025-11-11','Rice',12,10,2),
    ]
    for s in sample:
        c.execute('INSERT INTO waste_logs(date,dish,cooked,consumed,wasted) VALUES (?,?,?,?,?)', s)
    conn.commit()
    conn.close()

# Simple prediction: use recent average servings per attendance ratio and adjust by temp/weekend/special.
def predict_quantity(attendance, temp=25.0, weekday=0, special=0):
    ensure_db()
    conn = sqlite3.connect(DB)
    df = []
    try:
        c = conn.cursor()
        c.execute('SELECT attendance, servings FROM attendance_records ORDER BY id DESC LIMIT 30')
        rows = c.fetchall()
        for r in rows:
            if r[0] and r[1]:
                df.append((r[0], r[1]))
    except Exception:
        df = []
    conn.close()

    # fallback: 1 serving per person
    if not df:
        base_ratio = 1.0
    else:
        # average servings/attendance ratio
        ratios = [srv/att if att else 1.0 for att,srv in df]
        base_ratio = sum(ratios) / len(ratios)

    # small heuristic adjustments
    temp_adj = 1.0
    if temp > 30: temp_adj = 0.95
    if temp < 20: temp_adj = 1.05
    weekday_adj = 1.0
    if weekday in (5,6): weekday_adj = 1.1  # weekend more people
    special_adj = 1.2 if special else 1.0

    predicted = attendance * base_ratio * temp_adj * weekday_adj * special_adj
    # round to next integer serving
    return max(0, int(ceil(predicted)))

# Menu optimizer: simple low-waste sorting
def optimize_menu_logic(dishes_list):
    """
    dishes_list: list of dicts with keys: 'dish', 'served', 'waste'
    returns list of dish names with lowest waste ratio (top 5)
    """
    if not dishes_list:
        return []
    processed = []
    for d in dishes_list:
        served = d.get('served', 0) or 0
        waste = d.get('waste', 0) or 0
        ratio = (waste / served) if served else 0
        processed.append((d.get('dish','Unknown'), ratio))
    processed.sort(key=lambda x: x[1])
    return [p[0] for p in processed[:5]]
