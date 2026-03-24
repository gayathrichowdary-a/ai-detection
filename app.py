from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import joblib
import numpy as np
import requests
import json

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fraudshield_secret_2024")

# ─────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fraud.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    email    = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

class Transaction(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    user      = db.Column(db.String(150), nullable=False)
    merchant  = db.Column(db.String(100))
    category  = db.Column(db.String(100))
    amount    = db.Column(db.Float)
    status    = db.Column(db.String(20))
    risk      = db.Column(db.Integer)
    timestamp = db.Column(db.String(50))

with app.app_context():
    db.create_all()

# ─────────────────────────────────────────
# LOAD ML MODEL (if exists)
# ─────────────────────────────────────────
model  = None
scaler = None

try:
    model  = joblib.load("model.pkl")
    scaler = joblib.load("scaler.pkl")
    print("✅ ML model loaded")
except Exception as e:
    print(f"⚠️ ML model not found, using rule-based: {e}")

# ─────────────────────────────────────────
# CLAUDE API KEY  (set in Render env vars)
# ─────────────────────────────────────────
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")

# ─────────────────────────────────────────
# AUTH ROUTES
# ─────────────────────────────────────────
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
        db.session.add(User(email=email, password=generate_password_hash(password)))
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ─────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")

# ─────────────────────────────────────────
# CHATBOT PAGE
# ─────────────────────────────────────────
@app.route("/chatbot")
def chatbot():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("chatbot.html")

# ─────────────────────────────────────────
# TRANSACTION: ADD + GET
# ─────────────────────────────────────────
@app.route("/add_transaction", methods=["POST"])
def add_transaction():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data     = request.get_json()
    merchant = data.get("merchant", "").strip()
    category = data.get("category", "").strip()
    amount   = float(data.get("amount", 0))

    # ML prediction if model loaded, else rule-based
    if model and scaler:
        try:
            cat_map = {"food":1,"electronics":2,"clothes":3,"grocery":4,"travel":5,"other":6}
            cat_code = cat_map.get(category.lower(), 6)
            features = np.array([[amount, cat_code]])
            features_scaled = scaler.transform(features)
            pred = model.predict(features_scaled)[0]
            prob = model.predict_proba(features_scaled)[0][1]
            risk   = int(prob * 100)
            status = "fraud" if pred == 1 else ("warn" if risk > 40 else "safe")
        except Exception:
            status, risk = _rule_based(amount)
    else:
        status, risk = _rule_based(amount)

    from datetime import datetime
    tx = Transaction(
        user=session["user"], merchant=merchant, category=category,
        amount=amount, status=status, risk=risk,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M")
    )
    db.session.add(tx)
    db.session.commit()

    return jsonify({"status": status, "risk": risk, "id": tx.id})

def _rule_based(amount):
    if amount > 100000:
        return "fraud", min(95, 80 + int((amount - 100000) / 10000))
    elif amount > 50000:
        return "warn", 50 + int((amount - 50000) / 2000)
    else:
        return "safe", max(5, int(amount / 2500))

@app.route("/get_transactions")
def get_transactions():
    if "user" not in session:
        return jsonify([])
    txs = Transaction.query.filter_by(user=session["user"]).order_by(Transaction.id.desc()).all()
    return jsonify([{
        "merchant": t.merchant, "category": t.category,
        "amount": t.amount, "status": t.status,
        "risk": t.risk, "timestamp": t.timestamp
    } for t in txs])

# ─────────────────────────────────────────
# FRAUD REPORT (GenAI Feature 1)
# ─────────────────────────────────────────
@app.route("/generate_report", methods=["POST"])
def generate_report():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    txs = Transaction.query.filter_by(user=session["user"]).all()
    if not txs:
        return jsonify({"report": "No transactions found to analyze."})

    total  = len(txs)
    frauds = [t for t in txs if t.status == "fraud"]
    warns  = [t for t in txs if t.status == "warn"]
    safes  = [t for t in txs if t.status == "safe"]
    total_amt  = sum(t.amount for t in txs)
    fraud_amt  = sum(t.amount for t in frauds)
    avg_risk   = sum(t.risk for t in txs) / total

    summary = (
        f"User: {session['user']}\n"
        f"Total transactions: {total}\n"
        f"Fraud: {len(frauds)}, Suspicious: {len(warns)}, Safe: {len(safes)}\n"
        f"Total amount scanned: ₹{total_amt:,.0f}\n"
        f"Fraudulent amount: ₹{fraud_amt:,.0f}\n"
        f"Average risk score: {avg_risk:.1f}/100\n"
        f"Fraud merchants: {', '.join(set(t.merchant for t in frauds)) or 'None'}\n"
        f"Suspicious merchants: {', '.join(set(t.merchant for t in warns)) or 'None'}"
    )

    if CLAUDE_API_KEY:
        try:
            report = _call_claude(
                f"""You are a financial fraud analyst AI. 
Analyze this transaction summary and generate a professional fraud analysis report.
Include: overall risk assessment, key findings, suspicious patterns, and recommended actions.
Keep it concise (under 200 words). Use bullet points.

Transaction Data:
{summary}"""
            )
        except Exception as e:
            report = _fallback_report(total, frauds, warns, avg_risk, fraud_amt)
    else:
        report = _fallback_report(total, frauds, warns, avg_risk, fraud_amt)

    return jsonify({"report": report})

def _fallback_report(total, frauds, warns, avg_risk, fraud_amt):
    fraud_rate = (len(frauds) / total * 100) if total else 0
    risk_level = "HIGH" if avg_risk > 60 else "MEDIUM" if avg_risk > 30 else "LOW"
    return (
        f"📊 **Fraud Analysis Report**\n\n"
        f"• Total transactions analyzed: {total}\n"
        f"• Fraud detected: {len(frauds)} ({fraud_rate:.1f}%)\n"
        f"• Suspicious: {len(warns)}\n"
        f"• Fraudulent amount blocked: ₹{fraud_amt:,.0f}\n"
        f"• Average risk score: {avg_risk:.0f}/100\n"
        f"• Overall risk level: **{risk_level}**\n\n"
        f"{'⚠️ Immediate action required — multiple fraud transactions detected.' if len(frauds) > 2 else '✅ Transaction activity appears mostly normal.'}"
    )

# ─────────────────────────────────────────
# EXPLAIN TRANSACTION (GenAI Feature 2)
# ─────────────────────────────────────────
@app.route("/explain_transaction", methods=["POST"])
def explain_transaction():
    if "user" not in session:
        return jsonify({"explanation": "Not logged in"}), 401

    data     = request.get_json()
    merchant = data.get("merchant", "")
    category = data.get("category", "")
    amount   = data.get("amount", 0)
    status   = data.get("status", "")
    risk     = data.get("risk", 0)

    if CLAUDE_API_KEY:
        try:
            explanation = _call_claude(
                f"""You are a fraud detection AI assistant.
Explain in 2-3 simple sentences why this transaction was flagged as '{status.upper()}'.
Be specific about the risk factors. Use simple language a customer would understand.

Transaction details:
- Merchant: {merchant}
- Category: {category}
- Amount: ₹{amount:,}
- Status: {status.upper()}
- Risk Score: {risk}/100"""
            )
        except Exception:
            explanation = _fallback_explanation(merchant, amount, status, risk)
    else:
        explanation = _fallback_explanation(merchant, amount, status, risk)

    return jsonify({"explanation": explanation})

def _fallback_explanation(merchant, amount, status, risk):
    if status == "fraud":
        return f"⚠️ This ₹{amount:,} transaction at {merchant} was flagged as FRAUD because the amount significantly exceeds typical safe transaction limits (₹1,00,000+). Risk score: {risk}/100."
    elif status == "warn":
        return f"⚠️ This ₹{amount:,} transaction at {merchant} is SUSPICIOUS as it falls in the medium-high risk range (₹50,000–₹1,00,000). Monitor carefully. Risk score: {risk}/100."
    else:
        return f"✅ This ₹{amount:,} transaction at {merchant} appears SAFE with a low risk score of {risk}/100."

# ─────────────────────────────────────────
# CHATBOT API — Claude Powered (GenAI Feature 3)
# ─────────────────────────────────────────
@app.route("/chat", methods=["POST"])
def chat():
    data    = request.get_json()
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"reply": "Please type a message."})

    # Get user's transaction context
    context = ""
    if "user" in session:
        txs = Transaction.query.filter_by(user=session["user"]).order_by(Transaction.id.desc()).limit(5).all()
        if txs:
            context = "User's recent transactions:\n" + "\n".join(
                f"- {t.merchant} | {t.category} | ₹{t.amount:,} | {t.status.upper()} | risk:{t.risk}"
                for t in txs
            )

    if CLAUDE_API_KEY:
        try:
            system_prompt = f"""You are FraudShield AI — an expert fraud detection assistant for an Indian fintech platform.
You help users understand their transaction risks, fraud patterns, and financial safety.
Be concise, friendly, and professional. Use ₹ for currency. Keep responses under 150 words.
Use bullet points for lists. If asked about specific transactions, refer to the context provided.

{context}"""
            reply = _call_claude(message, system=system_prompt)
        except Exception as e:
            reply = _rule_chat(message)
    else:
        reply = _rule_chat(message)

    return jsonify({"reply": reply})

def _call_claude(prompt, system="You are a helpful AI assistant."):
    """Call Claude API (claude-haiku for speed & cost)"""
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    body = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 400,
        "system": system,
        "messages": [{"role": "user", "content": prompt}]
    }
    resp = requests.post("https://api.anthropic.com/v1/messages",
                         headers=headers, json=body, timeout=15)
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]

def _rule_chat(message):
    """Fallback rule-based chatbot when no API key"""
    msg = message.lower()
    if any(w in msg for w in ["hi","hello","hey"]):
        return "👋 Hello! I'm FraudShield AI. Ask me about fraud detection, risk scores, or your transactions!"
    if any(w in msg for w in ["risk","score"]):
        return "⚡ **Risk Scores:**\n• 0–39 → ✅ Safe\n• 40–79 → ⚠️ Suspicious\n• 80–100 → 🚨 Fraud\n\nHigher amount = higher risk."
    if any(w in msg for w in ["fraud","detect"]):
        return "🔍 Our AI analyzes merchant, category & amount to detect fraud in real-time using ML models trained on transaction patterns."
    if any(w in msg for w in ["safe","protect","tip"]):
        return "🛡️ **Safety Tips:**\n• Never share OTP\n• Avoid large unknown transactions\n• Enable transaction alerts\n• Check statements regularly"
    return "🤔 I can help with fraud detection, risk scores, and transaction safety. Try asking: 'How is risk score calculated?'"

# ─────────────────────────────────────────
# PREDICT (for detect.html compatibility)
# ─────────────────────────────────────────
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    features = data.get("features", [])
    try:
        amount = features[-1] if features else 0
        status, risk = _rule_based(float(amount))
        result = "Fraud Transaction" if status == "fraud" else "Normal Transaction"
        return jsonify({"result": result, "risk": risk})
    except Exception as e:
        return jsonify({"result": "Error", "error": str(e)})

# ─────────────────────────────────────────
# HISTORY PAGE
# ─────────────────────────────────────────
@app.route("/history")
def history():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("history.html")

# ─────────────────────────────────────────
# RUN
# ─────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
