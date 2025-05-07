#!/usr/bin/env python3
"""
Database connection checker script.
Attempts to connect to the database specified in DATABASE_URL environment variable.
"""
import asyncio
import os
import sys
import time
import aiomysql
import pymysql

# 프로젝트 루트를 sys.path에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

# Constants
MAX_RETRIES = 30
RETRY_DELAY = 2  # seconds

def parse_db_url(url):
    """DATABASE_URL을 파싱하여 연결 정보를 추출합니다."""
    if not url or not url.startswith('mysql+aiomysql://'):
        raise ValueError("유효한 mysql+aiomysql:// URL이 아닙니다.")

    # mysql+aiomysql:// 부분 제거
    url = url.replace('mysql+aiomysql://', '')

    # 사용자 정보와 호스트 정보 분리
    if '@' in url:
        auth, rest = url.split('@', 1)
    else:
        auth, rest = '', url

    # 호스트와 데이터베이스 분리
    if '/' in rest:
        host_port, db = rest.split('/', 1)
    else:
        host_port, db = rest, ''

    # 사용자와 비밀번호 분리
    if ':' in auth:
        user, password = auth.split(':', 1)
    else:
        user, password = auth, ''

    # 호스트와 포트 분리
    if ':' in host_port:
        host, port = host_port.split(':', 1)
        port = int(port)
    else:
        host, port = host_port, 3306

    return {
        'user': user,
        'password': password,
        'host': host,
        'port': port,
        'db': db
    }

async def check_db_connection():
    """데이터베이스 연결을 확인합니다. 직접 aiomysql을 사용합니다."""
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("오류: DATABASE_URL 환경 변수가 설정되지 않았습니다.", file=sys.stderr)
        return False

    print(f"데이터베이스 연결 시도 중... ({database_url})")

    try:
        db_config = parse_db_url(database_url)
    except ValueError as e:
        print(f"오류: {e}", file=sys.stderr)
        return False

    # Try to connect with retries
    for attempt in range(1, MAX_RETRIES + 1):
        conn = None
        try:
            # 직접 aiomysql 연결 생성
            conn = await aiomysql.connect(
                host=db_config['host'],
                port=db_config['port'],
                user=db_config['user'],
                password=db_config['password'],
                db=db_config['db']
            )

            # 간단한 쿼리 실행으로 연결 확인
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                result = await cur.fetchone()
                if result and result[0] == 1:
                    print("데이터베이스 연결 성공!")
                    return True

        except (pymysql.err.OperationalError, OSError) as e:
            print(f"데이터베이스 연결 실패 (시도 {attempt}/{MAX_RETRIES}): {e}",
                  file=sys.stderr)

            if attempt < MAX_RETRIES:
                print(f"{RETRY_DELAY}초 후 재시도...")
                await asyncio.sleep(RETRY_DELAY)
            else:
                print("최대 재시도 횟수 초과. 데이터베이스 연결에 실패했습니다.",
                      file=sys.stderr)
                return False

        except Exception as e:
            print(f"예상치 못한 오류 발생 (시도 {attempt}/{MAX_RETRIES}): {e}",
                  file=sys.stderr)

            if attempt < MAX_RETRIES:
                print(f"{RETRY_DELAY}초 후 재시도...")
                await asyncio.sleep(RETRY_DELAY)
            else:
                print("최대 재시도 횟수 초과. 데이터베이스 연결에 실패했습니다.",
                      file=sys.stderr)
                return False
        finally:
            # 연결이 열려 있으면 명시적으로 닫기
            if conn:
                conn.close()  # aiomysql의 close()는 동기 메서드

    return False

def main():
    """Main entry point with proper asyncio handling."""
    start_time = time.time()

    # .env 파일 로딩을 명시적으로 하려면 python-dotenv 설치 및 사용 필요
    # from dotenv import load_dotenv
    # load_dotenv(os.path.join(project_root, ".env"))

    # Use asyncio.run which properly manages the event loop
    success = asyncio.run(check_db_connection())

    elapsed_time = time.time() - start_time
    print(f"스크립트 실행 시간: {elapsed_time:.2f}초")

    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()