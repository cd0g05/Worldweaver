from backend.scripts.routes import app
from backend.scripts.dbmodels import SessionLocal, User
from backend.utils.logging_config import get_logger
import argparse
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get logger for main application (this also initializes the logging system)
logger = get_logger('main')

# Log startup environment info
logger.info("=== WorldWeaver Application Starting ===")
logger.info(f"Environment variables: DEV_MODE={os.environ.get('DEV_MODE', 'not set')}, DEPLOYED={os.environ.get('DEPLOYED', 'not set')}")
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")

def create_test_user():
    session = SessionLocal()

    # Check if user already exists
    existing_user = session.query(User).filter_by(email="t@t.t").first()
    if not existing_user:
        test_user = User(
            name="Test User",
            email="t@t.t",
            password="pwd"  # In production, hash this!
        )
        session.add(test_user)
        session.commit()
        logger.info("Test user created: t@t.t / pwd")
    else:
        logger.info("Test user already exists")

    session.close()

if __name__ == "__main__":
    try:
        logger.info("Starting WorldWeaver application...")
        create_test_user()
        
        parser = argparse.ArgumentParser()
        parser.add_argument("--stub", action="store_true", help="Enable stub mode")
        args = parser.parse_args()

        # put the stub flag into Flask's config
        app.config["STUB"] = args.stub
        logger.info(f"Stub mode: {args.stub}")

        import os
        port = int(os.environ.get("PORT", 5002))
        logger.info(f"Starting server on 0.0.0.0:{port}")
        logger.info(f"DEV_MODE: {os.environ.get('DEV_MODE', 'not set')}")
        
        app.run(host="0.0.0.0", port=port, debug=False)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
