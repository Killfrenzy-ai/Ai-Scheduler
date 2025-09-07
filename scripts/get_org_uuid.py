import os
import requests
from dotenv import load_dotenv

load_dotenv()
CALENDLY_API_KEY = os.getenv("CALENDLY_API_KEY")

headers = {"Authorization": f"Bearer {CALENDLY_API_KEY}"}

resp = requests.get("https://api.calendly.com/users/me", headers=headers)
data = resp.json()

print("🔗 Full response:", data)

org_url = data["resource"]["organization"]
org_uuid = org_url.split("/")[-1]

print("✅ Your Organization UUID:", org_uuid)