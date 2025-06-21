from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime
import os

from database import SessionLocal, engine
import crud, models, schemas
from utils.gpt import analyze_diary_emotion

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "your-secret-key"))

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def root():
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = crud.verify_user(db, username, password)
    if user:
        request.session['user_id'] = user.id
        return RedirectResponse(url="/analyze", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": "로그인 실패"})

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

@app.get("/analyze", response_class=HTMLResponse)
def analyze_form(request: Request):
    return templates.TemplateResponse("analyze.html", {"request": request})

@app.post("/analyze", response_class=HTMLResponse)
def analyze_diary(request: Request, diary: str = Form(...), db: Session = Depends(get_db)):
    user_id = request.session.get('user_id')
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    emotion_result = analyze_diary_emotion(diary)

    record_data = schemas.DiaryEmotionCreate(
        user_id=user_id,
        content=diary,
        emotion=emotion_result.get("emotion", "기타"),
        advice=emotion_result.get("advice", ""),
        score=emotion_result.get("score", 0.5),
        timestamp=datetime.utcnow()
    )

    crud.create_diary_emotion(db, record_data, user_id=int(user_id))

    return templates.TemplateResponse("analyze.html", {
        "request": request,
        "diary": diary,
        "emotion": record_data.emotion,
        "advice": record_data.advice,
        "score": record_data.score
    })

@app.get("/history", response_class=HTMLResponse)
def view_history(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get('user_id')
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    diaries = crud.get_user_diaries(db, user_id)
    return templates.TemplateResponse("history.html", {"request": request, "diaries": diaries})

@app.get("/stats", response_class=HTMLResponse)
def view_stats(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get('user_id')
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    stats = crud.get_emotion_statistics(db, user_id)
    return templates.TemplateResponse("stats.html", {"request": request, "stats": stats})

@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    if crud.get_user_by_username(db, username):
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "이미 존재하는 사용자입니다."
        })

    user = schemas.UserCreate(username=username, password=password)
    crud.create_user(db, user)
    return RedirectResponse(url="/login", status_code=303)

# ✅ 헬스 체크 엔드포인트 (타겟 그룹에서 /health로 설정할 때 사용)
@app.get("/health")
def health_check():
    return {"status": "ok"}
