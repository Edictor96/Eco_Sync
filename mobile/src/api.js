// mobile/src/api.js
import axios from 'axios';
// Replace with your Render URL after deploy, e.g. https://ecosync-backend.onrender.com
const BASE = 'https://<YOUR_RENDER_BACKEND_URL>';

export async function getPrediction(payload){
  const res = await axios.post(`${BASE}/predict_food`, payload);
  return res.data;
}
export async function getAQIByCity(city){
  const res = await axios.get(`${BASE}/aqi`, { params: { city }});
  return res.data;
}
export async function postWasteLog(payload){
  const res = await axios.post(`${BASE}/log_waste`, payload);
  return res.data;
}
export async function getSummary(){
  const res = await axios.get(`${BASE}/get_summary`);
  return res.data;
}
export async function optimizeMenu(list){
  const res = await axios.post(`${BASE}/optimize_menu`, list);
  return res.data;
}
