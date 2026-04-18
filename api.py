from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chatbot_core
import sqlite3

app = FastAPI(title="Berlin Construction AI")

# CORS Middleware (The bug fix we just did!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

# --- NEW: THE MAP DATA ENDPOINT ---
@app.get("/locations")
def get_map_locations():
    conn = sqlite3.connect('berlin_infrastructure.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT street, district, severity, latitude, longitude 
        FROM construction_sites 
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    locations = []
    for row in rows:
        locations.append({
            "street": row[0],
            "district": row[1],
            "severity": row[2],
            "lat": row[3],
            "lng": row[4]
        })
    return locations

# --- EXISTING CHATBOT ENDPOINT ---
@app.post("/ask")
def ask_chatbot(request: QuestionRequest):
    generated_sql = chatbot_core.get_sql_from_llm(request.question)
    results = chatbot_core.run_query_on_db(generated_sql)
    return {
        "question": request.question,
        "executed_sql": generated_sql,
        "answer": results
    }

# --- EXISTING FRONTEND ROUTE ---
@app.get("/")
def serve_frontend():
    with open("index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)