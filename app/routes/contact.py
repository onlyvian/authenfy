# app/routes/contact.py

from flask import Blueprint, render_template, request, jsonify
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
import os
import logging
from dotenv import load_dotenv

load_dotenv()

contact_bp = Blueprint('contact_bp', __name__)

# Load from env
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", 60))

# Logging
logger = logging.getLogger(__name__)
cooldowns = {}

def get_client_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr) or "127.0.0.1"

def send_email(name, email, message):
    try:
        msg = EmailMessage()
        msg['Subject'] = f"New message from {name}"
        msg['From'] = formataddr((name, SMTP_EMAIL))
        msg['To'] = RECEIVER_EMAIL
        msg['Reply-To'] = email
        msg.set_content(f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}")

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)

        return True, None
    except Exception as e:
        logger.error(f"Email send error: {e}")
        return False, str(e)

@contact_bp.route("/contact", methods=["POST"])
def handle_contact():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify(status="error", message="Invalid JSON"), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    message = data.get("message", "").strip()

    if not all([name, email, message]):
        return jsonify(status="error", message="All fields required"), 400

    ip = get_client_ip()
    now = datetime.utcnow()

    if ip in cooldowns and (now - cooldowns[ip]) < timedelta(seconds=COOLDOWN_SECONDS):
        return jsonify(status="cooldown", message="Please wait before sending again"), 429

    success, error = send_email(name, email, message)
    if success:
        cooldowns[ip] = now
        return jsonify(status="success", message="Message sent!")
    return jsonify(status="error", message=error), 500
