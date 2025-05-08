from typing import List, Tuple, Optional, Any, Dict
from sqlalchemy import select, func, or_, and_, cast, String, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import cast
from datetime import datetime, date
from fastapi import status as http_status

from app.models.trademark import TradeMark
from app.schemas.trademark import TradeMarkCreate

async def search_trademarks(
    db: AsyncSession,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    application_date_from: Optional[str] = None,
    application_date_to: Optional[str] = None,
    product_code: Optional[str] = None,
    page: int = 1,
    size: int = 10
) -> Tuple[List[TradeMark], int]:
    """
    상표 검색 서비스 함수
    
    Args:
        db: 데이터베이스 세션
        keyword: 상표명 검색 키워드 (한글/영문)
        status: 등록 상태 필터
        application_date_from: 출원일 시작 날짜 (YYYYMMDD)
        application_date_to: 출원일 종료 날짜 (YYYYMMDD)
        product_code: 상품 주 분류 코드
        page: 페이지 번호 (1부터 시작)
        size: 페이지 크기
        
    Returns:
        검색 결과 리스트와 전체 결과 개수
    """
    # 기본 쿼리 생성
    stmt = select(TradeMark)
    
    # 필터 조건 리스트
    filters = []
    
    # 키워드 검색 (상표명 한글/영문)
    if keyword:
        keyword_filter = or_(
            TradeMark.productName.ilike(f"%{keyword}%"),
            TradeMark.productNameEng.ilike(f"%{keyword}%")
        )
        filters.append(keyword_filter)
    
    # 등록 상태 필터
    if status:
        filters.append(TradeMark.registerStatus == status)
    
    # 출원일 범위 필터
    if application_date_from:
        try:
            date_from = datetime.strptime(application_date_from, "%Y%m%d").date()
            filters.append(TradeMark.applicationDate >= date_from)
        except ValueError:
            # 잘못된 날짜 형식은 무시
            pass
            
    if application_date_to:
        try:
            date_to = datetime.strptime(application_date_to, "%Y%m%d").date()
            filters.append(TradeMark.applicationDate <= date_to)
        except ValueError:
            # 잘못된 날짜 형식은 무시
            pass
    
    # 상품 분류 코드 필터 (JSON 필드에서 검색)
    if product_code:
        # JSON 필드에서 값 검색 - 데이터베이스에 따라 구현이 달라질 수 있음
        # MySQL에서 JSON 검색을 위한 방법
        filters.append(TradeMark.asignProductMainCodeList.cast(String).ilike(f"%{product_code}%"))
    
    # 모든 필터 조건 적용
    if filters:
        stmt = stmt.where(and_(*filters))
    
    # 전체 결과 개수 계산
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_count_result = await db.execute(count_stmt)
    total_count = total_count_result.scalar_one_or_none() or 0
    
    # 페이징 적용
    stmt = stmt.offset((page - 1) * size).limit(size)
    
    # 정렬 (출원일 기준 내림차순) - MySQL 호환 방식
    # NULLS LAST 대신 CASE 문 사용
    stmt = stmt.order_by(
        case(
            (TradeMark.applicationDate == None, 1),
            else_=0
        ),
        TradeMark.applicationDate.desc()
    )
    
    # 쿼리 실행
    result = await db.execute(stmt)
    items = result.scalars().all()
    
    return items, total_count


async def get_trademark_by_application_number(
    db: AsyncSession, 
    application_number: str
) -> Optional[TradeMark]:
    """
    출원번호로 단일 상표 정보 조회
    
    Args:
        db: 데이터베이스 세션
        application_number: 상표 출원번호
        
    Returns:
        조회된 상표 정보 또는 None
    """
    stmt = select(TradeMark).where(TradeMark.applicationNumber == application_number)
    result = await db.execute(stmt)
    return result.scalar_one_or_none() 