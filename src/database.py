# src/database.py
import sqlite3
import logging
from src.config import DATABASE_PATH

logger = logging.getLogger(__name__)

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS scenarios (
                            id INTEGER PRIMARY KEY,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                            summary TEXT,
                            recommendation TEXT,
                            agent_inputs TEXT
                        )''')
            conn.commit()
        logger.info(f"Database initialized successfully at {DATABASE_PATH}")
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}", exc_info=True)
        raise

def store_scenario(summary: str, recommendation: str, agent_inputs: str):
    """Stores a new scenario in the database."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO scenarios (summary, recommendation, agent_inputs) VALUES (?, ?, ?)",
                      (summary, recommendation, agent_inputs))
            conn.commit()
        logger.info("New scenario stored in the database.")
    except sqlite3.Error as e:
        logger.error(f"Error storing scenario in DB: {e}", exc_info=True)
        # Optionally, re-raise or handle gracefully
