from app.db.session import SessionLocal, engine
from app.models.user import User
from app.core.security import get_password_hash, create_access_token
from app.db.base_class import Base

def test_login_logic():
    print("Testing login logic...")
    db = SessionLocal()
    try:
        # Check if tables exist
        print("Ensuring tables exist...")
        Base.metadata.create_all(bind=engine)
        
        email = "xxx"
        password = "xxx"
        
        print(f"Checking for user {email}...")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print("Creating test user...")
            user = User(
                email=email,
                hashed_password=get_password_hash(password),
                full_name="Test User",
                is_active=True,
                is_superuser=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print("User created successfully.")
        else:
            print("User already exists.")
            
        print("Creating access token...")
        access_token = create_access_token(data={"sub": user.email, "role": "admin"})
        print(f"Access token: {access_token[:20]}...")
        
        print("Success!")
    except Exception as e:
        print(f"FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_login_logic()
