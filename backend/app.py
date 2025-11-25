from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import sqlite3, os
from models import train_or_load_predictor, predict_quantity, optimize_menu_logic
import requests

app = Flask(__name__)
CORS(app)

# === CONFIG ===
DB = os.path.join(os.path.dirname(__file__), 'db.sqlite')
WAQI_TOKEN = os.environ.get('WAQI_TOKEN', 'YOUR_WAQI_TOKEN')

@app.route('/predict_food', methods=['POST'])
def predict_food():
    data = request.get_json()
    if isinstance(data, list):
        sample = data[-1]
    else:
        sample = data
    att = float(sample.get('attendance', 100))
    temp = float(sample.get('temp', 25.0))
    wd = int(sample.get('weekday', 0))
    ev = int(sample.get('special_event', 0))
    qty = predict_quantity(attendance=att, temp=temp, weekday=wd, special=ev)
    return jsonify({'recommended_servings': round(qty, 1)})

@app.route('/optimize_menu', methods=['POST'])
def optimize_menu():
    data = request.get_json()
    df = pd.DataFrame(data)
    optimized = optimize_menu_logic(df)
    return jsonify({'optimized_menu': optimized})

@app.route('/log_waste', methods=['POST'])
def log_waste():
    payload = request.get_json()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''INSERT INTO waste_logs(date, dish, cooked, consumed, wasted) VALUES (?,?,?,?,?)''',
              (payload['date'], payload['dish'], payload['cooked'], payload['consumed'], payload['wasted']))
    conn.commit()
    conn.close()
    return jsonify({'status':'ok'})

@app.route('/get_summary', methods=['GET'])
def get_summary():
    conn = sqlite3.connect(DB)
    try:
        df = pd.read_sql('SELECT * FROM waste_logs', conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    if df.empty:
        return jsonify({'total_waste_kg':0, 'total_cooked_kg':0, 'waste_ratio':0})
    total_waste = df['wasted'].sum()
    total_cooked = df['cooked'].sum()
    return jsonify({'total_waste_kg': float(total_waste),
                    'total_cooked_kg': float(total_cooked),
                    'waste_ratio': float(total_waste/total_cooked) if total_cooked else 0})

@app.route('/aqi', methods=['GET'])
def aqi():
    city = request.args.get('city')
    lat = request.args.get('lat'); lon = request.args.get('lon')
    token = WAQI_TOKEN
    if token == 'YOUR_WAQI_TOKEN':
        return jsonify({'error':'WAQI_TOKEN not configured. Set WAQI_TOKEN environment variable on Render.'}), 400
    if city:
        url = f'https://api.waqi.info/feed/{city}/?token={token}'
    elif lat and lon:
        url = f'https://api.waqi.info/feed/geo:{lat};{lon}/?token={token}'
    else:
        return jsonify({'error':'Provide city or lat & lon'}), 400
    r = requests.get(url, timeout=8)
    if r.status_code != 200:
        return jsonify({'error':'Failed to fetch from WAQI','status_code':r.status_code}), 502
    data = r.json()
    return jsonify(data)

if __name__ == '__main__':
    train_or_load_predictor()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
