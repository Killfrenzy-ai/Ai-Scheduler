import os
import sqlite3
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()


CALENDLY_API_KEY = os.getenv("CALENDLY_API_KEY")
CALENDLY_BASE_URL = "https://api.calendly.com"
DB_PATH = "db/appointments.db"


class CalendarTool:
    def __init__(self, api_key: str | None = None, use_fallback: bool = False):
        self.api_key = api_key or CALENDLY_API_KEY
        self.use_fallback = use_fallback or not bool(self.api_key)

        if not self.use_fallback:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

    # -----------------------------
    # REAL CALENDLY API MODE
    # -----------------------------
    def get_user_uri(self):
        url = f"{CALENDLY_BASE_URL}/users/me"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()["resource"]["uri"]

    def list_event_types(self):
        user_uri = self.get_user_uri()  # fetch user first
        url = f"{CALENDLY_BASE_URL}/event_types"
        params = {"user": user_uri}
        resp = requests.get(url, headers=self.headers, params=params)
        resp.raise_for_status()
        return resp.json()["collection"]

    def create_scheduling_link(self, event_type_uri: str):
        """Create a booking link for a given event type."""
        url = f"{CALENDLY_BASE_URL}/scheduling_links"
        payload = {
            "max_event_count": 1,
            "owner": event_type_uri,   # full URI
            "owner_type": "EventType"  # must be included
        }
        print("Payload being sent:", payload)
        resp = requests.post(url, headers=self.headers, json=payload)
        resp.raise_for_status()
        return resp.json()["resource"]["booking_url"]

    def get_available_slots_calendly(self, event_type_uri: str, **kwargs):
        """
        Instead of deprecated available_times, return a booking link.
        Patients can click the link to see real slots.
        """
        return {"booking_url": self.create_scheduling_link(event_type_uri)}

    def book_slot_calendly(self, event_type_uri: str, invitee: dict):
        """
        For simplicity, booking is handled by Calendly via the scheduling link.
        This just returns the booking URL.
        """
        return {"booking_url": self.create_scheduling_link(event_type_uri)}
    # -----------------------------
    # SQLITE FALLBACK MODE
    # -----------------------------
    def init_fallback_db(self):
        """Initialize local doctor_schedules table if missing."""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS doctor_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id TEXT,
            clinic_location TEXT,
            start_dt DATETIME,
            end_dt DATETIME,
            status TEXT CHECK(status IN ('free','booked')) DEFAULT 'free'
        )
        """)
        conn.commit()
        conn.close()

    def get_available_slots_fallback(self, days_ahead: int = 7, limit: int = 5):
        """Return free slots from local SQLite fallback."""
        self.init_fallback_db()
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cutoff = (datetime.now() + timedelta(days=days_ahead)).isoformat()
        cur.execute("""
        SELECT id, doctor_id, clinic_location, start_dt, end_dt
        FROM doctor_schedules
        WHERE status='free' AND start_dt < ?
        LIMIT ?
        """, (cutoff, limit))
        rows = cur.fetchall()
        conn.close()

        slots = [
            {"id": r[0], "doctor_id": r[1], "location": r[2], "start": r[3], "end": r[4]}
            for r in rows
        ]
        return slots

    def book_slot_fallback(self, slot_id: int, patient_mrn: str):
        """Mark slot as booked in local DB."""
        self.init_fallback_db()
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
        UPDATE doctor_schedules
        SET status='booked'
        WHERE id=? AND status='free'
        """, (slot_id,))
        conn.commit()
        success = cur.rowcount > 0
        conn.close()
        return success

    # -----------------------------
    # Unified API
    # -----------------------------
    def get_available_slots(self, *args, **kwargs):
        if self.use_fallback:
            return self.get_available_slots_fallback(*args, **kwargs)
        return self.get_available_slots_calendly(*args, **kwargs)

    def book_slot(self, *args, **kwargs):
        if self.use_fallback:
            return self.book_slot_fallback(*args, **kwargs)
        return self.book_slot_calendly(*args, **kwargs)
