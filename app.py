from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
import sqlite3
from datetime import datetime
from database import init_db, register_user, login_user, add_expense, get_expenses
from export import export_to_pdf, export_to_excel, email_pdf
from database import (
    register_user,
    login_user,
    add_expense,
    get_expenses,
    get_monthly_limit,   # ✅ required
    set_monthly_limit    # ✅ if you use /set_limit route
)

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for session management

# Initialize database
init_db()

@app.route("/")
def home():
    return redirect("/login")
@app.route("/register")
def register():
    return render_template("register.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        if len(password) < 8:
            flash("Password must be at least 8 characters", "error")
            return redirect("/register")
        if register_user(name, email, password):
            flash("Registered successfully! Please login.", "success")
            return redirect("/login")
        else:
            flash("Email already registered", "error")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = login_user(email, password)
        if user:
            session["username"] = user[0]
            session["name"] = user[1]
            return redirect("/dashboard")
        else:
            flash("Invalid credentials", "error")
    return render_template("login.html")



@app.route("/add_expense", methods=["POST"])
def add_expense_route():
    if "username" not in session:
        return redirect("/login")

    category = request.form.get("category")
    amount = request.form.get("amount")
    description = request.form.get("description")

    if not category or not amount or not description:
        return "Invalid input", 400

    try:
        amount = int(amount)
    except ValueError:
        return "Amount must be a number", 400

    add_expense(session["username"], category, amount, description)
    
    # ✅ This is the missing return
    return redirect("/dashboard")



@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/login")
    expenses = get_expenses(session["username"])
    limit = get_monthly_limit(session["username"])
    total = sum([e[1] for e in expenses])
    return render_template("dashboard.html", name=session["name"], expenses=expenses, limit=limit, total=total)

@app.route("/export/pdf")
def export_pdf_route():
    if "username" not in session:
        return redirect("/login")
    export_to_pdf(session["username"])
    return send_file("expense_report.pdf", as_attachment=True)

@app.route("/export/excel")
def export_excel_route():
    if "username" not in session:
        return redirect("/login")
    export_to_excel(session["username"])
    return send_file("expense_report.xlsx", as_attachment=True)

@app.route("/email_report")
def email_report():
    if "username" not in session:
        return redirect("/login")
    # For demo: Replace with actual values or prompt user later
    sender = "youremail@gmail.com"
    receiver = "youremail@gmail.com"
    password = "your_app_password"
    export_to_pdf(session["username"])
    try:
        email_pdf(receiver, sender, password)
        flash("Email sent successfully!", "success")
    except Exception as e:
        flash(f"Failed to send email: {e}", "error")
    return redirect("/dashboard")
@app.route("/set_limit", methods=["POST"])
def set_limit():
    if "username" not in session:
        return redirect("/login")
    try:
        limit = int(request.form["limit"])
        set_monthly_limit(session["username"], limit)
        flash("Monthly limit updated!", "success")
    except:
        flash("Enter a valid number", "error")
    return redirect("/dashboard")
@app.route('/charts')
def charts():
    username = session['username']
    expenses = get_expenses(username)

    category_totals = {}
    for category, amount, desc, date in expenses:
        category_totals[category] = category_totals.get(category, 0) + int(amount)

    categories = list(category_totals.keys())
    amounts = list(category_totals.values())

    return render_template('charts.html', categories=categories, amounts=amounts)




@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
