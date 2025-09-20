from flask import Flask
from backend.utils.logging_config import get_module_logger

app = Flask(__name__)

# Get logger for iso_test module
logger = get_module_logger('iso_test')

@app.route('/')
def hello():
    return "Hello World! This is a basic Flask test."

@app.route('/test')
def test():
    return "Test page works!"

if __name__ == "__main__":
    logger.info("Starting basic Flask test...")
    app.run(debug=True, host='127.0.0.1', port=5000)