import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()  # load SMTP creds from .env


class EmailTool:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_pass = os.getenv("SMTP_PASS")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)

        if not self.smtp_user or not self.smtp_pass:
            raise ValueError("❌ Missing SMTP_USER or SMTP_PASS in environment variables.")

    def send_email(self, to_email: str, subject: str, body: str, html: str | None = None):
        """Generic email sender (plain + HTML)."""
        msg = MIMEMultipart("alternative")
        msg["From"] = self.from_email  # type: ignore
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))
        if html:
            msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)  # type: ignore
            server.sendmail(self.from_email, to_email, msg.as_string())  # type: ignore

        print(f"✅ Email sent to {to_email} with subject '{subject}'")

    # -------------------------------
    # Appointment Booking Link Email
    # -------------------------------
    def send_booking_link_email(
        self,
        to_email: str,
        patient_name: str,
        booking_url: str,
        doctor: str,
        clinic_location: str,
        duration_minutes: int,
    ):
        """Send patient a booking link email to choose a slot."""
        subject = f"Book Your Appointment with {doctor}"

        text_body = (
            f"Hello {patient_name},\n\n"
            f"Please book your {duration_minutes}-minute appointment with {doctor} "
            f"at {clinic_location} using the link below:\n\n"
            f"{booking_url}\n\n"
            "Thank you,\nAI Scheduler Team"
        )

        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <p>Hello <b>{patient_name}</b>,</p>
            <p>Please use the link below to book your <b>{duration_minutes}-minute</b> appointment with <b>{doctor}</b> at <b>{clinic_location}</b>:</p>
            <p><a href="{booking_url}" style="color: #007bff; text-decoration: none;">Click here to book your appointment</a></p>
            <p style="color: gray; font-size: 12px;">
              Thank you,<br>
              AI Scheduler Team
            </p>
          </body>
        </html>
        """

        self.send_email(to_email, subject, text_body, html_body)

    # -------------------------------
    # Appointment Reminder Email
    # -------------------------------
    def send_reminder_email(
        self,
        to_email: str,
        patient_name: str,
        appointment_dt: str,
        clinic_location: str,
    ):
        """Send a reminder for an already booked appointment."""
        subject = f"Reminder: Your Appointment on {appointment_dt}"

        text_body = (
            f"Hello {patient_name},\n\n"
            f"This is a reminder for your upcoming appointment on {appointment_dt}.\n"
            f"Location: {clinic_location}\n\n"
            "Please arrive 10 minutes early.\n\n"
            "Thank you,\nAI Scheduler Team"
        )

        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <p>Hello <b>{patient_name}</b>,</p>
            <p>This is a reminder for your upcoming appointment on:</p>
            <p><b>{appointment_dt}</b></p>
            <p>Location: {clinic_location}</p>
            <p>Please arrive 10 minutes early.</p>
            <p style="color: gray; font-size: 12px;">
              Thank you,<br>
              AI Scheduler Team
            </p>
          </body>
        </html>
        """

        self.send_email(to_email, subject, text_body, html_body)
