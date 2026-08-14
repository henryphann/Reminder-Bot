import sqlite3
from datetime import datetime

DB_NAME = "reminders.db"

def init_db():
    """Initializes the SQLite database and creates the reminders table if it doesn't exist."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                reminder_text TEXT NOT NULL,
                remind_at TEXT NOT NULL
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
    finally:
        conn.close()

def add_reminder(user_id: int, channel_id: int, reminder_text: str, remind_at: str):
    """Adds a new reminder and its originating channel ID to the database."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reminders (user_id, channel_id, reminder_text, remind_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, channel_id, reminder_text, remind_at))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error adding reminder: {e}")
        raise
    finally:
        conn.close()

def get_pending_reminders():
    """Fetches all reminders that are due."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute("SELECT id, user_id, channel_id, reminder_text, remind_at FROM reminders WHERE remind_at <= ?", (now,))
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"Error fetching reminders: {e}")
        return []
    finally:
        conn.close()

def delete_reminder(reminder_id: int):
    """Deletes a reminder after it has been sent."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error deleting reminder: {e}")
    finally:
        conn.close()
