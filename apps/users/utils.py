import resend
from django.conf import settings

def send_password_reset_email(email, reset_url):
    if not settings.RESEND_API_KEY:
        print("Warning: RESEND_API_KEY is not set. Cannot send password reset email.")
        return False
        
    resend.api_key = settings.RESEND_API_KEY
    
    html_content = f"""
    <h2>Seapedia - Reset Your Password</h2>
    <p>We received a request to reset your password for your Seapedia account.</p>
    <p>Click the link below to set a new password:</p>
    <a href="{reset_url}" style="display:inline-block;padding:10px 20px;background-color:#0B3D91;color:white;text-decoration:none;border-radius:5px;">Reset Password</a>
    <p>If you didn't request this, you can safely ignore this email.</p>
    <br>
    <p>Best regards,<br>The Seapedia Team</p>
    """

    params = {
        "from": "onboarding@resend.dev",
        "to": email,
        "subject": "Seapedia - Password Reset",
        "html": html_content,
    }

    try:
        resend.Emails.send(params)
        return True
    except Exception as e:
        print(f"Error sending email via Resend: {e}")
        return False
