import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load detected anomalies
anomalies = pd.read_csv("real_time_anomalies.csv")

# Email server configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "utkarshsingh.0902@gmail.com"
SENDER_PASSWORD = "qrmt oqbu dsbo mvdb"  # Use an app password (not your real password!)

def send_email(recipient_email, user_id, session_duration):
    """Sends an anomaly alert email to the user."""
    subject = f" Alert: Unusual Activity Detected (User {user_id})"
    body = f"""
    Dear User {user_id},

    We have detected unusual activity in your browsing pattern.
    
    - Session Duration: {session_duration} seconds
    - This activity is flagged as **anomalous** based on behavioral analysis.

    If this was not you, please take necessary actions.

    Regards,
    Security Team
    """

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        print(f"✔ Alert sent to {recipient_email}")
    except Exception as e:
        print(f" Failed to send email to {recipient_email}: {e}")

# Send alerts to affected users
for _, row in anomalies.iterrows():
    send_email(row["E_mail"], row["User_Id"], row["Session_Duration"])
