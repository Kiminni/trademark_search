import json
import os
from typing import List, Dict, Any
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.trademark import TradeMarkCreate # 데이터 유효성 검사 및 변환용 스키마
from app.models.trademark import TradeMark as TradeMarkModel # DB 저장을 위한 SQLAlchemy 모델


# date 객체를 문자열로 변환하는 JSON 인코더
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()  # ISO 형식 문자열로 변환 (예: "2023-05-06")
        return super().default(obj)
    

async def load_trademarks_from_json(
    db: AsyncSession,
    file_path: str = "/data/trademark_sample.json"
) -> int:
    """JSON 파일에서 상표 데이터를 읽어 데이터베이스에 적재합니다."""
    loaded_count = 0
    print(f"데이터 파일 경로: {file_path}")

    # 파일 존재 여부 확인
    if not os.path.exists(file_path):
        print(f"오류: {file_path} 파일을 찾을 수 없습니다.")
        return 0

    # 파일 크기 확인
    file_size = os.path.getsize(file_path)
    print(f"데이터 파일 크기: {file_size} 바이트")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_data: List[Dict[str, Any]] = json.load(f)
            print(f"JSON 파싱 완료: {len(raw_data)}개 항목 발견")
    except FileNotFoundError:
        print(f"오류: {file_path} 파일을 찾을 수 없습니다.")
        return 0
    except json.JSONDecodeError as e:
        print(f"오류: {file_path} 파일의 JSON 형식이 올바르지 않습니다. 상세: {e}")
        return 0
    except Exception as e:
        print(f"오류: 파일 읽기 중 예상치 못한 오류 발생: {e}")
        return 0

    # 데이터가 없는 경우
    if not raw_data:
        print("오류: 데이터 파일에 항목이 없습니다.")
        return 0

    print("데이터베이스에 항목 추가 시작...")

    for idx, item in enumerate(raw_data):
        try:
            # 진행 상황 로깅 (100개 단위)
            if idx % 100 == 0 and idx > 0:
                print(f"진행 중: {idx}/{len(raw_data)} 항목 처리...")

            trademark_data = TradeMarkCreate.model_validate(item)
            db_trademark = TradeMarkModel(**trademark_data.model_dump(mode='json', exclude_unset=True))
            db.add(db_trademark)
            loaded_count += 1

        except Exception as e:
            print(f"데이터 항목 처리 중 오류 발생: {item.get('applicationNumber', '알 수 없음')}, 오류: {e}")
            continue

    print(f"데이터베이스 커밋 시작 (총 {loaded_count}개 항목)...")
    try:
        await db.commit()
        print("데이터베이스 커밋 성공!")
    except Exception as e:
        await db.rollback()
        print(f"데이터베이스 커밋 중 오류 발생: {e}")
        return 0

    print(f"데이터 적재 완료! (총 {loaded_count}개)")
    return loaded_count