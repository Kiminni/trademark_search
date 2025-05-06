from sqlalchemy import Column, Integer, String, Date, JSON
from app.db.base import Base # 수정된 임포트 경로



class TradeMark(Base):
    __tablename__ = "trademarks"

    # 기본 키
    id = Column(Integer, primary_key=True, index=True)

    # 상표 정보
    productName = Column(String(255), nullable=True, index=True)
    productNameEng = Column(String(255), nullable=True, index=True)
    applicationNumber = Column(String(50), unique=True, index=True, nullable=False)
    applicationDate = Column(Date, nullable=True, index=True)
    registerStatus = Column(String(50), nullable=True, index=True)

    # 공고 정보
    publicationNumber = Column(String(50), nullable=True)
    publicationDate = Column(Date, nullable=True)

    # 등록 정보 (리스트는 JSON으로 저장)
    registrationNumber = Column(JSON, nullable=True)
    registrationDate = Column(JSON, nullable=True)
    registrationPubNumber = Column(String(50), nullable=True)
    registrationPubDate = Column(Date, nullable=True)

    # 국제 등록 정보
    internationalRegDate = Column(Date, nullable=True)
    internationalRegNumbers = Column(String(255), nullable=True) # 문자열 또는 JSON? 우선 문자열

    # 우선권 주장 정보 (리스트는 JSON으로 저장)
    priorityClaimNumList = Column(JSON, nullable=True)
    priorityClaimDateList = Column(JSON, nullable=True)

    # 지정상품 정보 (리스트는 JSON으로 저장)
    asignProductMainCodeList = Column(JSON, nullable=True)
    asignProductSubCodeList = Column(JSON, nullable=True)

    # 비엔나 코드 정보 (리스트는 JSON으로 저장)
    viennaCodeList = Column(JSON, nullable=True) 