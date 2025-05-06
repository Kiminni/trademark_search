from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.database import init_db
from app import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("애플리케이션 시작: DB 초기화 시도...")
    await init_db()
    print("애플리케이션 시작: DB 초기화 완료.")
    yield
    print("애플리케이션 종료...")

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health_check():
    return {"status": "OK"} 