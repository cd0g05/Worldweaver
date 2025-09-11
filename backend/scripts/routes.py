import os
from datetime import datetime
from backend.agents.processor import Processor
from flask import Flask, render_template, request, redirect, url_for, flash, current_app, jsonify, session
from backend.scripts.forms import LoginForm
from backend.scripts.dbmodels import SessionLocal, User
from backend.scripts.llm import call_ai
import re
from backend.scripts.prompts import PromptBuilder
import json
from backend.agents.current_agent import CurrentAgent
from backend.utils.conversation_logger import conversation_logger
from pathlib import Path

PROJ = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = PROJ / "frontend" / "templates"
STATIC_DIR = PROJ / "frontend" / "static"

app = Flask(
    __name__,
    template_folder=str(TEMPLATES_DIR),
    static_folder=str(STATIC_DIR),        # where Flask will serve /static from
    static_url_path="/static",
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

# Conversation Session Management ________________________________

def start_new_conversation_session():
    """
    Always create a new conversation session and log file for the current user.
    This will be called every time the user visits /planning.
    """
    if current_user.is_authenticated:
        # End any existing session first
        session_key = f"conversation_session_{current_user.id}"
        if session_key in session:
            conversation_logger.log_session_end()
            
        # Always start a new conversation session
        username = current_user.email.split('@')[0]  # Use email prefix as username
        log_file = conversation_logger.start_new_conversation(username)
        session[session_key] = {
            'log_file': log_file,
            'start_time': datetime.now().isoformat()
        }
        print(f"Started new conversation session for {username}: {log_file}")
        
        return session[session_key]
    return None

def ensure_conversation_session():
    """
    Ensure that a conversation session is active for the current user.
    This is used by /llm and /tutorial routes to make sure logging is active.
    """
    if current_user.is_authenticated:
        session_key = f"conversation_session_{current_user.id}"
        
        # Check if we already have an active conversation session
        if session_key not in session:
            # This shouldn't happen if user came through /planning, but create one just in case
            username = current_user.email.split('@')[0]
            log_file = conversation_logger.start_new_conversation(username)
            session[session_key] = {
                'log_file': log_file,
                'start_time': datetime.now().isoformat()
            }
            print(f"Created fallback conversation session for {username}: {log_file}")
        
        return session[session_key]
    return None

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
    try:
        if current_user.is_authenticated:
            return render_template("pages/dashboard.html")
        else:
            return render_template("pages/welcome.html", now=datetime.utcnow)
    except Exception as e:
        # Fallback for health checks or missing templates
        return f"WorldWeaver is running! Error: {str(e)}", 200

@app.route('/health')
def health():
    return {"status": "healthy", "service": "worldweaver"}, 200

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
    # Always create a new conversation session and log file
    start_new_conversation_session()
    
    build_path = os.path.join(current_app.static_folder, "planning-dist", "assets")
    files = os.listdir(build_path)

    css_file = next((f for f in files if re.match(r'^index-.*\.css$', f)), None)
    js_file = next((f for f in files if re.match(r'^index-.*\.js$', f)), None)
    # if os.environ.get("DEV_MODE") == "1":
    #     return redirect("http://localhost:5173")
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
        # Ensure conversation session is active
        ensure_conversation_session()
        
        data = request.get_json()
        stage = data.get('stage', '')
        int_stage = int(stage)
        chat_context = data.get('chat_context', '')
        document_context = data.get('doc_context', '')
        
        # Log the incoming tutorial request
        conversation_logger.log_tutorial_request(
            stage=int_stage,
            chat_context=chat_context,
            document_context=document_context
        )
        
        if current_app.config.get("STUB", False):
            json_output = {
                "type": "message",
                "text": "A tutorial for stage {stage}.".format(stage=stage)
            }
            stub_metadata = {"model": "stub", "prompt_name": f"tutorial_stage_{stage}", "stage": int_stage}
            conversation_logger.log_tutorial_response(
                raw_output=f"STUB: A tutorial for stage {stage}.",
                processed_output=json_output,
                metadata=stub_metadata
            )
            return jsonify(json_output)
        else:
            try:
                processor_result = processor.get_tutorial_response(int_stage, chat_context, document_context)
                
                # Handle both old format (string) and new format (tuple)
                if isinstance(processor_result, tuple):
                    raw_output, metadata = processor_result
                else:
                    raw_output = processor_result
                    metadata = {"model": "unknown", "prompt_name": f"tutorial_stage_{int_stage}", "stage": int_stage}
                
                json_output = {
                    "type": "message",
                    "text": raw_output
                }
                
                # Log the tutorial response
                conversation_logger.log_tutorial_response(
                    raw_output=raw_output,
                    processed_output=json_output,
                    metadata=metadata
                )
                
                return jsonify(json_output)
            except Exception as e:
                # Handle any other errors
                error_response = {
                    "type": "message",
                    "text": f"Sorry, I encountered an error with your introduction: {str(e)}"
                }
                
                # Log the error
                conversation_logger.log_error(
                    error_type="TUTORIAL_ERROR",
                    error_message=str(e),
                    context={
                        "stage": int_stage,
                        "chat_context": chat_context,
                        "document_context": document_context
                    }
                )
                
                conversation_logger.log_tutorial_response(
                    raw_output="ERROR_OCCURRED",
                    processed_output=error_response,
                    metadata={"stage": int_stage}
                )
                
                return jsonify(error_response)

@app.route('/llm', methods=["GET", "POST"])
@login_required
def llm():
    if request.method == "POST":
        # Ensure conversation session is active
        ensure_conversation_session()
        
        data = request.get_json()
        user_text = data.get('text', '')
        document = data.get('document', '')
        chat_history = data.get('chat_history', '')
        # stage = agent.get_agent()
        frontend_stage = int(data.get('stage', ''))
        
        # Log the incoming LLM request
        conversation_logger.log_llm_request(
            user_message=user_text,
            chat_history=chat_history,
            document_context=document,
            frontend_stage=frontend_stage
        )
        
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
                conversation_logger.log_message("Attempting llm call...")
                processor_result = processor.get_llm_response(frontend_stage, user_text, chat_history, document)
                
                # Handle both old format (string) and new format (tuple)
                if isinstance(processor_result, tuple):
                    raw_output, metadata = processor_result
                else:
                    raw_output = processor_result
                    metadata = {"model": "unknown", "prompt_name": "unknown", "stage": frontend_stage}

                # Try to parse the response as JSON first
                try:
                    parsed_output = json.loads(raw_output)

                    # Validate that it has the expected structure
                    if isinstance(parsed_output, dict) and 'type' in parsed_output:
                        # It's already properly formatted JSON
                        conversation_logger.log_llm_response(
                            raw_output=raw_output,
                            processed_output=parsed_output,
                            processing_type="json_direct",
                            metadata=metadata
                        )
                        return jsonify(parsed_output)
                    else:
                        # It's JSON but not in our expected format
                        # Treat it as a message
                        json_output = {
                            "type": "message",
                            "text": raw_output
                        }
                        conversation_logger.log_llm_response(
                            raw_output=raw_output,
                            processed_output=json_output,
                            processing_type="json_wrapped",
                            metadata=metadata
                        )
                        return jsonify(json_output)

                except json.JSONDecodeError:
                    # The LLM returned plain text, not JSON
                    # Wrap it in our message format
                    json_output_str = parse_string(raw_output)
                    try:
                        json_output = json.loads(json_output_str)
                        conversation_logger.log_llm_response(
                            raw_output=raw_output,
                            processed_output=json_output,
                            processing_type="string_parsed",
                            metadata=metadata
                        )
                        print(f"Recieved: {json_output_str}")
                        return json_output_str
                    except json.JSONDecodeError as parse_error:
                        # Fallback to basic message format
                        fallback_output = {
                            "type": "message",
                            "text": raw_output
                        }
                        conversation_logger.log_llm_response(
                            raw_output=raw_output,
                            processed_output=fallback_output,
                            processing_type="fallback",
                            metadata=metadata
                        )
                        conversation_logger.log_error(
                            error_type="JSON_PARSE_ERROR",
                            error_message=str(parse_error),
                            context={"raw_output": raw_output, "parsed_attempt": json_output_str, "metadata": metadata}
                        )
                        return jsonify(fallback_output)

            except Exception as e:
                # Handle any other errors
                error_response = {
                    "type": "message",
                    "text": f"Sorry, I encountered an error: {str(e)}"
                }
                conversation_logger.log_error(
                    error_type="LLM_ERROR",
                    error_message=str(e),
                    context={
                        "user_text": user_text,
                        "frontend_stage": frontend_stage
                    }
                )
                conversation_logger.log_llm_response(
                    raw_output="ERROR_OCCURRED",
                    processed_output=error_response,
                    processing_type="error",
                    metadata={"stage": frontend_stage}
                )
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

