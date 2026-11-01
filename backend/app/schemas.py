from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class VerifyIn(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class EmailOnlyIn(BaseModel):
    email: EmailStr


class ResetIn(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")
    new_password: str = Field(min_length=8, max_length=128)


class ScanIn(BaseModel):
    url: str = Field(min_length=1, max_length=2048)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    role: str
    email_verified: bool
    created_at: datetime


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ScanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    submitted_url: str
    normalized_url: str
    ml_probability: float
    heuristic_score: float
    risk_score: float
    verdict: str
    external_status: str
    explanation: str
    created_at: datetime


class ScanDetailOut(ScanOut):
    features: dict[str, Any]
    triggered_checks: list[dict[str, Any]]
    detection_method: str
    safety_note: str


class ProfileUpdateIn(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
