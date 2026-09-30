from ..config import get_settings
from ..schemas import WorkoutPlan
from .gemini_client import generate_structured

def _mock_update(original, feedback):
    revised=original.model_copy(deep=True)
    revised.summary=f"{original.summary} Revised using this feedback: {feedback}"
    low=feedback.lower()
    for day in revised.days:
        if "yoga" in low and day.day in {"Day 4","Day 7"}:
            day.focus="Yoga-inspired mobility and recovery"
            day.exercises=day.exercises[:2]
            day.exercises[0]=day.exercises[0].model_copy(update={"name":"Gentle yoga flow","sets":None,"reps":None,"duration_minutes":20})
        if "cardio" in low and day.day=="Day 5":
            day.exercises.append(day.exercises[0].model_copy(update={"name":"Easy cardio","sets":None,"reps":None,"duration_minutes":20,"rest_seconds":None}))
        if any(x in low for x in ["easier","lower impact","reduce intensity"]):
            day.exercises=[e.model_copy(update={"sets":max(1,(e.sets or 2)-1) if e.sets else None}) for e in day.exercises]
    return revised

def update_workout_plan(original_plan, feedback):
    s=get_settings()
    original=WorkoutPlan.model_validate_json(original_plan)
    if s.mock_ai: return _mock_update(original,feedback)
    prompt=f"""
Revise this existing FitBuddy 7-day workout plan based on the user's feedback.
Original:
{original.model_dump_json(indent=2)}
Feedback:
{feedback}
Preserve exactly 7 days. Make practical, conservative changes. Avoid medical treatment, extreme training, unsafe recommendations.
If feedback asks for something potentially unsafe, use a safer alternative and note it.
Return only the supplied structured schema.
"""
    return generate_structured(s.gemini_workout_model,prompt,WorkoutPlan)
