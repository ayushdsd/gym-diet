"""
Create a test user for development
Run: python scripts/create_test_user.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.models import User, Gym
from app.core.security import get_password_hash

def create_test_user():
    db: Session = SessionLocal()
    
    try:
        # Check if gym exists, create if not
        gym = db.query(Gym).filter(Gym.name == "Gym A").first()
        if not gym:
            gym = Gym(name="Gym A")
            db.add(gym)
            db.commit()
            db.refresh(gym)
            print(f"✅ Created gym: {gym.name} (ID: {gym.id})")
        else:
            print(f"✅ Gym already exists: {gym.name} (ID: {gym.id})")
        
        # Check if user exists
        test_email = "test@example.com"
        user = db.query(User).filter(User.email == test_email).first()
        
        if user:
            print(f"✅ Test user already exists: {test_email}")
            print(f"   Password: password")
            print(f"   Gym ID: {user.gym_id}")
            print(f"   Total XP: {user.total_xp}")
            print(f"   Streak: {user.current_streak} days")
        else:
            # Create test user
            hashed_password = get_password_hash("password")
            user = User(
                email=test_email,
                hashed_password=hashed_password,
                gym_id=gym.id,
                role="member",
                total_xp=0,
                current_streak=0
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ Created test user:")
            print(f"   Email: {test_email}")
            print(f"   Password: password")
            print(f"   Gym ID: {gym.id}")
        
        print("\n🎉 Setup complete! You can now login with:")
        print(f"   Email: test@example.com")
        print(f"   Password: password")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
