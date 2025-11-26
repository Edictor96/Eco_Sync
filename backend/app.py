# backend/app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import os, sqlite3
from models import seed_demo, predict_quantity, optimize_menu_logic

app = Flask(__name__)
CORS(app)

# Ensure demo DB exists when server starts
seed_demo()

DB = os.path.join(os.path.dirname(__file__), 'db.sqlite')

@app.route('/predict_food', methods=['POST'])
def predict_food():
    data = request.get_json() or {}
    att = int(data.get('attendance', 100))
    temp = float(data.get('temp', 25.0))
    wd = int(data.get('weekday', 0))
    special = int(data.get('special_event', 0))
    qty = predict_quantity(attendance=att, temp=temp, weekday=wd, special=special)
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
    cooked = float(payload.get('cooked', 0))
    consumed = float(payload.get('consumed', 0))
    wasted = float(payload.get('wasted', 0))
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('INSERT INTO waste_logs(date,dish,cooked,consumed,wasted) VALUES (?,?,?,?,?)',
              (date, dish, cooked, consumed, wasted))
    conn.commit()
    conn.close()
    return jsonify({'status':'ok'})

@app.route('/get_summary', methods=['GET'])
def get_summary():
    conn = sqlite3.connect(DB)
    try:
        df = conn.execute('SELECT cooked, consumed, wasted FROM waste_logs').fetchall()
    except Exception:
        df = []
    conn.close()
    total_cooked = sum([r[0] for r in df]) if df else 0
    total_wasted = sum([r[2] for r in df]) if df else 0
    ratio = (total_wasted / total_cooked) if total_cooked else 0
    return jsonify({'total_waste_kg': total_wasted, 'total_cooked_kg': total_cooked, 'waste_ratio': ratio})

# AQI proxy - requires WAQI_TOKEN env var
import requests
WAQI_TOKEN = os.environ.get('WAQI_TOKEN', 'YOUR_WAQI_TOKEN')
@app.route('/aqi', methods=['GET'])
def aqi():
    city = request.args.get('city')
    lat = request.args.get('lat'); lon = request.args.get('lon')
    token = WAQI_TOKEN
    if token == 'YOUR_WAQI_TOKEN':
        return jsonify({'error':'WAQI_TOKEN not set'}), 400
    if city:
        url = f'https://api.waqi.info/feed/{city}/?token={token}'
    elif lat and lon:
        url = f'https://api.waqi.info/feed/geo:{lat};{lon}/?token={token}'
    else:
        return jsonify({'error':'Provide city or lat/lon'}), 400
    r = requests.get(url, timeout=8)
    return jsonify(r.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)))
