from ..config import get_settings
from ..schemas import UserInput, WorkoutPlan
from .gemini_client import generate_structured

def _mock_plan(user):
    focus_map={
        "weight_loss":["Full body + cardio","Lower body + cardio","Upper body + core","Intervals + mobility","Full body circuit","Low-impact cardio","Recovery + mobility"],
        "muscle_gain":["Full body strength","Lower body strength","Upper body strength","Active recovery","Full body strength","Upper body + core","Recovery + mobility"],
        "general_wellness":["Full body","Cardio + core","Strength","Mobility","Full body","Cardio","Recovery + mobility"],
        "flexibility":["Mobility + lower body","Upper body mobility","Yoga-inspired flow","Mobility + core","Full body flexibility","Gentle cardio + stretch","Recovery flow"],
    }[user.goal]
    days=[]
    for i, focus in enumerate(focus_map,1):
        recovery="Recovery" in focus or "Mobility" in focus
        days.append({
            "day":f"Day {i}","focus":focus,
            "warmup":"5–8 minutes of easy movement and dynamic mobility.",
            "exercises":[
                {"name":"Bodyweight squat" if not recovery else "Cat-cow","sets":3 if not recovery else 2,"reps":"10–12" if not recovery else "8–10","duration_minutes":None,"rest_seconds":60,"notes":"Use a comfortable range of motion."},
                {"name":"Incline push-up" if not recovery else "Bird-dog","sets":3 if not recovery else 2,"reps":"8–12" if not recovery else "8 each side","duration_minutes":None,"rest_seconds":60,"notes":"Use an easier variation if form deteriorates."},
                {"name":"Brisk walk","sets":None,"reps":None,"duration_minutes":15 if not recovery else 20,"rest_seconds":None,"notes":"Keep the pace conversational."},
            ],
            "cooldown":"5 minutes of relaxed walking and gentle stretching.",
            "recovery_note":"Stop if you feel sharp pain, dizziness, or unusual shortness of breath.",
        })
    return WorkoutPlan(
        title=f"FitBuddy 7-Day {user.goal.replace('_',' ').title()} Plan",
        summary=f"A beginner-friendly {user.intensity}-intensity plan for {user.username}, emphasizing consistency and gradual progression.",
        safety_note="This is general wellness guidance, not medical advice. Adjust activity to your ability and seek professional advice when needed.",
        days=days)

def generate_workout_gemini(user: UserInput):
    s=get_settings()
    if s.mock_ai: return _mock_plan(user)
    prompt=f"""
You are FitBuddy's workout-planning engine. Create a safe, practical 7-day plan.
User: name={user.username}; age={user.age}; weight_kg={user.weight}; goal={user.goal}; intensity={user.intensity}.
Exactly 7 days. Each day needs focus, 5–10 minute warm-up, at least one exercise, cooldown, and recovery note where useful.
For strength give sets/reps; for cardio or mobility give duration when appropriate. Include rest periods.
Include at least one recovery or mobility day. Avoid diagnosis, treatment, medication, extreme dieting, or unsafe challenges.
Return only the supplied structured schema.
"""
    return generate_structured(s.gemini_workout_model,prompt,WorkoutPlan)
