from backend.scripts.routes import app
from backend.scripts.dbmodels import SessionLocal, User
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
        print("Test user created: test@example.com / password123")
    else:
        print(" * Test user already exists")

    session.close()

if __name__ == "__main__":
    try:
        print("Starting WorldWeaver application...")
        create_test_user()
        
        parser = argparse.ArgumentParser()
        parser.add_argument("--stub", action="store_true", help="Enable stub mode")
        args = parser.parse_args()

        # put the stub flag into Flask's config
        app.config["STUB"] = args.stub
        print(f" * Stub mode: {args.stub}")

        import os
        port = int(os.environ.get("PORT", 5002))
        print(f" * Starting server on 0.0.0.0:{port}")
        print(f" * DEV_MODE: {os.environ.get('DEV_MODE', 'not set')}")
        
        app.run(host="0.0.0.0", port=port, debug=False)
    except Exception as e:
        print(f"ERROR: Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
