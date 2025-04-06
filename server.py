from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get email credentials from .env
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

app = Flask(__name__)

# Store cooldowns per IP address to limit submissions
cooldowns = {}

@app.route("/")
@app.route("/index.html")
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
    try:
        data = request.get_json(force=True)
        name = data.get("name")
        email = data.get("email")
        msg = data.get("message")

        # Check if all fields are filled
        if not name or not email or not msg:
            return jsonify({
                "status": "error",
                "message": "All fields are required."
            }), 400

        ip = request.remote_addr or "127.0.0.1"
        now = datetime.utcnow()

        # 60-second cooldown logic to prevent spam
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

        # Send the email via Gmail's SMTP server
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SMTP_EMAIL, SMTP_PASSWORD)
            smtp.send_message(msg_obj)

        # Print success and update the cooldown timestamp for the IP
        print(f"[✓] Email sent from {email} to {RECEIVER_EMAIL}")
        cooldowns[ip] = now  # Update cooldown to the current time

        # Return success response
        return jsonify({
            "status": "success",
            "message": "✅ Email sent successfully!"
        })

    except Exception as e:
        # Print any errors to the console for debugging
        print("[✗] Error sending email:", str(e))
        return jsonify({
            "status": "error",
            "message": "❌ Failed to send email."
        }), 500

if __name__ == "__main__":
    # Run the Flask app on all available IPs and port 5000
    app.run(host="0.0.0.0", port=5000, debug=True)
