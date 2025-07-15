import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = "NYZIqkyBr9fOHmPK9H3RgKe82UkdgV22hPYCA6q5kbYW9uuUFGgiAy7rz9dfWosB"

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Simple user loader that doesn't require database
@login_manager.user_loader
def load_user(user_id):
    print(f"User loader called with ID: {user_id}")
    return None  # For now, always return None

# Test routes
@app.route('/')
def welcome():
    print("=== WELCOME ROUTE ACCESSED ===")
    print(f"Current user authenticated: {current_user.is_authenticated}")
    return f"""
    <h1>Welcome Page</h1>
    <p>User authenticated: {current_user.is_authenticated}</p>
    <a href='/protected'>Protected Page</a><br>
    <a href='/login'>Login Page</a>
    """

@app.route('/protected')
@login_required
def protected():
    return "<h1>This page requires login</h1>"

@app.route('/login')
def login():
    return "<h1>Login Page (not functional yet)</h1><a href='/'>Back to Welcome</a>"

if __name__ == "__main__":
    print("Starting Flask app with Flask-Login...")
    app.run(debug=True)