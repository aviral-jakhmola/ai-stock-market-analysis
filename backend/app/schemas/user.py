from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    """
    What the frontend sends when registering a new user.
    """
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """
    What the frontend sends when logging in.
    """
    username: str
    password: str


class UserResponse(BaseModel):
    """
    What the API sends back about a user — never includes the password
    or password hash, even hashed. Keep sensitive data out of responses.
    """
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True  # allows creating this from a SQLAlchemy model directly


class Token(BaseModel):
    """
    What the API sends back after a successful login.
    """
    access_token: str
    token_type: str = "bearer"