from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv()

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

app = Flask(__name__)

# Store cooldowns per IP address
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

        if not name or not email or not msg:
            return jsonify({
                "status": "error",
                "message": "All fields are required."
            }), 400

        ip = request.remote_addr or "127.0.0.1"
        now = datetime.utcnow()

        # 60-second cooldown logic
        if ip in cooldowns and (now - cooldowns[ip]) < timedelta(seconds=60):
            remaining = 60 - int((now - cooldowns[ip]).total_seconds())
            return jsonify({
                "status": "cooldown",
                "message": f"Please wait {remaining} seconds before sending another message."
            }), 429

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SMTP_EMAIL, SMTP_PASSWORD)
            smtp.send_message(msg)

        print(f"[✓] Email sent from {email} to {RECEIVER_EMAIL}")
        return jsonify({"status": "success", "message": "Email sent successfully!"})

    except Exception as e:
        print("[✗] Error sending email:", str(e))
        return jsonify({"status": "error", "message": "Failed to send email."}), 500

if __name__ == "__main__":
    # Run on all available IPs (public access), port 5000
    app.run(host="0.0.0.0", port=5000, debug=True)
