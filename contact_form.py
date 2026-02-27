from datetime import datetime
from firebase_init import get_db
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()
db = get_db()

def _send_email(to_email, subject, body):
    SMTP_EMAIL    = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    CLIENT_NAME   = os.getenv("CLIENT_NAME", "MNPIEPL")

    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print(f"⚠ SMTP not configured - USER:{SMTP_EMAIL}")
        return

    try:
        msg = MIMEMultipart()
        msg['From']    = f"{CLIENT_NAME} <{SMTP_EMAIL}>"
        msg['To']      = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=15) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)

        print(f"✅ Email sent → {to_email}")
    except Exception as e:
        print(f"❌ Email error ({to_email}): {e}")

def contact_form(data):
    try:
        CLIENT_NAME = os.getenv("CLIENT_NAME", "MNPIEPL")
        ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

        # ── Save to Firebase ──────────────────────────────────────
        ref = db.reference("contacts")
        new_contact = ref.push({
            "name":       data.get("name"),
            "phone":      data.get("phone"),
            "email":      data.get("email"),
            "subject":    data.get("subject"),
            "message":    data.get("message"),
            "created_at": datetime.utcnow().isoformat(),
            "ip_address": data.get("ip_address"),
        })
        print(f"✅ Saved to Firebase → {new_contact.key}")

        # ── Send User Thank You Email ─────────────────────────────
        _send_email(
            data["email"],
            "Thank you for contacting us!",
            f"Hi {data['name']},\n\n"
            f"Thank you for reaching out! We received your message and will get back to you soon.\n\n"
            f"Best regards,\n{CLIENT_NAME} Team"
        )

        # ── Send Admin Notification Email ─────────────────────────
        _send_email(
            ADMIN_EMAIL,
            f"New Contact Form - {data.get('subject')}",
            f"NEW CONTACT FORM SUBMISSION\n\n"
            f"Name:    {data.get('name')}\n"
            f"Phone:   {data.get('phone')}\n"
            f"Email:   {data.get('email')}\n"
            f"Subject: {data.get('subject')}\n\n"
            f"Message:\n{data.get('message')}\n\n"
            f"---\n"
            f"IP:        {data.get('ip_address')}\n"
            f"Timestamp: {datetime.utcnow().isoformat()}"
        )

        return {"success": True, "message": "Message received!"}

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"success": False, "message": str(e)}
