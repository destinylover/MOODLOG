from sqlalchemy.orm import Session
from models import User, DiaryEmotion
from passlib.context import CryptContext
from schemas import UserCreate, DiaryEmotionCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if user and pwd_context.verify(password, user.hashed_password):
        return user
    return None

def create_diary_emotion(db: Session, diary: DiaryEmotionCreate, user_id: int):
    data = diary.dict(exclude={"user_id"})  # user_id 중복 방지
    db_diary = DiaryEmotion(**data, user_id=user_id)
    db.add(db_diary)
    db.commit()
    db.refresh(db_diary)
    return db_diary

def get_user_diaries(db: Session, user_id: int):
    return db.query(DiaryEmotion).filter(DiaryEmotion.user_id == user_id).order_by(DiaryEmotion.created_at.desc()).all()

def get_emotion_statistics(db: Session, user_id: int):
    records = db.query(DiaryEmotion.emotion).filter(DiaryEmotion.user_id == user_id).all()
    stats = {}
    for (emotion,) in records:
        stats[emotion] = stats.get(emotion, 0) + 1
    return stats
