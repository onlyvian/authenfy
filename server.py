import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# Get email credentials from .env
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

app = Flask(__name__)

# Store cooldowns per IP address
cooldowns = {}

@app.route("/contact", methods=["POST"])
def handle_contact():
    try:
        # Retrieve data from the contact form submission
        data = request.get_json(force=True)
        name = data.get("name")
        email = data.get("email")
        msg = data.get("message")

        # Check for empty fields
        if not name or not email or not msg:
            return jsonify({
                "status": "error",
                "message": "All fields are required."
            }), 400

        ip = request.remote_addr or "127.0.0.1"
        now = datetime.utcnow()

        # Implement 60-second cooldown
        if ip in cooldowns and (now - cooldowns[ip]) < timedelta(seconds=60):
            remaining = 60 - int((now - cooldowns[ip]).total_seconds())
            return jsonify({
                "status": "cooldown",
                "message": f"Please wait {remaining} seconds before sending another message."
            }), 429

        # Construct the email message
        msg_obj = EmailMessage()
        msg_obj.set_content(f"Message from {name} <{email}>\n\n{msg}")
        msg_obj["Subject"] = "New Contact Form Submission"
        msg_obj["From"] = SMTP_EMAIL
        msg_obj["To"] = RECEIVER_EMAIL

        # Attempt to send the email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            print("[✓] Trying to login...")
            smtp.login(SMTP_EMAIL, SMTP_PASSWORD)  # Login using SMTP credentials
            print("[✓] Login successful.")
            smtp.send_message(msg_obj)  # Send the email message
            print(f"[✓] Email sent from {email} to {RECEIVER_EMAIL}")

        cooldowns[ip] = now  # Update cooldown for the IP address
        return jsonify({
            "status": "success",
            "message": "✅ Email sent successfully!"
        })

    except smtplib.SMTPAuthenticationError as e:
        # Handle authentication errors (invalid username/password)
        print("[✗] SMTP Authentication Error:", e)
        return jsonify({"status": "error", "message": "Invalid SMTP credentials."}), 500
    except smtplib.SMTPException as e:
        # Catch all other SMTP errors (network issues, etc.)
        print("[✗] SMTP Error:", e)
        return jsonify({"status": "error", "message": "Failed to send email. Please try again later."}), 500
    except Exception as e:
        # General error handler for anything else
        print("[✗] Error:", e)
        return jsonify({"status": "error", "message": "❌ Something went wrong."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
