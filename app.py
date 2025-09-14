from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecret"
UPLOAD_FOLDER = "photos/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- DB Setup ---
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS posts(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT,
                    category TEXT,
                    content TEXT,
                    images TEXT)""")
    conn.commit()
    conn.close()

init_db()

# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return "Invalid login"
    return render_template("index.html")

@app.route("/signup", methods=["POST"])
def signup():
    username = request.form["username"]
    password = request.form["password"]
    try:
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("INSERT INTO users(username, password) VALUES(?,?)", (username, password))
        conn.commit()
        conn.close()
        return redirect(url_for("login"))
    except:
        return "User already exists!"

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("main.html")

@app.route("/blog/<category>", methods=["GET", "POST"])
def blog(category):
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        # New post
        content = request.form["content"]
        files = request.files.getlist("images")
        filenames = []
        for file in files:
            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                filenames.append(filename)

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("INSERT INTO posts(user, category, content, images) VALUES(?,?,?,?)",
                  (session["user"], category, content, ",".join(filenames)))
        conn.commit()
        conn.close()

    # Fetch posts
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM posts WHERE category=? ORDER BY id DESC", (category,))
    posts = c.fetchall()
    conn.close()

    # Map category to template
    template_map = {
        "food": "food.html",
        "fashion": "fashion.html",
        "travel": "travel.html"
    }
    template_name = template_map.get(category.lower(), "blog.html")

    return render_template(template_name, posts=posts, category=category)

@app.route("/delete/<int:post_id>/<category>")
def delete_post(post_id, category):
    if "user" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("DELETE FROM posts WHERE id=? AND user=?", (post_id, session["user"]))
    conn.commit()
    conn.close()
    return redirect(url_for("blog", category=category))

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
