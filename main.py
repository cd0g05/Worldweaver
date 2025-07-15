from frontend.scripts.routes import app
from frontend.scripts.dbmodels import SessionLocal, User

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
        print("Test user already exists")

    session.close()

if __name__ == "__main__":
    create_test_user()
    app.run(debug=True)