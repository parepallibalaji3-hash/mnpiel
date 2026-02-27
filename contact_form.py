from datetime import datetime
from firebase_init import get_db
import resend
import os
from dotenv import load_dotenv

load_dotenv()
db = get_db()
resend.api_key = os.getenv("RESEND_API_KEY")

def contact_form(data):
    try:
        #── Save to Firebase ──────────────────────────────────────
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

        CLIENT_NAME = os.getenv("CLIENT_NAME", "MNPIEPL")
        ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
        FROM_EMAIL  = "onboarding@resend.dev"

        # ── Email to User ─────────────────────────────────────────
        resend.Emails.send({
            "from":    FROM_EMAIL,
            "to":      data["email"],
            "subject": "Thank you for contacting us!",
            "html":    f"""
                <h2>Thank You for Contacting {CLIENT_NAME}</h2>
                <p>Dear {data['name']},</p>
                <p>We received your message and will get back to you within 24 hours.</p>
                <p>Regards,<br>{CLIENT_NAME} Team</p>
            """
        })
        print(f"✅ User email sent → {data['email']}")

        # ── Email to Admin ────────────────────────────────────────
        resend.Emails.send({
            "from":    FROM_EMAIL,
            "to":      ADMIN_EMAIL,
            "subject": f"New Contact Form - {data.get('subject')}",
            "html":    f"""
                <h3>New Contact Form Submission</h3>
                <p><b>Name:</b> {data.get('name')}</p>
                <p><b>Phone:</b> {data.get('phone')}</p>
                <p><b>Email:</b> {data.get('email')}</p>
                <p><b>Subject:</b> {data.get('subject')}</p>
                <p><b>Message:</b> {data.get('message')}</p>
                <p><b>IP:</b> {data.get('ip_address')}</p>
            """
        })
        print(f"✅ Admin email sent → {ADMIN_EMAIL}")

        return {"success": True, "message": "Message received!"}

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"success": False, "message": str(e)}
