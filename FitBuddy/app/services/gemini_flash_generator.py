from ..config import get_settings
from ..schemas import NutritionTip, UserInput
from .gemini_client import generate_structured

def _mock_tip(user):
    return NutritionTip(
        tip=f"Build meals around protein-rich foods, vegetables or fruit, high-fiber carbohydrates, and minimally processed fats. For {user.goal.replace('_',' ')}, focus on consistent habits rather than aggressive restriction.",
        hydration="Drink regularly across the day and increase fluids when you sweat more; use thirst and activity as practical guides.",
        recovery="Aim for regular sleep, adequate food intake, and easier days between harder sessions.")

def generate_nutrition_tip_with_flash(user: UserInput):
    s=get_settings()
    if s.mock_ai: return _mock_tip(user)
    prompt=f"""
You are FitBuddy's fast nutrition and recovery assistant.
Give concise general wellness guidance for goal={user.goal}, intensity={user.intensity}, age={user.age}, weight_kg={user.weight}.
Return one nutrition tip, one hydration tip, and one recovery tip.
Do not prescribe a medical diet, diagnose conditions, recommend medication, or give extreme calorie/macronutrient targets.
Return only the supplied structured schema.
"""
    return generate_structured(s.gemini_fast_model,prompt,NutritionTip)
