import sqlite3
import json

def init_db():
    """Initialize SQLite database for simulations."""
    conn = sqlite3.connect("decisionforge.db")
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS simulations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dilemma TEXT,
        process_hint TEXT,
        extracted JSON,
        personas JSON,
        transcript JSON,
        summary TEXT,
        keywords JSON,
        suggestion TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

def save_simulation(dilemma, process_hint, extracted, personas, transcript, summary, keywords, suggestion):
    """Save simulation data to the database."""
    conn = sqlite3.connect("decisionforge.db")
    c = conn.cursor()
    c.execute('''
    INSERT INTO simulations (dilemma, process_hint, extracted, personas, transcript, summary, keywords, suggestion)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        dilemma,
        process_hint,
        json.dumps(extracted),
        json.dumps(personas),
        json.dumps(transcript),
        summary,
        json.dumps(keywords),
        suggestion
    ))
    conn.commit()
    conn.close()

def get_all_personas():
    """Retrieve all saved personas from the database."""
    conn = sqlite3.connect("decisionforge.db")
    c = conn.cursor()
    c.execute("SELECT personas FROM simulations WHERE personas IS NOT NULL")
    rows = c.fetchall()
    personas = []
    for row in rows:
        try:
            persona_list = json.loads(row[0])
            personas.extend(persona_list)
        except json.JSONDecodeError:
            continue
    conn.close()
    return personas
