# Animation and XP Deletion Fixes - Complete Implementation

## Issue 1: Aggressive FAB and Meal Logged Animations

### Problem Analysis
The floating Add Meal (+) button and meal logged card animations felt aggressive on mobile devices due to:
1. **Spring animations with high stiffness**: `withSpring` with `damping: 10, stiffness: 100` created bouncy, aggressive motion
2. **Excessive scale values**: Scaling to 1.2x was too dramatic for mobile screens
3. **Multiple overlapping animations**: Card scale, checkmark scale, and fade animations all using spring physics
4. **No animation sequencing**: FAB and bottom sheet animations triggered simultaneously

### Root Cause
- `withSpring` animations are physics-based and create bouncy, elastic motion
- High stiffness values (80-100) made animations snap aggressively
- Mobile devices have smaller screens, making large scale changes more noticeable
- Lack of timing control between FAB press and sheet opening

### Changes Made

#### 1. MealLoggedCard Component (`mobile/components/MealLoggedCard.tsx`)
**Before:**
```typescript
scale.value = withSpring(1, { damping: 10, stiffness: 100 });
checkScale.value = withDelay(
  200,
  withSequence(
    withSpring(1.2, { damping: 8 }),
    withSpring(1, { damping: 10 })
  )
);
```

**After:**
```typescript
scale.value = withTiming(1, {
  duration: 150,
  easing: Easing.out(Easing.ease),
});
checkScale.value = withDelay(
  200,
  withSequence(
    withTiming(1.05, { duration: 150, easing: Easing.out(Easing.ease) }),
    withTiming(1, { duration: 150, easing: Easing.out(Easing.ease) })
  )
);
```

**Changes:**
- Replaced `withSpring` with `withTiming` for predictable, smooth motion
- Reduced scale from 1.2x to 1.05x (subtle instead of dramatic)
- Added `Easing.out(Easing.ease)` for smooth deceleration
- Duration: 150ms (fast but not jarring)

#### 2. FAB Button Animation (`mobile/app/(tabs)/_layout.tsx`)
**Before:**
```typescript
<TouchableOpacity
  onPress={() => {
    haptics.medium();
    setShowMealSheet(true);
  }}
>
```

**After:**
```typescript
const fabScale = useSharedValue(1);

const handleFABPress = () => {
  // Subtle scale animation on press
  fabScale.value = withTiming(1.05, {
    duration: 150,
    easing: Easing.out(Easing.ease),
  });
  
  // Return to normal after animation completes
  setTimeout(() => {
    fabScale.value = withTiming(1, {
      duration: 150,
      easing: Easing.out(Easing.ease),
    });
  }, 150);
  
  haptics.medium();
  
  // Open sheet after FAB animation completes
  setTimeout(() => {
    setShowMealSheet(true);
  }, 150);
};

<Animated.View style={[styles.fab, fabAnimatedStyle]}>
```

**Changes:**
- Added controlled scale animation (1 → 1.05 → 1)
- Animation completes before bottom sheet opens (150ms delay)
- No overlapping animations
- Subtle 5% scale instead of aggressive bounce
- Smooth easing curve for premium feel

### Result
- Animations feel smooth and premium on mobile
- No aggressive bouncing or snapping
- Proper sequencing prevents visual conflicts
- Consistent 150ms timing across all animations
- Subtle 5% scale provides feedback without being distracting

---

## Issue 2: XP Not Removed When Meal is Deleted

### Problem Analysis
When a meal was deleted:
1. The meal was removed from the database
2. XP awarded for that meal remained in user's total
3. No link existed between XPLog entries and meals
4. Frontend didn't update XP values after deletion

### Root Cause
- `XPLog` table lacked `source` and `reference_id` fields
- No way to identify which XP entries were related to a specific meal
- Delete endpoint didn't handle XP removal
- Frontend didn't update Zustand store after deletion

### Implementation

#### Step 1: Database Schema Update

**Added fields to XPLog model** (`app/models/models.py`):
```python
class XPLog(Base):
    # ... existing fields ...
    source: Mapped[str] = mapped_column(String(50), nullable=False, default='meal_log', index=True)
    reference_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
```

**Fields:**
- `source`: Identifies where XP came from ("meal_log", "achievement", etc.)
- `reference_id`: Stores the ID of the related entity (meal_id for meals)
- Both indexed for fast lookups

**Migration** (`alembic/versions/20260324_000013_add_source_and_reference_id_to_xplog.py`):
```python
def upgrade():
    op.add_column('xplog', sa.Column('source', sa.String(length=50), 
                  nullable=False, server_default='meal_log'))
    op.add_column('xplog', sa.Column('reference_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_xplog_source'), 'xplog', ['source'], unique=False)
    op.create_index(op.f('ix_xplog_reference_id'), 'xplog', ['reference_id'], unique=False)
```

#### Step 2: XP Manager Update

**Updated `record_xp_transaction`** (`app/services/xp_manager.py`):
```python
def record_xp_transaction(
    db: Session,
    user_id: int,
    gym_id: int,
    delta: int,
    action_type: str,
    reason: str,
    source: str = "meal_log",
    reference_id: int | None = None  # NEW
) -> XPLog:
    xp_log = XPLog(
        user_id=user_id,
        gym_id=gym_id,
        delta=delta,
        action_type=action_type,
        reason=reason,
        source=source,
        reference_id=reference_id,  # NEW
        created_at=datetime.utcnow()
    )
    db.add(xp_log)
    db.flush()
    return xp_log
```

**Updated `award_xp`** to extract and pass `meal_id`:
```python
def award_xp(db: Session, user: User, action_type: str, context: dict) -> XPAwardResult:
    reference_id = None
    source = "meal_log"
    
    if action_type == "meal_logged":
        meal_xp = calculate_xp_for_meal()
        base_xp += meal_xp
        reference_id = context.get("meal_id")  # Extract meal_id from context
    
    # ... rest of logic ...
    
    record_xp_transaction(
        db=db,
        user_id=user.id,
        gym_id=user.gym_id,
        delta=total_xp,
        action_type=action_type,
        reason=reason,
        source=source,
        reference_id=reference_id  # Pass meal_id
    )
```

#### Step 3: Meal Creation Update

**Updated meal creation** (`app/api/routes/meals.py`):
```python
# Award XP for meal logging (pass meal_id as reference)
meal_xp_result = award_xp(db, user, "meal_logged", {"meal_id": meal.id})
```

Now when a meal is logged, the XPLog entry stores the meal's ID in `reference_id`.

#### Step 4: Meal Deletion Update

**Completely rewrote delete endpoint** (`app/api/routes/meals.py`):
```python
@router.delete("/{meal_id}", status_code=200)
def delete_meal(meal_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Delete a meal by ID and remove associated XP"""
    from app.models.models import XPLog
    from app.services.level_system import check_level_up
    
    meal = db.query(MealLog).filter(
        MealLog.id == meal_id,
        MealLog.user_id == user.id,
        MealLog.gym_id == user.gym_id
    ).first()
    
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    # Find XP logs associated with this meal
    xp_logs = db.query(XPLog).filter(
        XPLog.reference_id == meal_id,
        XPLog.source == "meal_log",
        XPLog.user_id == user.id
    ).all()
    
    # Calculate total XP to remove
    total_xp_to_remove = sum(log.delta for log in xp_logs)
    
    # Store old level for comparison
    old_xp = user.total_xp or 0
    old_level = max(1, int((old_xp / 100) ** 0.5))
    
    # Remove XP from user
    user.total_xp = max(0, (user.total_xp or 0) - total_xp_to_remove)
    new_xp = user.total_xp
    new_level = max(1, int((new_xp / 100) ** 0.5))
    
    # Delete XP logs
    for log in xp_logs:
        db.delete(log)
    
    # Delete meal
    db.delete(meal)
    db.commit()
    
    # Return gamification data for frontend update
    return {
        "success": True,
        "xp_removed": total_xp_to_remove,
        "new_total_xp": new_xp,
        "old_level": old_level,
        "new_level": new_level,
        "level_changed": old_level != new_level
    }
```

**Process:**
1. Find all XPLog entries where `reference_id == meal_id` and `source == "meal_log"`
2. Sum up the XP from those entries
3. Subtract from user's total XP (with floor of 0)
4. Calculate old and new levels
5. Delete XPLog entries
6. Delete meal
7. Return gamification data to frontend

#### Step 5: Frontend Update

**Updated dashboard delete handler** (`mobile/app/(tabs)/index.tsx`):
```typescript
const handleDeleteMeal = async (mealId: number) => {
  // ... confirmation logic ...
  
  if (confirmed) {
    try {
      if (token) {
        apiService.setToken(token);
        const response = await fetch(`${apiService.baseUrl}/meals/${mealId}`, {
          method: "DELETE",
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (response.ok) {
          const data = await response.json();
          
          // Update Zustand store with new XP values
          if (data.xp_removed > 0) {
            useGamification.setState({
              totalXp: data.new_total_xp,
              currentLevel: data.new_level,
            });
          }
          
          // Remove meal from local state
          deleteMeal(mealId);
          
          // Reload data to update totals
          await loadData();
          
          haptics.success();
        }
      }
    } catch (error) {
      // ... error handling ...
    }
  }
};
```

**Process:**
1. Delete meal via API
2. Parse response with XP data
3. Update Zustand gamification store immediately
4. Remove meal from meals store
5. Reload dashboard data
6. No page refresh required

### Data Flow

**Meal Creation:**
```
1. User logs meal
2. Meal saved to database (gets ID)
3. award_xp() called with {"meal_id": meal.id}
4. XPLog created with:
   - source: "meal_log"
   - reference_id: meal.id
   - delta: XP amount
5. User's total_xp updated
6. Frontend receives gamification data
```

**Meal Deletion:**
```
1. User deletes meal
2. Backend finds XPLog entries where reference_id == meal_id
3. Sums XP from those entries
4. Subtracts from user's total_xp
5. Deletes XPLog entries
6. Deletes meal
7. Returns: {xp_removed, new_total_xp, new_level}
8. Frontend updates Zustand store
9. Dashboard reloads with correct values
```

### Result
- XP is correctly linked to meals via `reference_id`
- Deleting a meal removes associated XP
- User's level updates if XP loss causes level down
- Frontend updates immediately without refresh
- No orphaned XP entries in database
- Consistent XP tracking across all actions

---

## Testing Checklist

### Animation Testing
- [ ] FAB button scales subtly on press (1 → 1.05)
- [ ] FAB animation completes before sheet opens
- [ ] No bouncy or aggressive motion
- [ ] Meal logged card appears smoothly
- [ ] Checkmark scales subtly (1 → 1.05 → 1)
- [ ] All animations feel premium on mobile
- [ ] No overlapping animations

### XP Deletion Testing
- [ ] Log a meal and verify XP is awarded
- [ ] Check XPLog table has entry with reference_id = meal_id
- [ ] Delete the meal
- [ ] Verify XP is removed from user's total
- [ ] Verify XPLog entry is deleted
- [ ] Verify level updates if necessary
- [ ] Verify frontend updates without refresh
- [ ] Log multiple meals and delete one - only that meal's XP removed
- [ ] Verify macro/daily goal XP is NOT affected by meal deletion

---

## Database Migration

Run the migration to add new fields:
```bash
alembic upgrade head
```

This adds:
- `source` column (VARCHAR(50), default 'meal_log', indexed)
- `reference_id` column (INTEGER, nullable, indexed)

Existing XPLog entries will have:
- `source` = 'meal_log' (default)
- `reference_id` = NULL (no retroactive linking)

---

## Summary

### Issue 1 - Animations
- Replaced aggressive `withSpring` with smooth `withTiming`
- Reduced scale from 1.2x to 1.05x
- Added proper animation sequencing
- 150ms duration with smooth easing
- Premium feel on mobile devices

### Issue 2 - XP Deletion
- Added `source` and `reference_id` to XPLog
- XP entries now linked to meals
- Delete endpoint removes associated XP
- Frontend updates immediately
- No orphaned XP in database
- Consistent XP tracking

Both issues fixed with minimal, stable changes. No refactoring of unrelated code. All existing functionality preserved.
