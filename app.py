import streamlit as st
import json
from scheduler_graph import parse_patient_request, create_scheduler_graph

st.set_page_config(page_title="AI Scheduler", page_icon="🩺", layout="centered")

# ---- Greeting Message ----
st.title("🤖 Patient Appointment Scheduler")
st.markdown(
    """
    👋 **Welcome to our AI-powered appointment assistant!**

    Please describe your request in plain English.  
    For example:  
    *"Hi, my name is Jane Smith, my DOB is 1990-03-12. I’d like to book an appointment with Dr. Johnson at Clinic A. My insurance is Blue Cross, member ID BC789456."*  

    I’ll take care of filling out your details and booking your appointment. ✅
    """
)

# Session state initialization
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "patient_data" not in st.session_state:
    st.session_state["patient_data"] = None

# Chat input for patient request
user_input = st.chat_input("Describe your appointment request...")

if user_input:
    # Display user message
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # --- Step 1: Intake only (parse patient request) ---
    patient_data = parse_patient_request(user_input)

    # Show extracted patient data
    assistant_msg = (
        f"Here’s what I understood from your request:\n"
        f"```json\n{json.dumps(patient_data, indent=2)}\n```"
    )
    st.session_state["messages"].append({"role": "assistant", "content": assistant_msg})
    st.chat_message("assistant").write(assistant_msg)

    # Save patient data for later use
    st.session_state["patient_data"] = patient_data

# Display chat history
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# --- Step 2: Confirm & Book ---
if st.session_state["patient_data"]:
    st.subheader("✅ Confirm Appointment")

    if st.button("Book Appointment"):
        scheduler = create_scheduler_graph()
        final_state = scheduler.invoke({
            "patient": st.session_state["patient_data"],
            "lookup_result": None,
            "booking": None,
            "notified": False,
        })

        st.success("🎉 Appointment booked successfully!")
        st.json(final_state)
