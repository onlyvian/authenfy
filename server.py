from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
COOLDOWN_SECONDS = 60

# Validate required environment variables
required_vars = [SMTP_EMAIL, SMTP_PASSWORD, RECEIVER_EMAIL]
if not all(required_vars):
    missing = [var for var in ["SMTP_EMAIL", "SMTP_PASSWORD", "RECEIVER_EMAIL"] if not os.getenv(var)]
    raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store cooldowns in memory (consider Redis for production)
cooldowns = {}

def get_client_ip():
    """Get client IP address considering proxy headers"""
    return request.headers.get('X-Forwarded-For', request.remote_addr) or "127.0.0.1"

def send_email(name, email, message):
    """Send email using SMTP with proper error handling"""
    try:
        msg = EmailMessage()
        msg['Subject'] = f"New message from {name} via website contact form"
        msg['From'] = formataddr((name, SMTP_EMAIL))
        msg['To'] = RECEIVER_EMAIL
        msg['Reply-To'] = email
        
        email_body = f"""
        Name: {name}
        Email: {email}
        Message:
        {message}
        """
        msg.set_content(email_body.strip())

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
        
        return True, None
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {str(e)}")
        return False, "SMTP server error"
    except Exception as e:
        logger.error(f"Email sending error: {str(e)}")
        return False, "Internal server error"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about.html")
def about():
    return render_template("about.html")

@app.route("/contact.html")
def contact():
    return render_template("contact.html")

@app.route("/contact", methods=["POST"])
def handle_contact():
    # Get and validate JSON data
    try:
        data = request.get_json(force=True)
    except Exception as e:
        logger.warning("Invalid JSON received")
        return jsonify(status="error", message="Invalid request format"), 400

    # Validate required fields
    required_fields = ['name', 'email', 'message']
    if not all(data.get(field) for field in required_fields):
        return jsonify(
            status="error",
            message="All fields are required: name, email, message"
        ), 400

    name = data['name'].strip()
    email = data['email'].strip().lower()
    message = data['message'].strip()

    # Basic email validation
    if '@' not in email or '.' not in email.split('@')[-1]:
        return jsonify(
            status="error",
            message="Please enter a valid email address"
        ), 400

    # Check cooldown
    ip = get_client_ip()
    now = datetime.utcnow()
    
    if ip in cooldowns:
        elapsed = now - cooldowns[ip]
        if elapsed < timedelta(seconds=COOLDOWN_SECONDS):
            remaining = COOLDOWN_SECONDS - elapsed.total_seconds()
            return jsonify(
                status="cooldown",
                message=f"Please wait {int(remaining)} seconds before sending another message"
            ), 429

    # Attempt to send email
    success, error = send_email(name, email, message)
    
    if success:
        # Update cooldown only after successful send
        cooldowns[ip] = now
        logger.info(f"Email sent from {email} ({ip})")
        return jsonify(
            status="success",
            message="Your message has been sent successfully!"
        )
    
    return jsonify(
        status="error",
        message=f"Failed to send email: {error}"
    ), 500

if __name__ == "__main__":
    # Use environment variable for debug mode
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)