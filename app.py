from flask import Flask, render_template, request, redirect, jsonify
import os

app = Flask(__name__)

# --------------------
# HOME ROUTE (IMPORTANT FOR RENDER)
# --------------------
@app.route("/")
def home():
    return redirect("/login")


# --------------------
# LOGIN PAGE
# --------------------
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        if(email == "admin@gmail.com"or  email=="23b61a7202@nmrec.edu.in") and password == "admin123":
            return redirect("/dashboard")

        else:
            return "Invalid Login"

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
# DASHBOARD PAGE
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)