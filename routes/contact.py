from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

contact_bp = Blueprint('contact', __name__)

# Store cooldowns based on IP
cooldowns = {}

@contact_bp.route("/contact", methods=["POST"])
def handle_contact():
    try:
        data = request.get_json(force=True)
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        message = data.get("message", "").strip()

        if not name or not email or not message:
            return jsonify({
                "status": "error",
                "message": "All fields are required."
            }), 400

        # Get client IP
        ip = request.remote_addr or "127.0.0.1"
        now = datetime.utcnow()

        # Check for cooldown (60 seconds)
        if ip in cooldowns and (now - cooldowns[ip]) < timedelta(seconds=60):
            remaining = 60 - int((now - cooldowns[ip]).total_seconds())
            return jsonify({
                "status": "cooldown",
                "message": f"⏳ Please wait {remaining} seconds before sending another message."
            }), 429

        # Log message (or later send to email / save to DB)
        print(f"📥 Message from {name} <{email}>: {message}")

        # Set cooldown
        cooldowns[ip] = now

        return jsonify({
            "status": "success",
            "message": "✅ Message sent successfully! You can send again in 60 seconds."
        })

    except Exception as e:
        print("❌ Server error:", e)
        return jsonify({
            "status": "error",
            "message": "❌ Something went wrong. Please try again later."
        }), 500
