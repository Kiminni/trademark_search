from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.database import init_db
from app.routers import trademark_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("애플리케이션 시작: DB 초기화 시도...")
    await init_db()
    print("애플리케이션 시작: DB 초기화 완료.")
    yield
    print("애플리케이션 종료...")

app = FastAPI(
    title="상표 검색 API",
    description="마크클라우드 상표 검색 API 시스템",
    version="1.0.0",
    lifespan=lifespan
)

# 라우터 등록
app.include_router(trademark_routes.router)

@app.get("/health")
async def health_check():
    return {"status": "OK"} 