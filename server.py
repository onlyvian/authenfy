from flask import Flask, render_template
from app.routes.contact import contact_bp
import os

app = Flask(
    __name__,
    template_folder="app/templates",   # 👈 point to templates inside /app
    static_folder="app/static"         # 👈 point to static inside /app
)

app.config['JSON_SORT_KEYS'] = False

app.register_blueprint(contact_bp)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about.html")
def about():
    return render_template("about.html")

@app.route("/contact.html")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
