# **EcoSync — Smart Campus Sustainability Platform**

EcoSync is a lightweight, modular system designed to help college campuses reduce food waste, energy use, and environmental impact.  
The project includes:

- A **Python (Flask)** backend that handles computation and data flow.
- A **React Native (Expo)** mobile client with a clean, responsive UI.
- Endpoints for food prediction, waste logging, menu optimization, and AQI data retrieval.

This repository serves as a functional MVP that can be deployed quickly and demonstrated easily.

---

## **📁 Project Structure**

```
EcoSync/
│
├── backend/           # Flask API (Render-ready)
│   ├── app.py
│   ├── models.py
│   ├── seed_data.py
│   ├── requirements.txt
│   ├── Procfile
│   └── db.sqlite
│
└── mobile/            # React Native (Expo) client
    ├── App.js
    ├── app.json
    ├── package.json
    └── src/
        ├── api.js
        ├── screens/
        └── components/
```

---

## **✨ Features**

### **Smart Mess Management**
- Predicts recommended servings using attendance-based estimation.
- Tracks cooked, consumed, and wasted quantities.
- Flags high-waste dishes for optimization.

### **Leftover Redistribution**
- Mess staff can log surplus food.
- NGOs/volunteers can claim available food in real time.

### **Power & Environment Awareness**
- Summary dashboard of total waste, consumption, and ratios.
- AQI data via WAQI API.

### **Mobile App**
- Built with Expo for browser + mobile use.
- No installation required (can run via Expo Snack).

---

## **🚀 Backend Deployment (Render)**

The backend is fully configured to deploy on **Render**.

### **Steps**
1. Push the **backend/** folder into a GitHub repository.
2. On Render:
   - *New → Web Service*
   - Connect GitHub repo
   - **Root Directory:** `backend`
   - **Build Command:**
     ```
     pip install -r requirements.txt
     ```
   - **Start Command:**
     ```
     gunicorn app:app -b 0.0.0.0:$PORT
     ```

3. Add environment variable:
```
WAQI_TOKEN = <your_token>
```

Get your free WAQI token here: https://aqicn.org/api/

4. Deploy. Render provides a URL such as:
```
https://ecosync-backend.onrender.com
```

---

## **📊 Seeding Demo Data**
To preload sample values:

```
python seed_data.py
```

This generates `db.sqlite` with sample attendance and waste logs.  
You may commit the database file if you want remote deployments to include sample data.

---

## **📱 Mobile App (Expo)**

### **Configure API URL**
Edit `mobile/src/api.js`:

```js
const BASE = "https://<your-render-backend-url>";
```

### **Run in Browser using Expo Snack**
1. Go to https://snack.expo.dev  
2. Create a new project.  
3. Copy all files from `/mobile/` into Snack.  
4. The preview loads instantly.  
5. Optionally scan QR to open on your phone.

### **Local run (optional)**
```
npm install
expo start
```

---

## **🔌 API Endpoints**

| Endpoint | Method | Description |
|---------|--------|-------------|
| `/predict_food` | POST | Returns recommended servings |
| `/optimize_menu` | POST | Suggests low-waste dishes |
| `/log_waste` | POST | Logs cooked/consumed/wasted food |
| `/get_summary` | GET | Returns consumption & waste stats |
| `/aqi` | GET | AQI data for city or coordinates |

### **Example Request**
```json
POST /predict_food
{
  "attendance": 120,
  "temp": 28,
  "weekday": 2,
  "special_event": 0
}
```

### **Example Response**
```json
{
  "recommended_servings": 127
}
```

---

## **🔮 Future Enhancements**
- PostgreSQL integration (Render Managed Database)
- Authentication (JWT)
- Real ML model training
- IoT sensor integration for smart mess & energy data

---

## **📄 License**
This project is intended for academic and demonstration use.  
Feel free to modify and adapt as needed.

---

## **👤 Maintainer**
**EcoSync MVP Template**  
Created for campus sustainability and technology projects.
