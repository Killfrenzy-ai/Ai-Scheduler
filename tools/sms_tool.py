import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class SMSTool:
    def __init__(self, use_twilio: bool = False):
        self.use_twilio = use_twilio
        if use_twilio:
            try:
                from twilio.rest import Client
                self.twilio_client = Client(
                    os.getenv("TWILIO_SID"),
                    os.getenv("TWILIO_AUTH_TOKEN")
                )
                self.from_number = os.getenv("TWILIO_PHONE_NUMBER")
                if not self.from_number:
                    raise ValueError("❌ Missing TWILIO_PHONE_NUMBER in .env")
            except ImportError:
                raise ImportError("Install twilio with `pip install twilio` to use SMS")

    def send_sms(self, to_number: str, message: str):
        """
        Send SMS via Twilio (if enabled) or simulate by printing/logging.
        """
        if self.use_twilio:
            msg = self.twilio_client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            print(f"✅ SMS sent via Twilio to {to_number}: SID={msg.sid}")
            return {"status": "sent", "sid": msg.sid}

        # --- Simulation mode ---
        log_entry = f"[{datetime.now().isoformat()}] To: {to_number} | Msg: {message}\n"
        print("📱 Simulated SMS:", log_entry.strip())
        with open("sms_log.txt", "a") as f:
            f.write(log_entry)
        return {"status": "simulated", "to": to_number, "message": message}
