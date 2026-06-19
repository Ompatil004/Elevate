from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class GenderEnum(str, Enum):
    male = "Male"
    female = "Female"


class GoalEnum(str, Enum):
    muscle_gain = "Muscle Gain"
    weight_loss = "Weight Loss"
    fat_loss = "Fat Loss"
    maintenance = "Maintenance"
    strength = "Strength"
    endurance = "Endurance"
    athletic_performance = "Athletic Performance"


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
    equipment: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    body_issues: List[str] = Field(default_factory=list)
    dietary_preference: DietaryPreferenceEnum = DietaryPreferenceEnum.non_veg
    days_per_week: int = 3
    streak: int = 0
    consistency: float = 0.7  # 0.0-1.0 adherence score
    sleep_score: float = 7.0  # 1-10 scale
    hydration_score: float = 7.0  # 1-10 scale
    stress_level: float = 5.0  # 1-10 scale (high = bad)


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
    consistency: Optional[float] = None
    sleep_score: Optional[float] = None
    hydration_score: Optional[float] = None
    stress_level: Optional[float] = None


class UserInDB(UserBase):
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WorkoutHistory(BaseModel):
    user_id: str
    workout_plan: dict
    date: datetime = Field(default_factory=datetime.utcnow)
    completed: bool = False


class MealHistory(BaseModel):
    user_id: str
    meal_plan: dict
    date: datetime = Field(default_factory=datetime.utcnow)
    calories_consumed: Optional[float] = None


class WorkoutCompletion(BaseModel):
    user_id: str
    workout_day: dict
    date: datetime = Field(default_factory=datetime.utcnow)
    completed: bool = True
    completion_time: Optional[datetime] = None


class MealCompletion(BaseModel):
    user_id: str
    meal_info: dict  # The specific meal from the weekly plan
    meal_type: str  # "breakfast", "lunch", "dinner", "snack"
    items: List[dict] = Field(default_factory=list)  # [{name, quantity, ticked, tick_time}, ...]
    date: str  # ISO date string "YYYY-MM-DD"
    consumed: bool = True
    calories_consumed: Optional[float] = None
    completion_time: Optional[str] = None
    locked: bool = False  # Locked after all items are ticked


class MealItemTick(BaseModel):
    user_id: str
    date: str  # ISO date string
    meal_type: str  # "breakfast", "lunch", "dinner", "snack"
    item_index: int
    ticked: bool


class MealHistoryEntry(BaseModel):
    user_id: str
    date: str
    meals: dict = Field(default_factory=dict)  # { "breakfast": {name, calories, items, completed_at}, ... }
    total_calories: Optional[float] = None
    total_protein: Optional[float] = None
    total_carbs: Optional[float] = None
    total_fat: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)