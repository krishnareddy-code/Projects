# app.py
# A simple Flask app demonstrating login flow with a MySQL backend.

import os
import time
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
from werkzeug.security import check_password_hash

# 1. Create the Flask app
app = Flask(__name__)

# Secret key is needed to use session (stores logged-in username).
# In production, set this via environment variable. NEVER hard-code secrets.
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

# 2. Database configuration (read from environment variables)
# This is critical for Docker; the app shouldn't hard-code the DB host.
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 3306)),
    "user": os.environ.get("DB_USER", "appuser"),
    "password": os.environ.get("DB_PASSWORD", "apppassword"),
    "database": os.environ.get("DB_NAME", "trainingdb")
}

def get_db_connection(retries: int = 10, delay: int = 3):
    """
    Connect to MySQL. Retries because when running under Docker Compose, 
    the DB container may not be ready the moment the app container starts.
    """
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            if conn.is_connected():
                return conn
        except Error as e:
            last_error = e
            print(f"(DB) attempt {attempt}/{retries} failed: {e}")
            time.sleep(delay)
    raise RuntimeError(f"Could not connect to MySQL after {retries} tries: {last_error}")

@app.route("/")
def index():
    """Show the login page."""
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    """Handle login form submission."""
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        flash("Please enter both username and password.", "error")
        return redirect(url_for("index"))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Note: MySQL uses %s as its placeholder syntax
        cursor.execute(
            "SELECT username, password_hash FROM users WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for("index"))

    # Verify password using hashed comparison (secure)
    if user and check_password_hash(user["password_hash"], password):
        session["username"] = user["username"]
        return redirect(url_for("welcome"))

    flash("Invalid username or password.", "error")
    return redirect(url_for("index"))

@app.route("/welcome")
def welcome():
    """Show the welcome page only if user is logged in."""
    if "username" not in session:
        return redirect(url_for("index"))
    return render_template("welcome.html", username=session["username"])

@app.route("/logout")
def logout():
    """Clear session and return to login page."""
    session.clear()
    return redirect(url_for("index"))


# this is for user registration for testing purposes only. In production, you would not expose this endpoint.
from werkzeug.security import generate_password_hash

@app.route("/register", methods=["GET", "POST"])
def register():
    """Endpoint to test adding a new user."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return redirect(url_for("register"))

        try:
            # Generate a modern secure hash automatically in your local system environment
            hashed_password = generate_password_hash(password)
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, hashed_password)
            )
            conn.commit()
            cursor.close()
            conn.close()
            
            flash("User created successfully! You can now log in.", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Error creating user: {e}", "error")
            return redirect(url_for("register"))

    return '''
    <div style="font-family:sans-serif; max-width:300px; margin:50px auto; padding:20px; border:1px solid #ddd; border-radius:8px;">
        <h2>Create Test User</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required style="width:100%; margin-bottom:10px; padding:8px;"><br>
            <input type="password" name="password" placeholder="Password" required style="width:100%; margin-bottom:10px; padding:8px;"><br>
            <button type="submit" style="width:100%; padding:10px; background:#2ecc71; color:white; border:none; border-radius:4px; cursor:pointer;">Register</button>
        </form>
    </div>
    '''


# --- ADDED HEALTH CHECK ROUTE HERE ---
@app.route("/health")
def health():
    """Health check endpoint for Docker."""
    return {"status": "healthy"}, 200

# 4. Entry point
if __name__ == "__main__":
    # host="0.0.0.0" is REQUIRED inside Docker so the container accepts
    # connections from outside. 127.0.0.1 would only work inside the container.
    app.run(host="0.0.0.0", port=5000, debug=True)
