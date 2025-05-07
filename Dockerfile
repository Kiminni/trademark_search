FROM python:3.11-slim

WORKDIR /app

# Python이 모듈을 찾을 경로에 프로젝트 루트 추가
ENV PYTHONPATH="/"

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

RUN chmod +x scripts/wait_for_db.py scripts/load_data.py

# 또는 애플리케이션이 uvicorn 등으로 실행된다면:
CMD ["sh", "-c", "python scripts/wait_for_db.py && python scripts/load_data.py && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"] 