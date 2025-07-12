from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
import sqlite3
import os
from datetime import datetime
from database import (
    init_db,
    register_user,
    login_user,
    add_expense,
    get_expenses,
    get_monthly_limit,
    set_monthly_limit
)
from export import export_to_pdf, export_to_excel

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Initialize database
init_db()

@app.route("/")
def home():
    return redirect("/login")

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

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/login")

    try:
        expenses = get_expenses(session["username"])
        limit = get_monthly_limit(session["username"])
        total = sum([e[1] for e in expenses]) if expenses else 0
        return render_template("dashboard.html", name=session["name"], expenses=expenses, limit=limit, total=total)
    except Exception as e:
        print("Error in dashboard:", e)
        return "Something went wrong in dashboard: " + str(e), 500

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
    return redirect("/dashboard")

@app.route("/export/pdf")
def export_pdf_route():
    if "username" not in session:
        return redirect("/login")
    
    file_path = export_to_pdf(session["username"])
    
    print(f"[DEBUG] PDF File Path: {file_path}")  # ✅ DEBUG LOG

    if not file_path or not os.path.exists(file_path):
        flash("PDF generation failed.", "error")
        return redirect("/dashboard")
    
    return send_file(file_path, as_attachment=True)


@app.route("/export/excel")
def export_excel_route():
    if "username" not in session:
        return redirect("/login")
    
    file_path = export_to_excel(session["username"])
    
    print(f"[DEBUG] Excel File Path: {file_path}")  # ✅ DEBUG LOG

    if not file_path or not os.path.exists(file_path):
        flash("No expenses to export!", "error")
        return redirect("/dashboard")
    
    return send_file(file_path, as_attachment=True)


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
    if "username" not in session:
        return redirect("/login")
    expenses = get_expenses(session["username"])

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
