import sqlite3
import pytest
from tools.calendar_tool import CalendarTool
from scripts.seed_schedules import seed_schedules

DB_PATH = "db/appointments.db"


@pytest.fixture(scope="module", autouse=True)
def setup_schedules():
    """Seed fallback schedules before running tests."""
    seed_schedules(num_days=2, slots_per_day=3)


def test_get_slots_fallback():
    cal = CalendarTool(use_fallback=True)
    slots = cal.get_available_slots(limit=5)
    assert isinstance(slots, list)
    assert len(slots) > 0
    assert "start" in slots[0] or "start_dt" in slots[0]  # handle dict format


def test_book_slot_fallback():
    cal = CalendarTool(use_fallback=True)
    slots = cal.get_available_slots(limit=1)
    assert len(slots) > 0

    slot_id = slots[0]["id"] # type: ignore
    success = cal.book_slot(slot_id, patient_mrn="MRN001")
    assert success is True

    # Verify DB updated
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT status FROM doctor_schedules WHERE id=?", (slot_id,))
    status = cur.fetchone()[0]
    conn.close()
    assert status == "booked"


@pytest.mark.skipif(not CalendarTool().api_key, reason="No Calendly API key configured")
def test_calendly_event_types():
    cal = CalendarTool()
    event_types = cal.list_event_types()
    assert isinstance(event_types, list)
    assert len(event_types) > 0


@pytest.mark.skipif(not CalendarTool().api_key, reason="No Calendly API key configured")
def test_calendly_slots():
    cal = CalendarTool()
    event_types = cal.list_event_types()
    if event_types:
        uri = event_types[0]["uri"]
        slot_info = cal.get_available_slots(uri, days_ahead=3)
        assert isinstance(slot_info, dict)
        assert "booking_url" in slot_info
        assert slot_info["booking_url"].startswith("https://calendly.com/")

