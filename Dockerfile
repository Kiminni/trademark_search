FROM python:3.11-slim

WORKDIR /app

# Python이 모듈을 찾을 경로에 프로젝트 루트 추가
ENV PYTHONPATH="/"

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

# uvicorn 실행 (app 패키지의 main 모듈 내 app 객체 지정)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 