import sqlite3


def setup_appointments_db():
    conn = sqlite3.connect("appointments.db")
    c = conn.cursor()

    # Create or update appointments table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            patient_email TEXT,
            patient_phone TEXT,
            dob TEXT,
            doctor TEXT,
            location TEXT,
            insurance_carrier TEXT,
            insurance_member_id TEXT,
            insurance_group TEXT,
            start_time TEXT,
            end_time TEXT,
            duration_minutes INTEGER,
            booking_url TEXT,
            status TEXT DEFAULT 'confirmed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()
    print("✅ appointments.db is set up with extended schema")


if __name__ == "__main__":
    setup_appointments_db()
