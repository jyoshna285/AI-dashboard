from flask import Flask, render_template, request
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# Function to get applied jobs based on filters
def get_applied_jobs(status_filter=None, start_date=None, end_date=None, search_query=None):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS applications (id INTEGER PRIMARY KEY, title TEXT, company TEXT, status TEXT, applied_on TEXT, ats_score INTEGER, resume_version TEXT)")

    query = "SELECT title, company, status, applied_on, ats_score, resume_version FROM applications WHERE 1=1"
    params = []

    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)

    if start_date and end_date:
        query += " AND applied_on BETWEEN ? AND ?"
        params.append(start_date)
        params.append(end_date)

    if search_query:
        query += " AND (title LIKE ? OR company LIKE ?)"
        params.append(f"%{search_query}%")
        params.append(f"%{search_query}%")
        
    query += " ORDER BY applied_on DESC"

    cursor.execute(query, params)
    jobs = cursor.fetchall()
    conn.close()
    return jobs

# Route for the dashboard
@app.route("/", methods=["GET", "POST"])
def dashboard():
    # Get filters from the form
    status_filter = request.form.get("status") if request.method == "POST" else None
    search_query = request.form.get("search") if request.method == "POST" else None

    # Date range filter (this week/month)
    today = datetime.today()
    start_date = None
    end_date = None
    if request.method == "POST":
        if request.form.get("date_range") == "this_week":
            start_date = today - timedelta(days=today.weekday())  # Monday of the current week
            end_date = start_date + timedelta(days=6)
        elif request.form.get("date_range") == "this_month":
            start_date = today.replace(day=1)
            end_date = today.replace(day=28) + timedelta(days=4)  # to get the last day of the month

    # Get jobs based on filters
    jobs = get_applied_jobs(status_filter, start_date, end_date, search_query)

    return render_template("dashboard.html", jobs=jobs, today=today)

if __name__ == "__main__":
    app.run(debug=True)
