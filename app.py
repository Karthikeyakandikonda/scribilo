from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

# Connect to SQLite
def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create users table if it doesn't exist
def create_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

create_table()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        action = request.form.get("action")
        email = request.form.get("email")
        password = request.form.get("password")
        name = request.form.get("name")

        conn = get_db_connection()

        if action == "signup":
            hashed_password = generate_password_hash(password)
            try:
                conn.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                             (name, email, hashed_password))
                conn.commit()
                flash("Signup successful! Please login.", "success")
            except sqlite3.IntegrityError:
                flash("Email already exists!", "error")
            conn.close()
            return redirect(url_for("index"))

        elif action == "login":
            user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            conn.close()
            if user and check_password_hash(user["password"], password):
                # Login successful → redirect to main
                return redirect(url_for("main"))
            else:
                flash("Invalid email or password!", "error")
                return redirect(url_for("index"))

    return render_template("index.html")

# Route for main page after login
@app.route("/main")
def main():
    return render_template("main.html")

if __name__ == "__main__":
    app.run(debug=True)
