import os
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST   = os.getenv("SMTP_HOST")
SMTP_PORT   = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER   = os.getenv("SMTP_USER")
SMTP_PASS   = os.getenv("SMTP_PASSWORD")
CLIENT_EMAIL = os.getenv("CLIENT_EMAIL")
CLIENT_NAME  = os.getenv("CLIENT_NAME", "MNPIEPL")

def _send(to_email, subject, html):
    try:
        msg = MIMEMultipart()
        msg["From"]    = SMTP_USER
        msg["To"]      = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        print(f"✅ Email sent → {to_email}")

    except Exception as e:
        print(f"❌ Email error → {to_email}: {e}")

# ── EMAIL TO CUSTOMER ─────────────────────────────────────────────
def send_user_thankyou(name, user_email):
    html = f"""
    <h2>Thank You for Contacting {CLIENT_NAME}</h2>
    <p>Dear {name},</p>
    <p>We have received your enquiry. Our team will contact you within 24 hours.</p>
    <br>
    <p>Regards,<br>{CLIENT_NAME}</p>
    """
    threading.Thread(target=_send, args=(user_email, "Thank you for contacting us", html), daemon=True).start()

# ── EMAIL TO ADMIN ────────────────────────────────────────────────
def send_admin_notification(data):
    html = f"""
    <h3>New Contact Form Submission</h3>
    <p><b>Name:</b> {data['name']}</p>
    <p><b>Phone:</b> {data['phone']}</p>
    <p><b>Email:</b> {data['email']}</p>
    <p><b>Subject:</b> {data['subject']}</p>
    <p><b>Message:</b> {data['message']}</p>
    """
    threading.Thread(target=_send, args=(CLIENT_EMAIL, "New Enquiry Received", html), daemon=True).start()
