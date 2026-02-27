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

        CLIENT_NAME = os.getenv("CLIENT_NAME", "MNPIEPL")
        ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "parepallibalaji3@gmail.com")
        FROM_EMAIL  = "onboarding@resend.dev"

        # ── Email to Admin (New Contact Notification) ─────────────
        resend.Emails.send({
            "from":    FROM_EMAIL,
            "to":      ADMIN_EMAIL,
            "subject": f"New Contact Form - {data.get('subject')}",
            "html":    f"""
                <h2>New Contact Form Submission</h2>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><b>Name</b></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{data.get('name')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><b>Phone</b></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{data.get('phone')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><b>Email</b></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{data.get('email')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><b>Subject</b></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{data.get('subject')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><b>Message</b></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{data.get('message')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><b>IP Address</b></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{data.get('ip_address')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><b>Timestamp</b></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{datetime.utcnow().isoformat()}</td>
                    </tr>
                </table>
            """
        })
        print(f"✅ Admin email sent → {ADMIN_EMAIL}")

        # ── Email to Admin (User Thank You Copy) ──────────────────
        resend.Emails.send({
            "from":    FROM_EMAIL,
            "to":      ADMIN_EMAIL,
            "subject": f"Thank You Email Copy - {data.get('name')}",
            "html":    f"""
                <p><b>Note:</b> This is a copy of the thank you email that would be sent to {data.get('email')}</p>
                <hr>
                <h2>Thank You for Contacting {CLIENT_NAME}</h2>
                <p>Dear {data.get('name')},</p>
                <p>We have received your enquiry regarding <b>{data.get('subject')}</b>.</p>
                <p>Our team will get back to you within 24 hours.</p>
                <br>
                <p>Regards,<br>
                <b>{CLIENT_NAME} Team</b></p>
            """
        })
        print(f"✅ Thank you copy sent → {ADMIN_EMAIL}")

        return {"success": True, "message": "Message received!"}

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"success": False, "message": str(e)}
