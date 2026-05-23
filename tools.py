import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("hotel.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preferences (
            user_id TEXT PRIMARY KEY,
            prefs TEXT
        )
    """)
    conn.commit()
    conn.close()

def load_preferences(user_id: str) -> str:
    conn = sqlite3.connect("hotel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT prefs FROM preferences WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "No historical preferences found."

def save_preferences(user_id: str, prefs: str):
    conn = sqlite3.connect("hotel.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO preferences (user_id, prefs)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET prefs = excluded.prefs
    """, (user_id, prefs))
    conn.commit()
    conn.close()

def check_room_availability(room_type: str, check_in_date: str, check_out_date: str) -> dict:
    """Checks if a room type is available for the given dates without any random fluctuating logic."""
    today = datetime.today().date()
    
    try:
        in_date = datetime.strptime(check_in_date, "%Y-%m-%d").date()
        out_date = datetime.strptime(check_out_date, "%Y-%m-%d").date()
    except ValueError:
        return {"status": "Error", "message": "Invalid date format. Please use YYYY-MM-DD."}

    
    if in_date < today or out_date < today:
        return {
            "status": "Error", 
            "message": f"Validation Failed: Booking dates cannot be in the past. Today's date is {today}. You provided check-in: {check_in_date}."
        }
        
    if out_date <= in_date:
        return {"status": "Error", "message": "Check-out date must be strictly after the check-in date."}

    
    if room_type.lower() == "suite" and "2026-06-01" <= check_in_date <= "2026-06-05":
        return {"status": "Fully Booked", "message": f"The {room_type} room type is fully booked from 2026-06-01 to 2026-06-05."}
        
    return {"status": "Available", "message": f"Great news! The {room_type} room is available for your requested dates."}