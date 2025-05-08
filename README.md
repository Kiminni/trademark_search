# 상표 검색 API

상표 데이터 검색을 위한 FastAPI 기반 API 서비스입니다.

## 목차
- [실행 방법](#실행-방법)
- [API 사용법](#api-사용법)
- [구현 기능](#구현-기능)
- [기술적 의사결정](#기술적-의사결정)
- [문제 해결 과정](#문제-해결-과정)
- [개선 희망 사항](#개선-희망-사항)

## 실행 방법

### ENV 파일 설정
```bash
# Database Settings
DB_NAME=trademark_db
DB_USER=user
DB_PASSWORD=password
DB_ROOT_PASSWORD=rootpassword
DB_HOST=db
DB_PORT=3306
DATABASE_URL=mysql+aiomysql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}
```

### 가상환경 설정 (로컬 개발)
```bash
# 저장소 복제
git clone https://github.com/yourusername/trademark_search.git
cd trademark_search

# Python 가상환경 생성
python -m venv venv

# 가상환경 활성화
## macOS/Linux:
source venv/bin/activate
## Windows:
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정 (예시)
export DB_NAME=trademark_db
export DB_USER=root
export DB_PASSWORD=password
export DB_HOST=localhost
export DB_PORT=3306
export DATABASE_URL=mysql+aiomysql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}

# 서버 실행
uvicorn app.main:app --reload
```

### Docker를 사용한 실행
```bash
docker compose up --build
```

서버가 시작되면 `http://localhost:8000`으로 접속할 수 있습니다.
API 문서는 `http://localhost:8000/docs`에서 확인 가능합니다.

## API 사용법

### 기본 검색 엔드포인트

#### GET `/api/trademarks/search`

상표 데이터를 키워드, 필터로 검색합니다.

**쿼리 파라미터:**
- `query`: 검색 키워드 (상표명에서 검색)
- `status`: 등록 상태 필터 (예: "등록", "출원", "거절" 등)
- `start_date`: 출원일 시작 날짜 (YYYYMMDD)
- `end_date`: 출원일 종료 날짜 (YYYYMMDD)
- `product_code`: 상품 주 분류 코드
- `fuzzy`: 유사 검색 사용 여부 (true/false)
- `page`: 페이지 번호 (기본값: 1)
- `page_size`: 페이지당 항목 수 (기본값: 20)

**응답 예시:**
```json
{
  "items": [...],
  "total": 15,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "query": "상표명",
  "filters_applied": {
    "status": "등록",
    "date_range": "20200101-20221231"
  }
}
```

#### GET `/api/trademarks/{application_number}`

출원 번호로 특정 상표 정보를 조회합니다.

**응답 예시:**
```json
{
  "productName": "상표명",
  "productNameEng": "Trademark Name",
  "applicationNumber": "4020200012345",
  "applicationDate": "20200101",
  "registerStatus": "등록",
  ...
}
```

## 구현 기능

1. **기본 검색 기능**
   - 상표명(한글/영문) 검색
   - 출원번호 기반 정확한 검색
   - 페이지네이션 지원

2. **고급 필터링**
   - 등록 상태별 필터링 (등록, 출원, 거절 등)
   - 날짜 범위 필터링 (출원일, 등록일)
   - 상품 분류 코드 기반 필터링

3. **유사 검색 기능**
   - Levenshtein 거리 기반 유사도 검색
   - 오타 교정 및 유사 단어 매칭

4. **결측치 처리**
   - 데이터 내 null 값 자동 처리
   - 리스트 형태 필드의 효율적 처리

5. **성능 최적화**
   - 인덱싱을 통한 빠른 검색 지원
   - 대용량 데이터 처리를 위한 스트리밍 응답

## 기술적 의사결정

### 데이터 처리 방식
- 초기 로딩 시 JSON 파일을 SQLAlchemy 모델로 변환하여 데이터베이스에 저장
- 효율적인 쿼리 빌더 패턴을 통한 검색 성능 최적화
- 필터링 및 검색 연산은 SQLAlchemy ORM 기반으로 구현

### 데이터베이스 구조
- MySQL을 메인 데이터베이스로 사용하여 데이터 영속성 확보
- SQLAlchemy의 비동기 세션을 활용한 효율적인 데이터 접근
- 인덱싱을 통한 검색 성능 최적화

### API 설계
- RESTful 원칙 준수
- 명확한 엔드포인트 구조화
- 상세한 필터링 옵션 제공

## 문제 해결 과정

### 데이터 전처리 문제
상표 데이터에는 여러 형태의 결측치와 리스트 필드가 존재했습니다.
- null 값은 필드 특성에 맞게 빈 문자열 또는 빈 리스트로 변환
- 날짜 형식은 YYYYMMDD 형식으로 통일하여 비교 연산 용이하게 처리
- 리스트 필드는 검색 시 효율적인 처리를 위해 별도 인덱싱 구조 도입

### 복합 필터링 구현 도전
다중 필터 조건을 동시에 처리하는 과정에서 발생한 문제들:
- AND/OR 조건 결합 시 성능 저하 문제 발생
- 해결: 필터 적용 순서 최적화 (선택도가 높은 필터 우선 적용)
- SQLAlchemy의 동적 쿼리 빌더 패턴 구현으로 효율적인 필터 체이닝 구현

## 테스트 코드 작성

프로젝트 안정성을 위해 다양한 테스트 코드를 작성했습니다:

### 단위 테스트
- `tests/unit/test_trademark_service.py`: 상표 검색 서비스 로직 테스트
- `tests/unit/test_filters.py`: 필터 로직 정확성 테스트
- `tests/unit/test_data_processing.py`: 데이터 전처리 기능 테스트

### 통합 테스트
- `tests/integration/test_api_endpoints.py`: API 엔드포인트 동작 검증
- `tests/integration/test_db_operations.py`: 데이터베이스 연동 테스트

### 성능 테스트
- `tests/performance/test_search_performance.py`: 대규모 데이터 검색 성능 측정
- `tests/performance/test_caching.py`: 캐싱 효율성 테스트

테스트 실행 방법:
```bash
# 모든 테스트 실행
pytest

# 특정 테스트 실행
pytest tests/unit/test_trademark_service.py

# 커버리지 리포트 생성
pytest --cov=app tests/
```

## 개선 희망 사항

### 검색 기능 고도화
- 형태소 분석 기반 검색 품질 향상
- 관련성 점수(relevance score) 기반 결과 정렬
- 자동 완성 및 추천 검색어 기능 추가

### 대용량 데이터 처리 
- 해결: 커서 기반 페이지네이션 구현으로 메모리 효율성 개선
- 비동기 I/O 활용으로 동시 요청 처리 성능 향상
- Redis 캐싱을 통한 조회 속도 향상

### 검색 품질 개선
- 자소 분리 적용으로 한글 특성 고려한 검색 개선
- 상품 코드 및 등록 상태 기반 결과 정렬 로직 구현

### 캐싱 시스템 도입
- Redis를 활용한 검색 결과 캐싱 구현
- 자주 사용되는 쿼리 패턴 분석을 통한 효율적인 캐싱 전략 수립
- 캐시 무효화 정책 구현으로 데이터 일관성 확보

### 확장성 강화
- 로드 밸런싱 및 수평적 확장 구조 도입
- 캐싱 계층 강화
- 마이크로서비스 아키텍처로 재구성 고려
