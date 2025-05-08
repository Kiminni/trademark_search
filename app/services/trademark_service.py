from typing import List, Tuple, Optional, Any, Dict, TypedDict
from sqlalchemy import select, func, or_, and_, cast, String, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import cast
from datetime import datetime, date
from fastapi import status as http_status
from pydantic import BaseModel 

from app.models.trademark import TradeMark
from app.schemas.trademark import TradeMarkCreate


# 검색 파라미터 타입 정의
class SearchParams(BaseModel):
    keyword: Optional[str] = None
    status: Optional[str] = None
    application_date_from: Optional[str] = None
    application_date_to: Optional[str] = None
    product_code: Optional[str] = None
    page: int = 1
    size: int = 10


# 검색 결과 타입 정의
class SearchResult(TypedDict):
    items: List[Dict[str, Any]]
    total_count: int
    page: int
    size: int
    pages_count: int


class TrademarkQueryBuilder:
    """상표 검색 쿼리 빌더 클래스"""
    
    def __init__(self):
        self.stmt = select(TradeMark)
        self.filters = []
    
    def with_keyword(self, keyword: Optional[str]) -> 'TrademarkQueryBuilder':
        """키워드 검색 필터 추가"""
        if keyword:
            self.filters.append(
                or_(
                    TradeMark.productName.ilike(f"%{keyword}%"),
                    TradeMark.productNameEng.ilike(f"%{keyword}%")
                )
            )
        return self
    
    def with_status(self, status: Optional[str]) -> 'TrademarkQueryBuilder':
        """등록 상태 필터 추가"""
        if status:
            self.filters.append(TradeMark.registerStatus == status)
        return self
    
    def with_application_date_range(
        self, 
        date_from: Optional[str], 
        date_to: Optional[str]
    ) -> 'TrademarkQueryBuilder':
        """출원일 범위 필터 추가"""
        if date_from:
            try:
                parsed_date = datetime.strptime(date_from, "%Y%m%d").date()
                self.filters.append(TradeMark.applicationDate >= parsed_date)
            except ValueError:
                pass
                
        if date_to:
            try:
                parsed_date = datetime.strptime(date_to, "%Y%m%d").date()
                self.filters.append(TradeMark.applicationDate <= parsed_date)
            except ValueError:
                pass
        
        return self
    
    def with_product_code(self, product_code: Optional[str]) -> 'TrademarkQueryBuilder':
        """상품 분류 코드 필터 추가"""
        if product_code:
            self.filters.append(
                TradeMark.asignProductMainCodeList.cast(String).ilike(f"%{product_code}%")
            )
        return self
    
    def with_pagination(self, page: int, size: int) -> 'TrademarkQueryBuilder':
        """페이지네이션 적용"""
        self.stmt = self.stmt.offset((page - 1) * size).limit(size)
        return self
    
    def with_order_by(self) -> 'TrademarkQueryBuilder':
        """정렬 조건 적용 (MySQL 호환)"""
        self.stmt = self.stmt.order_by(
            case(
                (TradeMark.applicationDate == None, 1),
                else_=0
            ),
            TradeMark.applicationDate.desc()
        )
        return self
    
    def build(self) -> Any:
        """최종 쿼리 빌드"""
        if self.filters:
            self.stmt = self.stmt.where(and_(*self.filters))
        return self.stmt


class TrademarkRepository:
    """상표 데이터 접근 레이어"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def count(self, stmt: Any) -> int:
        """쿼리 결과 개수 조회"""
        count_stmt = select(func.count()).select_from(stmt.subquery())
        result = await self.db.execute(count_stmt)
        return result.scalar_one_or_none() or 0
    
    async def search(self, params: SearchParams) -> Tuple[List[TradeMark], int]:
        """상표 검색 수행"""
        # 쿼리 빌더로 쿼리 구성
        query = (TrademarkQueryBuilder()
            .with_keyword(params.keyword)
            .with_status(params.status)
            .with_application_date_range(params.application_date_from, params.application_date_to)
            .with_product_code(params.product_code)
            .build()
        )
        
        # 전체 개수 계산
        total_count = await self.count(query)
        
        # 페이지네이션 및 정렬 적용
        final_query = (TrademarkQueryBuilder()
            .with_keyword(params.keyword)
            .with_status(params.status)
            .with_application_date_range(params.application_date_from, params.application_date_to)
            .with_product_code(params.product_code)
            .with_pagination(params.page, params.size)
            .with_order_by()
            .build()
        )
        
        # 쿼리 실행
        result = await self.db.execute(final_query)
        items = result.scalars().all()
        
        return items, total_count
    
    async def get_by_application_number(self, application_number: str) -> Optional[TradeMark]:
        """출원번호로 상표 조회"""
        stmt = select(TradeMark).where(TradeMark.applicationNumber == application_number)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class TrademarkService:
    """상표 검색 비즈니스 로직 레이어"""
    
    def __init__(self, db: AsyncSession):
        self.repository = TrademarkRepository(db)
    
    async def search_trademarks(self, params: SearchParams) -> SearchResult:
        """상표 검색 수행"""
        items, total_count = await self.repository.search(params)
        
        # ORM 객체를 딕셔너리로 변환
        items_dict = [self._convert_to_dict(item) for item in items]
        
        # 결과 페이지 수 계산
        pages_count = (total_count + params.size - 1) // params.size if total_count > 0 else 0
        
        # 최종 결과 생성
        return {
            "items": items_dict,
            "total_count": total_count,
            "page": params.page,
            "size": params.size,
            "pages_count": pages_count
        }
    
    async def get_trademark_by_application_number(self, application_number: str) -> Optional[Dict[str, Any]]:
        """출원번호로 상표 조회"""
        trademark = await self.repository.get_by_application_number(application_number)
        if not trademark:
            return None
        return self._convert_to_dict(trademark)
    
    def _convert_to_dict(self, model: TradeMark) -> Dict[str, Any]:
        """ORM 모델을 딕셔너리로 변환"""
        return {
            "id": model.id,
            "productName": model.productName,
            "productNameEng": model.productNameEng,
            "applicationNumber": model.applicationNumber,
            "applicationDate": model.applicationDate.isoformat() if model.applicationDate else None,
            "registerStatus": model.registerStatus,
            "publicationNumber": model.publicationNumber,
            "publicationDate": model.publicationDate.isoformat() if model.publicationDate else None,
            "registrationNumber": model.registrationNumber,
            "registrationDate": model.registrationDate,
            "registrationPubNumber": getattr(model, "registrationPubNumber", None),
            "registrationPubDate": getattr(model, "registrationPubDate", None),
            "internationalRegNumbers": model.internationalRegNumbers,
            "internationalRegDate": model.internationalRegDate.isoformat() if model.internationalRegDate else None,
            "priorityClaimNumList": model.priorityClaimNumList,
            "priorityClaimDateList": model.priorityClaimDateList,
            "asignProductMainCodeList": model.asignProductMainCodeList,
            "asignProductSubCodeList": model.asignProductSubCodeList,
            "viennaCodeList": model.viennaCodeList
        }


# 이전 버전 호환을 위한 함수들 (라우터에서 직접 호출 가능)
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
    """상표 검색 서비스 함수 (이전 버전과 호환)"""
    service = TrademarkService(db)
    params = SearchParams(
        keyword=keyword,
        status=status,
        application_date_from=application_date_from,
        application_date_to=application_date_to,
        product_code=product_code,
        page=page,
        size=size
    )
    result = await service.search_trademarks(params)
    # 원래 함수는 (items, total_count) 튜플을 반환했으므로 호환성 유지
    return result["items"], result["total_count"]

async def get_trademark_by_application_number(
    db: AsyncSession, 
    application_number: str
) -> Optional[TradeMark]:
    """출원번호로 단일 상표 정보 조회 (이전 버전과 호환)"""
    service = TrademarkService(db)
    return await service.repository.get_by_application_number(application_number) 