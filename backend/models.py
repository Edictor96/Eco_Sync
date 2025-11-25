import pandas as pd
import sqlite3, os
from sklearn.ensemble import RandomForestRegressor
import joblib

MODEL_FILE='food_predictor.joblib'
DB=os.path.join(os.path.dirname(__file__), 'db.sqlite')

def train_or_load_predictor():
    if os.path.exists(os.path.join(os.path.dirname(__file__), MODEL_FILE)):
        return joblib.load(os.path.join(os.path.dirname(__file__), MODEL_FILE))
    conn = sqlite3.connect(DB)
    try:
        df = pd.read_sql('SELECT * FROM attendance_records', conn)
    except Exception:
        df = pd.DataFrame({'attendance':[100,120,80,150],'temp':[28,30,25,27],'weekday':[1,2,3,4],'special':[0,1,0,0],'servings':[100,120,80,150]})
    conn.close()
    X = df[['attendance','temp','weekday','special']]
    y = df['servings']
    model = RandomForestRegressor(n_estimators=50, random_state=42).fit(X,y)
    joblib.dump(model, os.path.join(os.path.dirname(__file__), MODEL_FILE))
    return model

def predict_quantity(attendance, temp, weekday, special):
    model = train_or_load_predictor()
    X = [[attendance, temp, weekday, special]]
    pred = model.predict(X)[0]
    return max(0, round(pred * 1.02))

def optimize_menu_logic(df):
    df = df.copy()
    if 'served' not in df.columns or 'waste' not in df.columns:
        return []
    df['waste_ratio'] = df['waste'] / (df['served'] + 1e-6)
    best = df.sort_values('waste_ratio').head(5)
    return best['dish'].tolist()
