import sqlite3
from datetime import datetime, timedelta

DB_PATH = "db/appointments.db"

def seed_schedules(num_days: int = 5, slots_per_day: int = 4):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Ensure doctor_schedules table exists
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

    # Clear old demo data
    cur.execute("DELETE FROM doctor_schedules")

    doctors = ["D001", "D002"]
    locations = ["Clinic A", "Clinic B"]

    start_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)

    for day in range(num_days):
        for doc in doctors:
            for slot in range(slots_per_day):
                start_time = start_date + timedelta(days=day, hours=slot)
                end_time = start_time + timedelta(minutes=30)
                cur.execute("""
                INSERT INTO doctor_schedules (doctor_id, clinic_location, start_dt, end_dt, status)
                VALUES (?, ?, ?, ?, 'free')
                """, (doc, locations[0 if doc == "D001" else 1], start_time.isoformat(), end_time.isoformat()))

    conn.commit()
    conn.close()
    print(f"✅ Seeded {num_days * slots_per_day * len(doctors)} slots into doctor_schedules.")

if __name__ == "__main__":
    seed_schedules()
