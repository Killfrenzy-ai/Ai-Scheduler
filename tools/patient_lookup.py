# tools/patient_lookup.py
from typing import Optional
import sqlite3
from datetime import datetime, timedelta

DB_PATH = "db/patients.db"

def lookup_patient(name: str = "", dob: str = "", mrn: Optional[str] = None) -> dict:
    """
    Lookup patient in patients.db.
    Provide either `mrn` or both `name` and `dob`.
    Returns a dict with 'found' (bool), patient fields if found, and classification.
    """
    if not mrn and (not name or not dob):
        raise ValueError("Provide either mrn or both name and dob")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if mrn:
        cur.execute("SELECT * FROM patients WHERE mrn = ?", (mrn,))
    else:
        cur.execute("SELECT * FROM patients WHERE name = ? AND dob = ?", (name, dob))

    row = cur.fetchone()
    conn.close()

    if not row:
        return {
            "found": False,
            "classification": "new",
            "reason": "Not found in DB – treat as new patient"
        }

    # Row schema with id first:
    # (id, mrn, name, dob, email, phone, insurance_carrier, insurance_member_id,
    #  insurance_group, doctor, preferred_location, last_visit_dt)
    (
        _id,
        mrn_val,
        pname,
        pdob,
        email,
        phone,
        insurance_carrier,
        insurance_member_id,
        insurance_group,
        doctor,
        location,
        last_visit,
    ) = row

    classification = "new"
    reason = "No visit record"

    if last_visit:  # guard against NULL
        try:
            last_visit_dt = datetime.strptime(last_visit, "%Y-%m-%d").date()
            cutoff = datetime.now().date() - timedelta(days=730)  # 24 months
            if last_visit_dt >= cutoff:
                classification = "returning"
                reason = "Visited within last 24 months"
            else:
                classification = "new"
                reason = "Last visit more than 24 months ago"
        except Exception as e:
            reason = f"Invalid last_visit format: {e}"

    return {
        "found": True,
        "mrn": mrn_val,
        "name": pname,
        "dob": pdob,
        "email": email,
        "phone": phone,
        "insurance_carrier": insurance_carrier,
        "insurance_member_id": insurance_member_id,
        "insurance_group": insurance_group,
        "doctor": doctor or "General Physician",
        "preferred_location": location,
        "last_visit": last_visit,
        "classification": classification,
        "reason": reason,
    }
