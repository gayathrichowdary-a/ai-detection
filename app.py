from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fraudshield_secret_2024")

# ─────────────────────────────
# DATABASE SETUP
# ─────────────────────────────
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fraud.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class User(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    email    = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)


with app.app_context():
    db.create_all()


# ─────────────────────────────
# AUTH ROUTES
# ─────────────────────────────
@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["user"] = email
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid email or password.")
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if User.query.filter_by(email=email).first():
            return render_template("signup.html", error="Email already registered.")
        hashed = generate_password_hash(password)
        db.session.add(User(email=email, password=hashed))
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ─────────────────────────────
# DASHBOARD
# ─────────────────────────────
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")


# ─────────────────────────────
# CHATBOT PAGE
# ─────────────────────────────
@app.route("/chatbot")
def chatbot():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("chatbot.html")


# ─────────────────────────────
# CHATBOT API  (/chat)
# ─────────────────────────────
# Rule-based fraud knowledge base (no external API needed)
RESPONSES = {
    # Greetings
    r"\b(hi|hello|hey|hola)\b": (
        "👋 Hello! I'm the FraudShield AI Assistant. "
        "Ask me anything about fraud detection, risk scores, or transaction safety!"
    ),

    # What is fraud detection
    r"what is fraud|fraud detection|how does.*work": (
        "🔍 <b>Fraud Detection</b> is the process of identifying suspicious financial transactions "
        "using AI and pattern recognition.<br><br>"
        "Our system analyzes:<br>"
        "• Merchant type & category<br>"
        "• Transaction amount<br>"
        "• Spending patterns<br><br>"
        "It then assigns a <b>risk score (0–100)</b> and classifies the transaction as "
        "<b>Safe ✅</b>, <b>Suspicious ⚠️</b>, or <b>Fraud 🚨</b>."
    ),

    # Risk score
    r"risk score|score calculated|how.*score": (
        "⚡ <b>Risk Score (0–100)</b><br><br>"
        "• <b>0–39</b> → ✅ Safe (amount below ₹50,000)<br>"
        "• <b>40–79</b> → ⚠️ Suspicious (₹50,000 – ₹1,00,000)<br>"
        "• <b>80–100</b> → 🚨 Fraud (above ₹1,00,000)<br><br>"
        "A higher risk score means higher probability of fraudulent activity."
    ),

    # Suspicious transaction
    r"suspicious|what.*suspicious|why.*flagged": (
        "⚠️ A transaction is marked <b>Suspicious</b> when:<br><br>"
        "• Amount is unusually high compared to normal patterns<br>"
        "• Merchant category doesn't match typical spending<br>"
        "• Transaction occurs at an odd time or location<br>"
        "• Multiple large transactions in a short period<br><br>"
        "Suspicious transactions are reviewed more carefully before being flagged as fraud."
    ),

    # Fraud tips
    r"tips|avoid fraud|prevent|safe.*transaction|stay safe": (
        "🛡️ <b>Tips to Stay Safe from Fraud:</b><br><br>"
        "1. Never share OTP or card details with anyone<br>"
        "2. Use strong, unique passwords for banking apps<br>"
        "3. Monitor your transactions regularly<br>"
        "4. Avoid public Wi-Fi for financial transactions<br>"
        "5. Enable SMS/email alerts for all transactions<br>"
        "6. Report suspicious activity immediately to your bank"
    ),

    # High amount
    r"large|high amount|big transaction|₹|rupee": (
        "🚨 Transactions <b>above ₹1,00,000</b> are automatically flagged as <b>High Risk Fraud</b> "
        "in our system with a risk score of 80–95.<br><br>"
        "This is because unusually large amounts are a common indicator of:<br>"
        "• Unauthorized card usage<br>"
        "• Account takeover fraud<br>"
        "• Money laundering activity"
    ),

    # Categories
    r"category|categories|merchant|amazon|flipkart|electronics": (
        "🛒 <b>High-risk merchant categories</b> in fraud statistics:<br><br>"
        "• Electronics — highest fraud rate (~42%)<br>"
        "• Luxury goods — high value, easy to resell<br>"
        "• International transfers — often unverified<br>"
        "• Gift cards & crypto — hard to trace<br><br>"
        "Low-risk categories include food, grocery, and utility payments."
    ),

    # CSV / export
    r"csv|export|download|report": (
        "📥 You can <b>Export your transaction data as CSV</b> directly from the dashboard.<br><br>"
        "The report includes:<br>"
        "• Merchant name<br>"
        "• Category<br>"
        "• Amount (₹)<br>"
        "• Status (Safe / Suspicious / Fraud)<br>"
        "• Risk Score<br><br>"
        "Click the <b>⬇ Export CSV</b> button on the dashboard."
    ),

    # Machine learning
    r"machine learning|ml|model|ai|artificial intelligence": (
        "🤖 Our system uses <b>Machine Learning</b> models trained on financial transaction data.<br><br>"
        "Models used:<br>"
        "• <b>Random Forest</b> — for pattern classification<br>"
        "• <b>Logistic Regression</b> — for probability scoring<br>"
        "• <b>Anomaly Detection</b> — for outlier transactions<br><br>"
        "These models analyze hundreds of features to detect fraud in real-time."
    ),

    # Help / features
    r"help|features|what can you|what do you": (
        "💬 <b>I can help you with:</b><br><br>"
        "• Explaining how fraud detection works<br>"
        "• Understanding risk scores and classifications<br>"
        "• Tips to prevent fraud<br>"
        "• How to read your dashboard analytics<br>"
        "• Questions about merchants, categories & amounts<br>"
        "• How to export transaction reports<br><br>"
        "Just type your question!"
    ),
}

DEFAULT_REPLY = (
    "🤔 I'm not sure about that specific question, but I'm here to help with:<br><br>"
    "• Fraud detection concepts<br>"
    "• Risk score explanation<br>"
    "• Transaction safety tips<br>"
    "• Dashboard features<br><br>"
    "Try asking: <i>'How is the risk score calculated?'</i>"
)


@app.route("/chat", methods=["POST"])
def chat():
    data    = request.get_json()
    message = (data.get("message", "") or "").lower().strip()

    for pattern, reply in RESPONSES.items():
        if re.search(pattern, message):
            return jsonify({"reply": reply})

    return jsonify({"reply": DEFAULT_REPLY})


# ─────────────────────────────
# RUN
# ─────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)