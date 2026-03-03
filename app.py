from flask import Flask, render_template, request, redirect, jsonify

app = Flask(__name__)

# --------------------
# LOGIN PAGE (MAIN LINK)
# --------------------
@app.route("/")
@app.route("/login")
def login():
    return render_template("login.html")


# --------------------
# SIGNUP PAGE
# --------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        return redirect("/login")
    return render_template("signup.html")


# --------------------
# DASHBOARD PAGE  (THIS FIXES YOUR ERROR)
# --------------------
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# --------------------
# CHATBOT PAGE
# --------------------
@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")


# --------------------
# CHATBOT API
# --------------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "").lower()

    if "website" in message:
        reply = "This AI-Based Fraud Detection system analyzes transaction patterns to detect suspicious activity."

    elif "fraud" in message:
        reply = "Fraud is detected based on transaction amount thresholds and risk scoring."

    elif "model" in message:
        reply = "The model evaluates risk based on transaction behavior patterns."

    else:
        reply = "Ask me about fraud detection, transactions, or analysis."

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)