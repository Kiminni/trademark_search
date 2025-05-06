from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import date
import re

def parse_date_or_none(value: Optional[str]) -> Optional[date]:
    if value is None:
        return None
    if not re.match(r"^\d{8}$", value):
        return None
    try:
        return date(int(value[:4]), int(value[4:6]), int(value[6:8]))
    except ValueError:
        return None

class TradeMarkBase(BaseModel):
    productName: Optional[str] = None
    productNameEng: Optional[str] = Field(None, alias='productNameEng') # alias 사용 예시 (필요시)
    applicationNumber: str
    applicationDate: Optional[date] = None
    registerStatus: Optional[str] = None
    publicationNumber: Optional[str] = None
    publicationDate: Optional[date] = None
    registrationNumber: Optional[List[str]] = None
    registrationDate: Optional[List[Optional[date]]] = None # 리스트 내 날짜도 Optional 처리
    registrationPubNumber: Optional[str] = None
    registrationPubDate: Optional[date] = None
    internationalRegDate: Optional[date] = None
    internationalRegNumbers: Optional[str] = None # 문자열일 수 있음 (확인 필요)
    priorityClaimNumList: Optional[List[str]] = None
    priorityClaimDateList: Optional[List[Optional[date]]] = None # 리스트 내 날짜도 Optional 처리
    asignProductMainCodeList: Optional[List[str]] = None
    asignProductSubCodeList: Optional[List[str]] = None
    viennaCodeList: Optional[List[str]] = None

    # 날짜 필드 유효성 검사 및 변환
    @field_validator('applicationDate', 'publicationDate', 'registrationPubDate', 'internationalRegDate', mode='before')
    @classmethod
    def validate_date_format(cls, value: Optional[str]) -> Optional[date]:
        return parse_date_or_none(value)

    # 날짜 리스트 필드 유효성 검사 및 변환
    @field_validator('registrationDate', 'priorityClaimDateList', mode='before')
    @classmethod
    def validate_date_list_format(cls, value: Optional[List[Optional[str]]]) -> Optional[List[Optional[date]]]:
        if value is None:
            return None
        return [parse_date_or_none(d) for d in value]


# 데이터베이스 저장을 위한 스키마 (필요시 Base 상속 및 수정)
class TradeMarkCreate(TradeMarkBase):
    pass

# 데이터베이스에서 읽어올 때 또는 API 응답을 위한 스키마
class TradeMark(TradeMarkBase):
    id: int # 데이터베이스에서 자동 생성되는 ID

    class Config:
        orm_mode = True # SQLAlchemy 모델과 호환되도록 설정 (Pydantic V1)
        # Pydantic V2에서는 from_attributes = True
        from_attributes = True 