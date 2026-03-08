from typing import Optional, Iterable, Dict
from math import floor


def compute_calories(protein: int, carbs: int, fats: int) -> int:
    return protein * 4 + carbs * 4 + fats * 9


def sanitize_meal_input(protein: int, carbs: int, fats: int, calories: Optional[int] = None) -> Dict[str, int]:
    if any(x is None for x in [protein, carbs, fats]):
        raise ValueError("macros_required")
    if protein < 0 or carbs < 0 or fats < 0:
        raise ValueError("macros_non_negative")
    calc = compute_calories(protein, carbs, fats)
    final_cal = calc if calories is None else calc
    return {"protein": protein, "carbs": carbs, "fats": fats, "calories": final_cal}


def sum_macros(rows: Iterable) -> Dict[str, int]:
    p = c = f = cal = 0
    for r in rows:
        p += int(getattr(r, "protein", 0) or 0)
        c += int(getattr(r, "carbs", 0) or 0)
        f += int(getattr(r, "fats", 0) or 0)
        cal += int(getattr(r, "calories", 0) or 0)
    return {"protein": p, "carbs": c, "fats": f, "calories": cal}


def weekly_averages(rows: Iterable, days: int = 7) -> Dict[str, float]:
    totals = sum_macros(rows)
    d = max(days, 1)
    return {
        "protein": totals["protein"] / d,
        "carbs": totals["carbs"] / d,
        "fats": totals["fats"] / d,
        "calories": totals["calories"] / d,
        "days": d,
    }

