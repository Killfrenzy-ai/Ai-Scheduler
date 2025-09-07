# register_webhook.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
CALENDLY_API_KEY = os.getenv("CALENDLY_API_KEY")
ORG_UUID = "50cab1cc-36fa-47e8-af94-5627c5fea7e7"
 # get this via /users/me
WEBHOOK_URL = "https://58db76d1cd41.ngrok-free.app/webhook"     # set this to your ngrok https://xxxx.ngrok-free.app/webhook

headers = {
    "Authorization": f"Bearer {CALENDLY_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "url": WEBHOOK_URL,
    "events": ["invitee.created", "invitee.canceled"],
    "organization": f"https://api.calendly.com/organizations/{ORG_UUID}",
    "scope": "organization"
}

resp = requests.post("https://api.calendly.com/webhook_subscriptions",
                     headers=headers, json=payload)

print("🔗 Calendly response:", resp.status_code, resp.json())
if resp.status_code == 201:
    print("✅ Webhook registered successfully.")