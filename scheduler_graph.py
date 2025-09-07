from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, Dict, cast
from tools.patient_lookup import lookup_patient
from tools.calendar_tool import CalendarTool
from tools.email_tool import EmailTool
from tools.sms_tool import SMSTool
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
import json


# ---- Define State ----
class SchedulerState(TypedDict):
    patient: Dict
    lookup_result: Optional[Dict]
    booking: Optional[Dict]
    notified: bool


# ---- Define Nodes ----
def parse_patient_request(request: str) -> dict:
    """
    Use Ollama to parse free-text patient request into structured JSON.
    """
    llm = Ollama(model="mistral", temperature=0)
    prompt = PromptTemplate.from_template("""
    You are a medical intake assistant. Extract structured patient data 
    from the request below. Always return valid JSON with keys:
    name, dob, mrn, email, phone, doctor, location, insurance_carrier,
    insurance_member_id, insurance_group.

    Request: {request}
    """)
    response = llm.invoke(prompt.format(request=request))
    try:
        return json.loads(response)
    except Exception:
        return {"raw_text": request}

def intake_node(state: SchedulerState) -> SchedulerState:
    """
    Graph node wrapper for intake.
    """
    patient = state["patient"]

    # Only parse if there's a free-text request
    if "request" in patient:
        parsed = parse_patient_request(patient["request"])
        patient.update(parsed)

    print("🟢 Intake:", patient)
    state["patient"] = patient
    return state


def lookup_node(state: SchedulerState):
    patient = state["patient"]
    lookup_res = lookup_patient(
        name=patient.get("name","John Doe"),
        dob=patient.get("dob","1970-01-01"),
        mrn=patient.get("mrn"),
    )
    print("📋 Lookup:", lookup_res)
    state["lookup_result"] = lookup_res
    return state


def booking_node(state: SchedulerState):
    patient = state["patient"]
    lookup_res = state["lookup_result"] or {}
    duration = 30 if lookup_res.get("classification") == "returning" else 60

    cal = CalendarTool()

    if cal.use_fallback:
        # fallback booking using slot_id (for demo we pick first available)
        slots = cal.get_available_slots_fallback(limit=1)
        if not slots:
            raise ValueError("❌ No slots available in fallback DB")
        slot = slots[0]
        success = cal.book_slot_fallback(slot["id"], patient.get("mrn") or "TEMP-MRN")
        booking = {
            "slot_id": slot["id"],
            "start_time": slot["start"],
            "end_time": slot["end"],
            "duration_minutes": duration,
            "status": "booked" if success else "failed",
            "booking_url": None,
        }
    else:
        # Calendly mode – just generate a scheduling link for the right event type
       # pick the event type that matches duration
        target_duration = duration
        event_types = cal.list_event_types()

        matched_event = None
        for et in event_types:
            if str(target_duration) in et["name"]:  # e.g. "30 Minute Meeting"
                matched_event = et
                break

        if not matched_event:
            raise ValueError(f"❌ No Calendly event type found for {target_duration} minutes")

        booking_url = cal.create_scheduling_link(matched_event["uri"])

        booking = {
            "event_type": matched_event,
            "duration_minutes": duration,
            "booking_url": booking_url,
            "start_time": "TBD",  # actual slot comes via webhook
            "status": "pending",
        }

    print("📅 Booking:", booking)
    state["booking"] = booking
    return state



def notify_node(state: SchedulerState):
    patient = state["patient"]
    booking = state["booking"] or {}

    email_tool = EmailTool()
    email_tool.send_booking_link_email(
        to_email=patient["email"],
        patient_name=patient["name"],
        doctor=patient.get("doctor", "your doctor"),
        booking_url=booking.get("booking_url", "N/A"),
        clinic_location=patient["location"],
        duration_minutes=booking.get("duration_minutes", 30),
    )

    sms_tool = SMSTool(use_twilio=True)
    sms_tool.send_sms(
        patient["phone"],
        f"Hello {patient['name']}, please book your {booking.get('duration_minutes', 'TBD')}-minute "
        f"appointment using this link: {booking.get('booking_url', 'N/A')}"
    )

    state["notified"] = True
    return state

# ---- Build Graph ----
def create_scheduler_graph():
    llm = Ollama(model="llama3:8b", temperature=0)  # strictly Ollama
    graph = StateGraph(SchedulerState)

    graph.add_node("intake", intake_node)
    graph.add_node("lookup", lookup_node)
    graph.add_node("booking", booking_node)
    graph.add_node("notify", notify_node)

    graph.set_entry_point("intake")
    graph.add_edge("intake", "lookup")
    graph.add_edge("lookup", "booking")
    graph.add_edge("booking", "notify")
    graph.add_edge("notify", END)

    return graph.compile()


if __name__ == "__main__":
    scheduler = create_scheduler_graph()

    patient_data = {
        "name": "John Doe",
        "dob": "1980-05-15",
        "mrn": None,
        "email": "patient@example.com",
        "phone": "+911234567890",
        "doctor": "Dr. Smith",
        "location": "Clinic A - Main Street",
        "insurance_carrier": "Blue Cross",
        "insurance_member_id": "BC123456",
        "insurance_group": "GRP7890",
    }

    final_state = scheduler.invoke({
        "patient": patient_data,
        "lookup_result": None,
        "booking": None,
        "notified": False,
    })

    print("\n✅ Final State:", final_state)
