import os
from datetime import datetime
from backend.agents.processor import Processor
from flask import Flask, render_template, request, redirect, url_for, flash, current_app, jsonify
from frontend.scripts.forms import LoginForm
from frontend.scripts.dbmodels import SessionLocal, User
from backend.llm import call_ai
import re
from backend.prompts import PromptBuilder
import json
from backend.agents.current_agent import CurrentAgent

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # this will be `.../frontend/scripts`

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "..", "templates"),
    static_folder=os.path.join(BASE_DIR, "..", "static")
)
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

agent = CurrentAgent()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # where to redirect if not logged in
app.secret_key = "NYZIqkyBr9fOHmPK9H3RgKe82UkdgV22hPYCA6q5kbYW9uuUFGgiAy7rz9dfWosB"


processor = Processor("gemini")
builder = PromptBuilder()
ai = call_ai()
#
# class WorldweaverRoutes():
#     def __init__(self, llm:call_ai):
#         self.llm = llm
# User Loader ________________________________
# @app.teardown_appcontext
# def shutdown_session(exception=None):
#     SessionLocal.remove()
def parse_string(input_str: str) -> str:
    # Extract contents between tags using regex
    message_match = re.search(r"<message>(.*?)</message>", input_str, re.DOTALL)
    document_match = re.search(r"<document>(.*?)</document>", input_str, re.DOTALL)
    message_content = message_match.group(1).strip() if message_match else None
    document_content = None

    if document_match:
        raw_doc = document_match.group(1).strip()
        try:
            # Try to parse as JSON
            document_content = json.loads(raw_doc)
        except json.JSONDecodeError:
            # Fallback: keep as plain string if invalid JSON
            document_content = raw_doc
    if message_content and document_content:
        result = {
            "type": "both",
            "text": message_content,
            "document": document_content
        }
    elif message_content:
        result = {
            "type": "message",
            "text": message_content
        }
    elif document_content:
        result = {
            "type": "document",
            "document": document_content
        }
    else:
        result = {
            "type": "message",
            "text": input_str
        }

    return json.dumps(result, indent=2)


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

@app.route("/planning", methods=["GET", "POST"])
@login_required
def planning():
    build_path = os.path.join(current_app.static_folder, "planning-dist", "assets")
    files = os.listdir(build_path)

    css_file = next((f for f in files if re.match(r'^index-.*\.css$', f)), None)
    js_file = next((f for f in files if re.match(r'^index-.*\.js$', f)), None)
    if os.environ.get("DEV_MODE") == "1":
        return redirect("http://localhost:5173")
    if request.method == "POST":
        user_text = request.form.get("text")
        print(f"The user's text: {user_text}")
    return render_template("pages/planning.html", css_file=css_file, js_file=js_file)

@app.route("/test", methods=["GET", "POST"])
def test():
    if request.method == "POST":
        data = request.get_json()
        user_text = data.get('text', '')
        timestamp = data.get('timestamp', '')

        print(f"The user's text (/test version): {user_text}, at timestamp: {timestamp}")
        return jsonify({
            'status': 'success',
            'received_text': user_text,
            'message': 'Message received successfully'
        })

@app.route('/set_agent', methods=["GET", "POST"])
@login_required
def set_agent():
    if request.method == "POST":
        new_agent = request.form.get("agent")
        agent.set_agent(int(new_agent))
        print(f"New agent set to {agent.get_agent()}")
        return redirect(request.referrer or '/pages/dashboard.html')

@app.route('/advance_agent', methods=["GET", "POST"])
@login_required
def advance_agent():
    if request.method == "POST":
        agent.advance_agent()
        print(f"New agent set to {agent.get_agent()}")
        return redirect(request.referrer or '/pages/dashboard.html')

@app.route('/back_agent', methods=["GET", "POST"])
@login_required
def back_agent():
    if request.method == "POST":
        agent.back_agent()
        print(f"New agent set to {agent.get_agent()}")
        return redirect(request.referrer or '/pages/dashboard.html')


@app.route('/partials/planner/doc')
def partial_doc():
    return render_template('partials/planner/doc.html')

@app.route('/partials/planner/llm')
def partial_llm():
    return render_template('partials/planner/llm.html')


@app.route('/prune', methods=["POST"])
@login_required
def prune():
    if request.method == "POST":
        data = request.get_json()
        print(f"Pruning: {data}")
        json_output = {
            "type": "context",
            "text": "A pruned context..."
        }
        return jsonify(json_output)

@app.route('/tutorial', methods=["POST"])
@login_required
def tutorial():
    if request.method == "POST":
        data = request.get_json()
        stage = data.get('stage', '')
        int_stage = int(stage)
        chat_context = data.get('chat_context', '')
        document_context = data.get('doc_context', '')
        if current_app.config.get("STUB", False):
            json_output = {
                "type": "message",
                "text": "A tutorial for stage {stage}.".format(stage=stage)
            }
            return jsonify(json_output)
        else:
            try:
                raw_output = processor.get_tutorial_response(int_stage, chat_context, document_context)
                json_output = {
                    "type": "message",
                    "text": raw_output
                }
                return jsonify(json_output)
            except Exception as e:
                # Handle any other errors
                error_response = {
                    "type": "message",
                    "text": f"Sorry, I encountered an error with your introduction: {str(e)}"
                }
                return jsonify(error_response)

@app.route('/llm', methods=["GET", "POST"])
@login_required
def llm():
    if request.method == "POST":
        data = request.get_json()
        user_text = data.get('text', '')
        # print(f"The user's text: {user_text}")
        document = data.get('document', '')
        # print(f"The document's text: {document}")
        chat_history = data.get('chat_history', '')
        # print(f"The chat history's text: {chat_history}")
        stage = agent.get_agent()
        frontend_stage = int(data.get('stage', ''))
        # print(f"Frontend stage: {frontend_stage}")
        if current_app.config.get("STUB", False):
            output = ai.get_stub(user_text)
            if output.startswith("<"):
                output = parse_string(output)
            elif output == "failed":
                return "error"
            return output


        else:
            try:
                # Get the raw response from your LLM
                print("Attempting llm call:")
                raw_output = processor.get_llm_response(frontend_stage, user_text, chat_history, document)
                print(f"----------------------------\nThe llm output:\n{raw_output}\n----------------------------")
                # Try to parse the response as JSON first
                try:
                    parsed_output = json.loads(raw_output)

                    # Validate that it has the expected structure
                    if isinstance(parsed_output, dict) and 'type' in parsed_output:
                        # It's already properly formatted JSON
                        return jsonify(parsed_output)
                    else:
                        # It's JSON but not in our expected format
                        # Treat it as a message
                        json_output = {
                            "type": "message",
                            "text": raw_output
                        }
                        return jsonify(json_output)

                except json.JSONDecodeError:
                    # The LLM returned plain text, not JSON
                    # Wrap it in our message format
                    json_output = parse_string(raw_output)
                    print(f"Recieved: {json_output}")
                    # print(f"Returning:\n{json_output}")
                    return json_output

            except Exception as e:
                # Handle any other errors
                error_response = {
                    "type": "message",
                    "text": f"Sorry, I encountered an error: {str(e)}"
                }
                return jsonify(error_response)
        #
        # return json
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

