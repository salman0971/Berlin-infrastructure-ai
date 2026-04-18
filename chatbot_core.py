import os
import sqlite3
import anthropic
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Initialize the LLM Client securely
api_key = os.environ.get("CLAUDE_API_KEY")
if not api_key:
    print("⚠️ WARNING: CLAUDE_API_KEY is missing!")

client = anthropic.Anthropic(api_key=api_key)

def get_schema_prompt():
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_year = datetime.now().strftime("%Y")
    
    return f"""
You are a SQLite expert. I have a database table named 'construction_sites'.

CRITICAL CONTEXT:
- Today's exact date is: {current_date}
- The current year is: {current_year}
Use this context to accurately evaluate phrases like "this year", "currently", "active", or "ending soon".

Here is the schema:
- id (TEXT)
- subtype (TEXT)
- severity (TEXT) -- DATA DICTIONARY (German values):
  * 'vollsperrung' = Full Closure (Critical Impact)
  * 'Fahrtrichtungssperrung' = Directional Closure (High Impact)
  * 'keine sperrung' = No Closure (Low/Info Impact)
  CRITICAL: If a user asks in English for "closures", "severe", or "full closures", you MUST translate their intent and write the SQL using the EXACT German terms above (e.g., WHERE severity = 'vollsperrung').
- direction (TEXT)
- street (TEXT)
- district (TEXT) -- Contains neighborhood names (e.g., Mitte, Steglitz)
- section (TEXT)
- content (TEXT)
- validity_from (TEXT) -- Format is YYYY-MM-DDTHH:MM
- validity_to (TEXT) -- Format is YYYY-MM-DDTHH:MM
- longitude (REAL)
- latitude (REAL)

Given a user's question, write a valid SQLite query to answer it. 
Return ONLY the raw SQL query. Do not include markdown formatting, backticks, or any explanation. Just the SQL string.
"""

def get_sql_from_llm(user_question):
    print("🧠 Asking Claude to translate your question into SQL...")
    
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=get_schema_prompt(), # <-- CALL THE NEW FUNCTION HERE
        messages=[
            {"role": "user", "content": user_question}
        ]
    )
    return response.content[0].text.strip()

# ... (Keep run_query_on_db exactly the same below this) ...

def run_query_on_db(sql_query):
    print(f"🖥️  Running SQL on local database: {sql_query}")
    
    conn = sqlite3.connect('berlin_infrastructure.db')
    # --- NEW: Tell SQLite to return labeled dictionaries, not raw lists ---
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql_query)
        # Convert the rows into standard JSON-friendly dictionaries
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    except Exception as e:
        conn.close()
        return f"Error running query: {e}"
# --- Let's test the pipeline! ---
if __name__ == "__main__":
    print("Welcome to the Berlin Construction Chatbot (Terminal Edition)\n")
    
    # 1. The Ask
    question = "How many total construction sites are in Mitte?"
    print(f"User: {question}")
    
    # 2. The Translation (English -> SQL)
    generated_sql = get_sql_from_llm(question)
    
    # 3. The Execution
    database_results = run_query_on_db(generated_sql)
    
    # 4. The Result
    print(f"\n📊 Final Data Result: {database_results}")