import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, current_app
from frontend.scripts.forms import LoginForm
from frontend.scripts.dbmodels import SessionLocal, User
from backend.llm import call_ai
import re


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # this will be `.../frontend/scripts`

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "..", "templates"),
    static_folder=os.path.join(BASE_DIR, "..", "static")
)
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # where to redirect if not logged in
app.secret_key = "NYZIqkyBr9fOHmPK9H3RgKe82UkdgV22hPYCA6q5kbYW9uuUFGgiAy7rz9dfWosB"

ai = call_ai()
#
# class WorldweaverRoutes():
#     def __init__(self, llm:call_ai):
#         self.llm = llm
# User Loader ________________________________
# @app.teardown_appcontext
# def shutdown_session(exception=None):
#     SessionLocal.remove()

@login_manager.user_loader
def load_user(user_id):
    session = SessionLocal()
    try:
        user = session.get(User, int(user_id))
        return user
    finally:
        session.close()
# Page Routes ________________________________

@app.route('/')
def welcome():
    if current_user.is_authenticated:
        return render_template("pages/dashboard.html")
    else:
        return render_template("pages/welcome.html", now=datetime.utcnow)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("pages/dashboard.html")

@app.route('/planner')
@login_required
def story_planner():
    return render_template("pages/story_planner.html")

@app.route("/planning")
@login_required
def planning():
    build_path = os.path.join(current_app.static_folder, "planning-dist", "assets")
    files = os.listdir(build_path)

    css_file = next((f for f in files if re.match(r'^index-.*\.css$', f)), None)
    js_file = next((f for f in files if re.match(r'^index-.*\.js$', f)), None)
    if os.environ.get("DEV_MODE") == "1":
        return redirect("http://localhost:5173")
    return render_template("pages/planning.html", css_file=css_file, js_file=js_file)


@app.route('/partials/planner/doc')
def partial_doc():
    return render_template('partials/planner/doc.html')

@app.route('/partials/planner/llm')
def partial_llm():
    return render_template('partials/planner/llm.html')

@app.route('/llm', methods=["GET", "POST"])
@login_required
def llm():
    if request.method == "POST":
        user_text = request.form.get("text")
        print(f"received user text: {user_text}")
        if user_text.startswith("$"):
            output = ai.get_stub(user_text[1:])
            return output

        else:
            prompt = "tbd"
            output = ai.get_response(prompt, user_text)
            json = {"type":"message", "text":output}

        return json
    else:
        return render_template("llm.html")
# Login stuff ________________________________

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    session = SessionLocal()
    form = LoginForm()

    if form.validate_on_submit():  # This handles POST and form validation
        email = form.email.data
        password = form.password.data

        try:
            user = session.query(User).filter_by(email=email).first()

            if user and user.password == password:  # In production, use proper password hashing!
                login_user(user)
                next_page = request.args.get("next")
                return redirect(next_page or url_for('dashboard'))
            else:
                flash("Invalid email or password", "error")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
        finally:
            session.close()

    return render_template("pages/login.html", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")
# Main _______________________________________

app = app

