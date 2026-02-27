from datetime import datetime
from firebase_init import get_db
import requests
import os
import threading
from dotenv import load_dotenv

load_dotenv()
db = get_db()

def _send_email(to_email, subject, html_body):
    RESEND_API_KEY = os.getenv("RESEND_API_KEY")
    CLIENT_NAME    = os.getenv("CLIENT_NAME", "MNPIEPL")

    if not RESEND_API_KEY:
        print("⚠ RESEND_API_KEY not configured")
        return

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
        if response.status_code in [200, 201]:
            print(f"✅ Email sent → {to_email}")
        else:
            print(f"❌ Email failed ({to_email}): {response.text}")
    except Exception as e:
        print(f"❌ Email error ({to_email}): {e}")


def _send_all_emails(data):
    """Runs in background thread — sends both emails in parallel"""
    CLIENT_NAME = os.getenv("CLIENT_NAME", "MNPIEPL")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

    # Run both emails at the same time
    t1 = threading.Thread(target=_send_email, args=(
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
        </div>
        """
    ), daemon=True)

    t2 = threading.Thread(target=_send_email, args=(
        data.get("email"),
        f"Thank you for contacting {CLIENT_NAME}!",
        f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2c3e50;">Thank You for Contacting {CLIENT_NAME}!</h2>
            <p>Dear <strong>{data.get('name')}</strong>,</p>
            <p>We have received your enquiry regarding <strong>{data.get('subject')}</strong>.</p>
            <p>Our team will get back to you within <strong>24 hours</strong>.</p>
            <br>
            <p>Best regards,</p>
            <p><strong>{CLIENT_NAME} Team</strong></p>
        </div>
        """
    ), daemon=True)

    t1.start()
    t2.start()
    t1.join()
    t2.join()


def contact_form(data):
    try:
        # ── Save to Firebase instantly ────────────────────────────
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

        # ── Fire emails in background — don't wait ────────────────
        threading.Thread(
            target=_send_all_emails,
            args=(data,),
            daemon=True
        ).start()

        # ⚡ Returns immediately — user sees success instantly
        return {"success": True, "message": "Message received!"}

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"success": False, "message": str(e)}
