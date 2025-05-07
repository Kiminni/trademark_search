import asyncio
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from app.db.database import AsyncSessionLocal, engine 
from app.utils.data_loader import load_trademarks_from_json 
from app.models.trademark import Base 

async def main():
    """데이터베이스를 초기화하고 JSON 데이터를 로드하는 메인 함수"""
    print("데이터베이스 테이블 초기화 (기존 테이블 재생성)...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("테이블 초기화 완료.")

    async with AsyncSessionLocal() as db_session:
        print(f"trademark_sample.json 파일에서 데이터 로딩 시작...")
        
        json_file_path = os.path.join(os.path.dirname(__file__), "trademark_sample.json")
        loaded_count = await load_trademarks_from_json(db=db_session, file_path=json_file_path)
        print(f"데이터 로딩 완료. 총 {loaded_count}개 항목 처리.")

    # 모든 작업 완료 후 엔진 리소스 명시적 해제
    await engine.dispose()
    print("데이터베이스 엔진 리소스 해제 완료.")

if __name__ == "__main__":
    if not os.getenv("DATABASE_URL"):
        print("오류: DATABASE_URL 환경 변수가 설정되지 않았습니다. .env 파일을 확인하세요.")
        sys.exit(1)
        
    asyncio.run(main()) 