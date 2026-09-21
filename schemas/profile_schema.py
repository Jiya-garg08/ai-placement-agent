from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=255)


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentProfileBase(BaseModel):
    target_role: str = Field(default="Software Development Engineer (SDE)", max_length=150)
    career_goal: Optional[str] = Field(default=None, max_length=255)
    target_company_tier: Optional[str] = Field(default="Tier 1 / Product", max_length=50)
    college: Optional[str] = Field(default=None, max_length=255)
    graduation_year: Optional[int] = Field(default=None, ge=2020, le=2035)
    current_semester: Optional[int] = Field(default=None, ge=1, le=10)
    primary_skills: List[str] = Field(default_factory=list)


class StudentProfileCreate(StudentProfileBase):
    user_id: int


class StudentProfileUpdate(BaseModel):
    target_role: Optional[str] = None
    career_goal: Optional[str] = None
    target_company_tier: Optional[str] = None
    college: Optional[str] = None
    graduation_year: Optional[int] = None
    current_semester: Optional[int] = None
    primary_skills: Optional[List[str]] = None


class StudentProfileResponse(StudentProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentOnboardingRequest(BaseModel):
    """Combined payload for onboarding a student with user and profile data."""
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    target_role: str = Field(default="Software Development Engineer (SDE)")
    career_goal: Optional[str] = "Product Company SDE-1"
    target_company_tier: Optional[str] = "Tier 1 / Product"
    college: Optional[str] = None
    graduation_year: Optional[int] = 2026
    current_semester: Optional[int] = 7
    primary_skills: List[str] = Field(default_factory=list)
