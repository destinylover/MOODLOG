from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

    class Config:
        from_attributes = True


class DiaryEmotionCreate(BaseModel):
    user_id: int
    content: str
    emotion: str
    advice: str
    score: float
    timestamp: datetime

    class Config:
        from_attributes = True


class DiaryEmotionOut(BaseModel):
    id: int
    content: str
    emotion: str
    advice: str
    score: float
    timestamp: datetime

    class Config:
        from_attributes = True
