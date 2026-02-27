from datetime import datetime
from firebase_init import get_db
import requests
import os
from dotenv import load_dotenv

load_dotenv()
db = get_db()

def _send_email(to_email, subject, html_body):
    RESEND_API_KEY = os.getenv("RESEND_API_KEY")
    SMTP_USER      = os.getenv("SMTP_USER")
    CLIENT_NAME    = os.getenv("CLIENT_NAME", "MNPIEPL")

    if not RESEND_API_KEY:
        print("⚠ RESEND_API_KEY not configured")
        return False

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "from":    f"{CLIENT_NAME} <onboarding@resend.dev>",
                "to":      [to_email],
                "subject": subject,
                "html":    html_body
            },
            timeout=10
        )

        if response.status_code == 200 or response.status_code == 201:
            print(f"✅ Email sent → {to_email}")
            return True
        else:
            print(f"❌ Email failed ({to_email}): {response.text}")
            return False

    except Exception as e:
        print(f"❌ Email error ({to_email}): {e}")
        return False


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

        # ── Send Admin Notification (User Details) ────────────────
        _send_email(
            ADMIN_EMAIL,
            f"New Enquiry from {data.get('name')} - {data.get('subject')}",
            f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                    New Contact Form Submission
                </h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background: #f8f9fa;">
                        <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold; width: 30%;">Name</td>
                        <td style="padding: 12px; border: 1px solid #dee2e6;">{data.get('name')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Phone</td>
                        <td style="padding: 12px; border: 1px solid #dee2e6;">{data.get('phone')}</td>
                    </tr>
                    <tr style="background: #f8f9fa;">
                        <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Email</td>
                        <td style="padding: 12px; border: 1px solid #dee2e6;">{data.get('email')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Subject</td>
                        <td style="padding: 12px; border: 1px solid #dee2e6;">{data.get('subject')}</td>
                    </tr>
                    <tr style="background: #f8f9fa;">
                        <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Message</td>
                        <td style="padding: 12px; border: 1px solid #dee2e6;">{data.get('message')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">IP Address</td>
                        <td style="padding: 12px; border: 1px solid #dee2e6;">{data.get('ip_address')}</td>
                    </tr>
                    <tr style="background: #f8f9fa;">
                        <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Timestamp</td>
                        <td style="padding: 12px; border: 1px solid #dee2e6;">{datetime.utcnow().isoformat()}</td>
                    </tr>
                </table>
                <p style="color: #7f8c8d; font-size: 12px; margin-top: 20px;">
                    This email was sent automatically by {CLIENT_NAME} contact form.
                </p>
            </div>
            """
        )

        # ── Send Thank You to User ────────────────────────────────
        _send_email(
            data.get("email"),
            f"Thank you for contacting {CLIENT_NAME}!",
            f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2c3e50;">Thank You for Contacting {CLIENT_NAME}!</h2>
                <p>Dear <strong>{data.get('name')}</strong>,</p>
                <p>We have received your enquiry regarding <strong>{data.get('subject')}</strong>.</p>
                <p>Our team will review your message and get back to you within <strong>24 hours</strong>.</p>
                <br>
                <p>Best regards,</p>
                <p><strong>{CLIENT_NAME} Team</strong></p>
            </div>
            """
        )

        return {"success": True, "message": "Message received!"}

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"success": False, "message": str(e)}
