# AI Scheduler MVP

## 📌 Overview
This project implements an AI-powered medical appointment scheduling agent.  
It automates:
- Patient intake (via chatbot in Streamlit powered by Ollama)
- Patient lookup in SQLite (patients.db)
- Appointment booking (Calendly API + SQLite fallback)
- Insurance capture (carrier, member ID, group)
- Email + SMS confirmations
- Automated reminders (3-stage)
- Webhook integration for real-time updates

The system is designed to reduce no-shows, improve insurance collection, and streamline clinic operations.

---

## 🚀 How to Run Locally
### 1. Clone Repository
```bash
git clone https://github.com/killfrenzy-ai/ai-scheduler.git
cd ai-scheduler

### 2. Create Virtual Environment & Install Dependencies
```bash
python -m venv venv
source venv/bin/activate   # on macOS/Linux
venv\Scripts\activate    # on Windows

pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the root directory:

```
# Calendly API
CALENDLY_API_KEY=your_calendly_api_key

# SMTP for EmailTool
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_smtp_password
FROM_EMAIL=your_email@gmail.com

# Twilio for SMSTool (optional)
TWILIO_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth
TWILIO_FROM=+1234567890
```

### 4. Initialize Databases
```bash
python scripts/setup_db.py
```

### 5. Run Streamlit Frontend
```bash
streamlit run app.py
```

### 6. Run Calendly Webhook Listener (FastAPI)
```bash
uvicorn webhook_server:app --reload --port 8000
```

Expose via ngrok:
```bash
ngrok http 8000
```

Register the webhook with:
```bash
python scripts/register_webhook.py
```

---

## 🛠 Tech Stack
- **LangGraph + LangChain** for workflow orchestration
- **Ollama (LLaMA 3)** for chatbot intake
- **SQLite (patients.db, appointments.db)** for persistence
- **Calendly API** for scheduling
- **SMTP (Gmail/Outlook/Mailtrap)** for email
- **Twilio (or mock)** for SMS
- **Streamlit** for UI
- **FastAPI + ngrok** for webhook handling

---

## ✅ Features
- Differentiates between **new (60 min)** and **returning (30 min)** patients
- Captures **insurance details** and doctor info
- Sends **email & SMS confirmations**
- Automates **reminders with action checks**
- **Webhook integration** for appointment lifecycle updates

---

## 📂 Project Structure
```
ai-scheduler/
│── app.py                  # Streamlit chatbot interface
│── scheduler_graph.py      # Agent workflow with LangGraph
│── tools/                  # Tools for email, sms, calendar, patient lookup
│── scripts/                # Setup and utility scripts
│── db/                     # SQLite databases (patients.db, appointments.db)
│── tests/                  # Unit tests
│── requirements.txt
│── README.md
│── technical_approach.txt
```
