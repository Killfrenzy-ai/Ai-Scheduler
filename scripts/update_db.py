import sqlite3

DB_PATH = "db/patients.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Get existing columns
    cur.execute("PRAGMA table_info(patients)")
    columns = [row[1] for row in cur.fetchall()]

    # Add insurance columns if missing
    if "insurance_carrier" not in columns:
        cur.execute("ALTER TABLE patients ADD COLUMN insurance_carrier TEXT")
        print("✅ Added 'insurance_carrier'")
    else:
        print("ℹ️ 'insurance_carrier' already exists")

    if "insurance_member_id" not in columns:
        cur.execute("ALTER TABLE patients ADD COLUMN insurance_member_id TEXT")
        print("✅ Added 'insurance_member_id'")
    else:
        print("ℹ️ 'insurance_member_id' already exists")

    if "insurance_group" not in columns:
        cur.execute("ALTER TABLE patients ADD COLUMN insurance_group TEXT")
        print("✅ Added 'insurance_group'")
    else:
        print("ℹ️ 'insurance_group' already exists")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
