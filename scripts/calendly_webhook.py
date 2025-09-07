import sqlite3
from fastapi import FastAPI, Request
import uvicorn

DB_PATH = "db/appointments.db"

app = FastAPI()

def save_booking(payload: dict):
    """Save confirmed booking into appointments.db"""
    invitee = payload.get("payload", {}).get("invitee", {})
    event = payload.get("payload", {}).get("event", {})

    if not invitee or not event:
        print("⚠️ Invalid payload, skipping")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO appointments (
            patient_name, patient_email, start_dt, end_dt, doctor_id,
            clinic_location, type, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        invitee.get("name"),
        invitee.get("email"),
        event.get("start_time"),
        event.get("end_time"),
        "unknown",  # can map later if needed
        "unknown",
        "Calendly",
        "confirmed"
    ))

    conn.commit()
    conn.close()
    print(f"✅ Booking saved for {invitee.get('name')} at {event.get('start_time')}")

def cancel_booking(payload: dict):
    """Mark appointment as canceled in appointments.db"""
    invitee = payload.get("payload", {}).get("invitee", {})
    if not invitee:
        return

    email = invitee.get("email")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        UPDATE appointments
        SET status = 'canceled'
        WHERE patient_email = ?
    """, (email,))
    conn.commit()
    conn.close()
    print(f"❌ Booking canceled for {email}")
@app.post("/webhooks/calendly")
async def calendly_webhook(request: Request):
    data = await request.json()
    print("📩 Received webhook:", data)

    event_type = data.get("event")
    if event_type == "invitee.created":
        save_booking(data)
    elif event_type == "invitee.canceled":
        cancel_booking(data)

    return {"status": "ok"}
@app.get("/webhooks/calendly")
async def webhook_check():
    return {"status": "listening"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
