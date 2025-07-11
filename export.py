import sqlite3
from fpdf import FPDF
import openpyxl
from email.message import EmailMessage
import smtplib

DB_NAME = "users.db"

def export_to_pdf(username):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT category, amount, description, date FROM expenses WHERE username = ?", (username,))
    expenses = c.fetchall()
    conn.close()

    pdf.cell(200, 10, txt=f"Expense Report for {username}", ln=True, align="C")
    pdf.ln(10)

    for category, amount, description, date in expenses:
        line = f"{date} | {category} | Rs.{amount} | {description}"
        pdf.cell(200, 10, txt=line.encode('latin-1', 'replace').decode('latin-1'), ln=True)

    pdf.output("expense_report.pdf")

def export_to_excel(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT category, amount, description, date FROM expenses WHERE username = ?", (username,))
    expenses = c.fetchall()
    conn.close()

    if not expenses:
        return False

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Expenses"
    ws.append(["Date", "Category", "Amount", "Description"])

    for row in expenses:
        ws.append([row[3], row[0], row[1], row[2]])

    wb.save("expense_report.xlsx")
    return True

def email_pdf(to_email, from_email, app_password):
    msg = EmailMessage()
    msg["Subject"] = "Your Monthly Expense Report"
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content("Please find attached your PDF report.")

    with open("expense_report.pdf", "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename="expense_report.pdf")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(from_email, app_password)
        smtp.send_message(msg)
