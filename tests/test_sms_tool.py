import os
import pytest
from tools.sms_tool import SMSTool


def test_sms_simulation(tmp_path, monkeypatch):
    """
    Test SMS simulation mode (no Twilio).
    """
    # Use a temp log file so tests don't overwrite real logs
    log_file = tmp_path / "sms_log.txt"
    monkeypatch.chdir(tmp_path)

    sms_tool = SMSTool(use_twilio=False)
    result = sms_tool.send_sms("+911234567890", "Test SMS from simulation mode.")

    assert result["status"] == "simulated"
    assert "message" in result

    # Verify log file created
    assert log_file.exists()
    content = log_file.read_text()
    assert "Test SMS from simulation mode." in content


@pytest.mark.skipif(
    not os.getenv("TWILIO_SID") or not os.getenv("TWILIO_AUTH_TOKEN"),
    reason="No Twilio credentials in .env"
)
def test_sms_twilio():
    """
    Test Twilio SMS sending (requires real credentials and verified number).
    """
    sms_tool = SMSTool(use_twilio=True)
    result = sms_tool.send_sms(
        to_number=os.getenv("TEST_PHONE_NUMBER", "+911234567890"),
        message="Test SMS from Twilio mode."
    )

    assert result["status"] == "sent"
    assert "sid" in result
