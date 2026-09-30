from typing import Literal
from pydantic import BaseModel, Field, field_validator

Goal = Literal["weight_loss", "muscle_gain", "general_wellness", "flexibility"]
Intensity = Literal["low", "medium", "high"]

class UserInput(BaseModel):
    username: str = Field(min_length=2, max_length=120)
    user_id: str = Field(min_length=2, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=20, le=500)
    goal: Goal
    intensity: Intensity
    @field_validator("username", "user_id")
    @classmethod
    def clean(cls, v):
        v=v.strip()
        if not v: raise ValueError("Value cannot be blank")
        return v

class FeedbackRequest(BaseModel):
    user_id: str = Field(min_length=2, max_length=80)
    feedback: str = Field(min_length=5, max_length=2000)
    @field_validator("user_id", "feedback")
    @classmethod
    def clean(cls, v):
        v=v.strip()
        if not v: raise ValueError("Value cannot be blank")
        return v

class Exercise(BaseModel):
    name: str
    sets: int | None = Field(default=None, ge=1, le=10)
    reps: str | None = None
    duration_minutes: int | None = Field(default=None, ge=1, le=180)
    rest_seconds: int | None = Field(default=None, ge=0, le=600)
    notes: str | None = None

class WorkoutDay(BaseModel):
    day: str
    focus: str
    warmup: str
    exercises: list[Exercise] = Field(min_length=1, max_length=10)
    cooldown: str
    recovery_note: str | None = None

class WorkoutPlan(BaseModel):
    title: str
    summary: str
    safety_note: str
    days: list[WorkoutDay] = Field(min_length=7, max_length=7)

class NutritionTip(BaseModel):
    tip: str
    hydration: str
    recovery: str
