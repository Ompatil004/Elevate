from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum


class GenderEnum(str, Enum):
    male = "Male"
    female = "Female"


class GoalEnum(str, Enum):
    muscle_gain = "Muscle Gain"
    weight_loss = "Weight Loss"
    maintain = "Maintain"


class ActivityLevelEnum(str, Enum):
    sedentary = "Sedentary"
    lightly_active = "Lightly Active"
    moderately_active = "Moderately Active"
    very_active = "Very Active"


class ExperienceLevelEnum(str, Enum):
    beginner = "Beginner"
    intermediate = "Intermediate"
    advanced = "Advanced"


class DietaryPreferenceEnum(str, Enum):
    veg = "Veg"
    non_veg = "Non-Veg"
    vegan = "Vegan"


class UserBase(BaseModel):
    age: int
    weight: float
    height: float
    gender: GenderEnum
    goal: GoalEnum
    activity_level: ActivityLevelEnum
    experience: ExperienceLevelEnum
    equipment: List[str] = []
    allergies: List[str] = []
    body_issues: List[str] = []
    dietary_preference: DietaryPreferenceEnum = DietaryPreferenceEnum.non_veg
    days_per_week: int = 3
    streak: int = 0


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    gender: Optional[GenderEnum] = None
    goal: Optional[GoalEnum] = None
    activity_level: Optional[ActivityLevelEnum] = None
    experience: Optional[ExperienceLevelEnum] = None
    equipment: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    body_issues: Optional[List[str]] = None
    dietary_preference: Optional[DietaryPreferenceEnum] = None
    days_per_week: Optional[int] = None
    streak: Optional[int] = None


class UserInDB(UserBase):
    id: str
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()


class WorkoutHistory(BaseModel):
    user_id: str
    workout_plan: dict
    date: datetime = datetime.utcnow()
    completed: bool = False


class MealHistory(BaseModel):
    user_id: str
    meal_plan: dict
    date: datetime = datetime.utcnow()
    calories_consumed: Optional[float] = None


class WorkoutCompletion(BaseModel):
    user_id: str
    workout_day: dict  # The specific day's workout from the weekly plan
    date: datetime = datetime.utcnow()
    completed: bool = True
    completion_time: Optional[datetime] = None


class MealCompletion(BaseModel):
    user_id: str
    meal_info: dict  # The specific meal from the weekly plan
    date: datetime = datetime.utcnow()
    consumed: bool = True
    calories_consumed: Optional[float] = None
    completion_time: Optional[datetime] = None