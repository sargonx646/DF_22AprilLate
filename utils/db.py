import sqlite3
import json

def init_db():
    """Initialize SQLite database for storing simulation data."""
    conn = sqlite3.connect("decisionforge.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS simulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dilemma TEXT,
            process_hint TEXT,
            extracted TEXT,
            personas TEXT,
            transcript TEXT,
            summary TEXT,
            keywords TEXT,
            suggestion TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_simulation(dilemma, process_hint, extracted, personas, transcript, summary, keywords, suggestion):
    """Save simulation data to SQLite database.

    Args:
        dilemma (str): User-defined dilemma.
        process_hint (str): Process or stakeholder details.
        extracted (dict): Extracted structure.
        personas (list[dict]): Generated personas.
        transcript (list[dict]): Debate transcript.
        summary (str): Debate summary.
        keywords (list[str]): Extracted keywords.
        suggestion (str): Optimization suggestion.
    """
    conn = sqlite3.connect("decisionforge.db")
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO simulations (dilemma, process_hint, extracted, personas, transcript, summary, keywords, suggestion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            dilemma,
            process_hint,
            json.dumps(extracted),
            json.dumps(personas),
            json.dumps(transcript),
            summary,
            json.dumps(keywords),
            suggestion
        )
    )
    conn.commit()
    conn.close()
