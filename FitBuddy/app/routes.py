import json
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from .database import get_db
from .config import BASE_DIR
from .models import Plan, User
from .schemas import FeedbackRequest, UserInput, NutritionTip
from .services.gemini_client import GeminiServiceError
from .services.gemini_flash_generator import generate_nutrition_tip_with_flash
from .services.gemini_generator import generate_workout_gemini
from .services.updated_plan import update_workout_plan

router=APIRouter()
templates=Jinja2Templates(directory=str(BASE_DIR / "templates"))
GOAL_LABELS={"weight_loss":"Weight loss","muscle_gain":"Muscle gain","general_wellness":"General wellness","flexibility":"Flexibility"}

def ctx(request,**values): return {"request":request,"goal_labels":GOAL_LABELS,**values}

@router.get("/",response_class=HTMLResponse)
def home(request: Request): return templates.TemplateResponse(request=request,name="index.html",context=ctx(request))

@router.post("/generate-workout",response_class=HTMLResponse)
def generate_workout(request:Request, username:str=Form(...), user_id:str=Form(...), age:int=Form(...), weight:float=Form(...), goal:str=Form(...), intensity:str=Form(...), db:Session=Depends(get_db)):
    try:
        data=UserInput(username=username,user_id=user_id,age=age,weight=weight,goal=goal,intensity=intensity)
        workout=generate_workout_gemini(data)
        nutrition=generate_nutrition_tip_with_flash(data)
        user=db.scalar(select(User).where(User.user_id==data.user_id))
        if user is None:
            user=User(user_id=data.user_id,username=data.username,age=data.age,weight=data.weight,goal=data.goal,intensity=data.intensity)
            db.add(user); db.flush()
        else:
            user.username,user.age,user.weight,user.goal,user.intensity=data.username,data.age,data.weight,data.goal,data.intensity
        plan=user.plan
        if plan is None:
            plan=Plan(user_id=user.id,original_plan=workout.model_dump_json(),nutrition_tip=nutrition.model_dump_json()); db.add(plan)
        else:
            plan.original_plan=workout.model_dump_json(); plan.updated_plan=None; plan.feedback=None; plan.nutrition_tip=nutrition.model_dump_json()
        db.commit()
        return templates.TemplateResponse(request=request,name="result.html",context=ctx(request,user=user,workout=workout,nutrition=nutrition,is_updated=False,message="Your personalized plan is ready."))
    except (ValueError,GeminiServiceError) as exc:
        db.rollback()
        return templates.TemplateResponse(request=request,name="error.html",context={"request":request,"message":str(exc)},status_code=400)

@router.post("/submit-feedback",response_class=HTMLResponse)
def submit_feedback(request:Request,user_id:str=Form(...),feedback:str=Form(...),db:Session=Depends(get_db)):
    try:
        data=FeedbackRequest(user_id=user_id,feedback=feedback)
        user=db.scalar(select(User).options(joinedload(User.plan)).where(User.user_id==data.user_id))
        if not user or not user.plan: raise HTTPException(404,"User or plan not found.")
        revised=update_workout_plan(user.plan.original_plan,data.feedback)
        user.plan.updated_plan=revised.model_dump_json(); user.plan.feedback=data.feedback; db.commit()
        nutrition=NutritionTip.model_validate(json.loads(user.plan.nutrition_tip))
        return templates.TemplateResponse(request=request,name="result.html",context=ctx(request,user=user,workout=revised,nutrition=nutrition,is_updated=True,message="Your plan has been updated using your feedback."))
    except HTTPException: raise
    except (ValueError,GeminiServiceError) as exc:
        db.rollback()
        return templates.TemplateResponse(request=request,name="error.html",context={"request":request,"message":str(exc)},status_code=400)

@router.get("/view-all-users",response_class=HTMLResponse)
def view_all_users(request:Request,db:Session=Depends(get_db)):
    users=db.scalars(select(User).options(joinedload(User.plan)).order_by(User.created_at.desc())).unique().all()
    return templates.TemplateResponse(request=request,name="all_users.html",context=ctx(request,users=users))

@router.post("/delete-user/{user_id}")
def delete_user(user_id:str,db:Session=Depends(get_db)):
    user=db.scalar(select(User).where(User.user_id==user_id))
    if not user: raise HTTPException(404,"User not found.")
    db.delete(user); db.commit()
    return RedirectResponse("/view-all-users",status_code=303)

@router.get("/health")
def health(): return {"status":"ok","service":"FitBuddy"}
