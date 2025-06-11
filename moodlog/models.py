from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # ✅ 이름을 diary_emotions로 수정하여 일치시킴
    diary_emotions = relationship("DiaryEmotion", back_populates="owner")


class DiaryEmotion(Base):
    __tablename__ = "diary_emotions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)
    emotion = Column(String)
    advice = Column(String)
    score = Column(Float)
    timestamp = Column(DateTime)

    # ✅ User와의 관계에서 이름 일치
    owner = relationship("User", back_populates="diary_emotions")

    # ✅ created_at 기본값 추가
    created_at = Column(DateTime, default=datetime.utcnow)
