"""
Script to populate historical meal data for testing the monthly goal tracker.
Creates meal logs for the current month with varying completion rates.
"""
import sys
import os
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from app.models.models import User, MealLog
import random


def populate_monthly_data():
    db: Session = SessionLocal()
    
    try:
        # Get first user
        user = db.query(User).first()
        if not user:
            print("❌ No users found. Please create a user first.")
            return
        
        print(f"✅ Found user: {user.email} (ID: {user.id})")
        
        # Get current month start
        now = datetime.now(timezone.utc)
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Macro targets
        TARGETS = {
            "protein": 150,
            "carbs": 250,
            "fats": 60,
        }
        
        # Clear existing meals for this month
        db.query(MealLog).filter(
            MealLog.user_id == user.id,
            MealLog.created_at >= start_of_month
        ).delete()
        db.commit()
        print(f"🗑️  Cleared existing meals for {now.strftime('%B %Y')}")
        
        # Create meals for each day of the month so far
        current_day = start_of_month
        days_created = 0
        completed_days = 0
        
        while current_day <= now:
            # 70% chance of logging meals on a day
            if random.random() < 0.7:
                # Determine if this day will meet goals (60% chance)
                meets_goals = random.random() < 0.6
                
                if meets_goals:
                    # Create meals that meet targets (within ±10%)
                    protein = random.randint(int(TARGETS["protein"] * 0.92), int(TARGETS["protein"] * 1.08))
                    carbs = random.randint(int(TARGETS["carbs"] * 0.92), int(TARGETS["carbs"] * 1.08))
                    fats = random.randint(int(TARGETS["fats"] * 0.92), int(TARGETS["fats"] * 1.08))
                    completed_days += 1
                else:
                    # Create meals that don't meet targets
                    protein = random.randint(50, int(TARGETS["protein"] * 0.7))
                    carbs = random.randint(100, int(TARGETS["carbs"] * 0.7))
                    fats = random.randint(20, int(TARGETS["fats"] * 0.7))
                
                calories = (protein * 4) + (carbs * 4) + (fats * 9)
                
                # Create 2-4 meals throughout the day
                num_meals = random.randint(2, 4)
                for i in range(num_meals):
                    # Distribute macros across meals
                    meal_protein = protein // num_meals + (protein % num_meals if i == 0 else 0)
                    meal_carbs = carbs // num_meals + (carbs % num_meals if i == 0 else 0)
                    meal_fats = fats // num_meals + (fats % num_meals if i == 0 else 0)
                    meal_calories = calories // num_meals + (calories % num_meals if i == 0 else 0)
                    
                    # Random time during the day
                    hour = 7 + (i * 4) + random.randint(0, 2)
                    minute = random.randint(0, 59)
                    meal_time = current_day.replace(hour=hour, minute=minute)
                    
                    meal = MealLog(
                        user_id=user.id,
                        gym_id=user.gym_id,
                        protein=meal_protein,
                        carbs=meal_carbs,
                        fats=meal_fats,
                        calories=meal_calories,
                        description=f"Test meal {i+1}",
                        created_at=meal_time
                    )
                    db.add(meal)
                
                days_created += 1
            
            current_day += timedelta(days=1)
        
        db.commit()
        
        total_days = (now - start_of_month).days + 1
        completion_rate = (completed_days / days_created * 100) if days_created > 0 else 0
        
        print(f"\n✅ Created meal data for {now.strftime('%B %Y')}")
        print(f"📊 Stats:")
        print(f"   - Total days in month so far: {total_days}")
        print(f"   - Days with meals logged: {days_created}")
        print(f"   - Days meeting goals: {completed_days}")
        print(f"   - Completion rate: {completion_rate:.1f}%")
        print(f"\n🎯 You can now test the Monthly Goal Tracker!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    populate_monthly_data()
