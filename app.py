
from flask import Flask, request, redirect, render_template_string
import sqlite3
import os

app = Flask(__name__)

# ---------- DATABASE ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "jobs.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- HTML (INLINE) ----------
PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Job Application Tracker</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f0f2f5;
        }
        .container {
            width: 420px;
            margin: 40px auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
        }
        input, select, button {
            width: 100%;
            padding: 10px;
            margin: 8px 0;
        }
        button {
            background: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
        }
        .job {
            background: #eee;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .delete {
            color: red;
            text-decoration: none;
            margin-left: 10px;
        }
    </style>
</head>
<body>

<div class="container">
    <h2>Job Application Tracker</h2>

    <form method="POST">
        <input name="company" placeholder="Company Name" required>
        <input name="role" placeholder="Job Role" required>

        <select name="status" required>
            <option value="">Select Status</option>
            <option>Applied</option>
            <option>Interview</option>
            <option>Rejected</option>
            <option>Offer</option>
        </select>

        <button>Add Job</button>
    </form>

    <h3>My Applications</h3>

    {% for job in jobs %}
    <div class="job">
        <b>{{ job.company }}</b> — {{ job.role }}

        <form method="POST" action="/update/{{ job.id }}">
            <select name="status">
                <option value="Applied" {% if job.status=='Applied' %}selected{% endif %}>Applied</option>
                <option value="Interview" {% if job.status=='Interview' %}selected{% endif %}>Interview</option>
                <option value="Rejected" {% if job.status=='Rejected' %}selected{% endif %}>Rejected</option>
                <option value="Offer" {% if job.status=='Offer' %}selected{% endif %}>Offer</option>
            </select>
            <button>Update</button>
        </form>

        <a class="delete" href="/delete/{{ job.id }}">Delete</a>
    </div>
    {% else %}
        <p>No jobs added yet.</p>
    {% endfor %}
</div>

</body>
</html>
"""

# ---------- ROUTES ----------
@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db()

    if request.method == "POST":
        conn.execute(
            "INSERT INTO jobs (company, role, status) VALUES (?, ?, ?)",
            (request.form["company"], request.form["role"], request.form["status"])
        )
        conn.commit()
        conn.close()
        return redirect("/")

    jobs = conn.execute("SELECT * FROM jobs").fetchall()
    conn.close()
    return render_template_string(PAGE, jobs=jobs)

@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM jobs WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    conn = get_db()
    conn.execute(
        "UPDATE jobs SET status=? WHERE id=?",
        (request.form["status"], id)
    )
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    app.run()
