import sqlite3
import json

def init_db():
    """Initialize SQLite database for simulations."""
    try:
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
        c.execute('''
        CREATE TABLE IF NOT EXISTS personas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            persona JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
    except Exception as e:
        print(f"Database Initialization Error: {str(e)}")
    finally:
        conn.close()

def save_simulation(dilemma, process_hint, extracted, personas, transcript, summary, keywords, suggestion):
    """Save simulation data to the database."""
    try:
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
    except Exception as e:
        print(f"Simulation Save Error: {str(e)}")
    finally:
        conn.close()

def save_persona(persona):
    """Save a single persona to the database."""
    try:
        conn = sqlite3.connect("decisionforge.db")
        c = conn.cursor()
        c.execute('''
        INSERT INTO personas (persona) VALUES (?)
        ''', (json.dumps(persona),))
        conn.commit()
    except Exception as e:
        print(f"Persona Save Error: {str(e)}")
    finally:
        conn.close()

def get_all_personas():
    """Retrieve all saved personas from the database."""
    try:
        conn = sqlite3.connect("decisionforge.db")
        c = conn.cursor()
        c.execute("SELECT persona FROM personas WHERE persona IS NOT NULL")
        rows = c.fetchall()
        personas = []
        for row in rows:
            try:
                persona = json.loads(row[0])
                personas.append(persona)
            except json.JSONDecodeError:
                continue
        return personas
    except Exception as e:
        print(f"Get Personas Error: {str(e)}")
        return []
    finally:
        conn.close()
