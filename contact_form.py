from datetime import datetime
from firebase_init import get_db
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()
db = get_db()

def contact_form(data):
    try:
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
        print(f"✅ Firebase saved → {new_contact.key}")

        # ── Print env vars to debug ───────────────────────────────
        SMTP_USER     = os.getenv("SMTP_USER")
        SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
        ADMIN_EMAIL   = os.getenv("ADMIN_EMAIL")
        CLIENT_NAME   = os.getenv("CLIENT_NAME", "MNPIEPL")

        print(f"📧 SMTP_USER={SMTP_USER}")
        print(f"🔑 SMTP_PASSWORD={'SET' if SMTP_PASSWORD else 'NOT SET'}")
        print(f"📬 ADMIN_EMAIL={ADMIN_EMAIL}")

        # ── Send Email Directly ───────────────────────────────────
        msg = MIMEMultipart()
        msg['From']    = SMTP_USER
        msg['To']      = ADMIN_EMAIL
        msg['Subject'] = f"New Contact - {data.get('subject')}"
        msg.attach(MIMEText(f"Name: {data.get('name')}\nEmail: {data.get('email')}\nMessage: {data.get('message')}", 'plain'))

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        print(f"✅ Email sent → {ADMIN_EMAIL}")

        return {"success": True, "message": "Message received!"}

    except Exception as e:
        print(f"❌ FULL ERROR: {e}")
        return {"success": False, "message": str(e)}
