# backend/app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import os, sqlite3, requests

from models import seed_demo, predict_quantity, optimize_menu_logic, ensure_db

app = Flask(__name__)
CORS(app)

DB = os.path.join(os.path.dirname(__file__), 'db.sqlite')

# Ensure DB & seed on startup
seed_demo()

@app.route('/predict_food', methods=['POST'])
def predict_food():
    data = request.get_json() or {}
    att = int(data.get('attendance', 100))
    temp = float(data.get('temp', 25.0))
    wd = int(data.get('weekday', 0))
    special = int(data.get('special_event', 0))

    qty = predict_quantity(attendance=att, temp=temp, weekday=wd, special=special)

    # Log this prediction into attendance history so system "learns" over time
    ensure_db()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO attendance_records(attendance,temp,weekday,special,servings) "
        "VALUES (?,?,?,?,?)",
        (att, temp, wd, special, qty)
    )
    conn.commit()
    conn.close()

    return jsonify({'recommended_servings': qty})

@app.route('/optimize_menu', methods=['POST'])
def optimize_menu():
    data = request.get_json() or []
    optimized = optimize_menu_logic(data)
    return jsonify({'optimized_menu': optimized})

@app.route('/log_waste', methods=['POST'])
def log_waste():
    payload = request.get_json() or {}
    date = payload.get('date')
    dish = payload.get('dish', 'Unknown')
    cooked = float(payload.get('cooked', 0) or 0)
    consumed = float(payload.get('consumed', 0) or 0)
    wasted = float(payload.get('wasted', 0) or 0)

    ensure_db()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO waste_logs(date,dish,cooked,consumed,wasted) VALUES (?,?,?,?,?)",
        (date, dish, cooked, consumed, wasted)
    )
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/get_summary', methods=['GET'])
def get_summary():
    ensure_db()
    conn = sqlite3.connect(DB)
    try:
        rows = conn.execute(
            "SELECT cooked, consumed, wasted FROM waste_logs"
        ).fetchall()
    except Exception:
        rows = []
    conn.close()

    total_cooked = sum(r[0] for r in rows) if rows else 0
    total_wasted = sum(r[2] for r in rows) if rows else 0
    ratio = (total_wasted / total_cooked) if total_cooked else 0

    return jsonify({
        'total_waste_kg': total_wasted,
        'total_cooked_kg': total_cooked,
        'waste_ratio': ratio
    })

# AQI proxy via WAQI
WAQI_TOKEN = os.environ.get('WAQI_TOKEN', 'YOUR_WAQI_TOKEN')

@app.route('/aqi', methods=['GET'])
def aqi():
    city = request.args.get('city')
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    token = WAQI_TOKEN

    if token == 'YOUR_WAQI_TOKEN':
        return jsonify({'error': 'WAQI_TOKEN not set on server'}), 400

    if city:
        url = f'https://api.waqi.info/feed/{city}/?token={token}'
    elif lat and lon:
        url = f'https://api.waqi.info/feed/geo:{lat};{lon}/?token={token}'
    else:
        return jsonify({'error': 'Provide city or lat/lon'}), 400

    r = requests.get(url, timeout=8)
    return jsonify(r.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
