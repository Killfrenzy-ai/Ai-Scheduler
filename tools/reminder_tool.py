import sqlite3
from datetime import datetime, timedelta
from tools.email_tool import EmailTool
from tools.sms_tool import SMSTool

DB_PATH = "db/appointments.db"

class ReminderTool:
    def __init__(self, use_twilio: bool = False):
        self.email_tool = EmailTool()
        self.sms_tool = SMSTool(use_twilio=use_twilio)

    def get_upcoming_appointments(self, within_hours: int = 48):
        """
        Fetch appointments scheduled within the next `within_hours`.
        """
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cutoff = (datetime.utcnow() + timedelta(hours=within_hours)).isoformat()

        cur.execute("""
        SELECT id, patient_name, email, start_time
        FROM appointments
        WHERE start_time IS NOT NULL AND start_time < ?
        """, (cutoff,))
        rows = cur.fetchall()
        conn.close()

        return [
            {"id": r[0], "patient_name": r[1], "email": r[2], "start_time": r[3]}
            for r in rows
        ]

    def send_reminder(self, appointment: dict, stage: int = 1):
        """
        Send a reminder for an appointment.
        stage 1 → normal reminder
        stage 2 → check if forms are filled
        stage 3 → confirm attendance / ask cancellation reason
        """
        name = appointment["patient_name"]
        email = appointment["email"]
        start_time = appointment["start_time"]

        if stage == 1:
            subject = f"Reminder: Appointment on {start_time}"
            body = f"Hello {name}, this is a reminder for your upcoming appointment on {start_time}."
            sms = f"Reminder: Your appointment is on {start_time}."
        elif stage == 2:
            subject = f"Action Needed: Forms for your appointment on {start_time}"
            body = (
                f"Hello {name}, please complete your intake forms before your appointment on {start_time}. "
                f"Click here to access your forms: [link]"
            )
            sms = f"Reminder: Please complete your intake forms before {start_time}."
        elif stage == 3:
            subject = f"Confirm Your Appointment on {start_time}"
            body = (
                f"Hello {name}, please confirm if you will attend your appointment on {start_time}. "
                f"If not, reply with the reason for cancellation."
            )
            sms = f"Confirm your appointment on {start_time}. Reply YES to confirm or NO to cancel."

        else:
            raise ValueError("Stage must be 1, 2, or 3.")

        # Send email
        self.email_tool.send_email(to_email=email, subject=subject, body=body)

        # Send SMS
        self.sms_tool.send_sms(to_number="+911234567890", message=sms)  # Replace with real phone if in DB

        print(f"✅ Reminder (stage {stage}) sent to {name} at {email}.")

    def run_reminders(self):
        """
        Run all reminders (for demo: sends all 3 sequentially).
        In production, you'd schedule them at different intervals.
        """
        appointments = self.get_upcoming_appointments(within_hours=48)
        for appt in appointments:
            for stage in [1, 2, 3]:
                self.send_reminder(appt, stage=stage)
