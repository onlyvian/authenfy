from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta

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
        message = data.get("message")

        if not name or not email or not message:
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

        print(f"Message from {name} <{email}>: {message}")
        cooldowns[ip] = now

        return jsonify({
            "status": "success",
            "message": "✅ Message sent successfully!"
        })

    except Exception as e:
        print("Server error:", e)
        return jsonify({
            "status": "error",
            "message": "❌ Something went wrong on the server."
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
