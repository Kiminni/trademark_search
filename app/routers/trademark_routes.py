from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi import status as http_status
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.trademark_service import search_trademarks, get_trademark_by_application_number
from app.schemas.trademark import TradeMark

router = APIRouter(
    prefix="/api/trademarks",
    tags=["상표 검색"]
)

@router.get("/search")
async def search_trademarks_api(
    keyword: Optional[str] = Query(None, description="상표명 검색 키워드 (한글/영문)"),
    status: Optional[str] = Query(None, description="등록 상태 (등록, 실효, 거절, 출원 등)"),
    application_date_from: Optional[str] = Query(None, description="출원일 시작 (YYYYMMDD)", regex=r"^\d{8}$"),
    application_date_to: Optional[str] = Query(None, description="출원일 종료 (YYYYMMDD)", regex=r"^\d{8}$"),
    product_code: Optional[str] = Query(None, description="상품 주 분류 코드"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 당 결과 수"),
    db: AsyncSession = Depends(get_db)
):
    """
    상표 검색 API
    
    다양한 조건으로 상표를 검색합니다:
    - 키워드: 상표명(한글/영문)에서 부분 일치 검색
    - 등록 상태: 등록, 실효, 거절, 출원 등
    - 출원일 범위: YYYYMMDD 형식
    - 상품 분류 코드: 상품 주 분류 코드
    
    결과는 페이징되어 반환됩니다.
    """
    try:
        items, total_count = await search_trademarks(
            db=db,
            keyword=keyword,
            status=status,
            application_date_from=application_date_from, 
            application_date_to=application_date_to,
            product_code=product_code,
            page=page,
            size=size
        )
        
        # SQLAlchemy 모델을 dict로 변환
        items_dict = []
        for item in items:
            item_dict = {
                "id": item.id,
                "productName": item.productName,
                "productNameEng": item.productNameEng,
                "applicationNumber": item.applicationNumber,
                "applicationDate": item.applicationDate.isoformat() if item.applicationDate else None,
                "registerStatus": item.registerStatus,
                "publicationNumber": item.publicationNumber,
                "publicationDate": item.publicationDate.isoformat() if item.publicationDate else None,
                "registrationNumber": item.registrationNumber,
                "registrationDate": item.registrationDate,
                "registrationPubNumber": getattr(item, "registrationPubNumber", None),
                "registrationPubDate": getattr(item, "registrationPubDate", None),
                "internationalRegNumbers": item.internationalRegNumbers,
                "internationalRegDate": item.internationalRegDate.isoformat() if item.internationalRegDate else None,
                "priorityClaimNumList": item.priorityClaimNumList,
                "priorityClaimDateList": item.priorityClaimDateList,
                "asignProductMainCodeList": item.asignProductMainCodeList,
                "asignProductSubCodeList": item.asignProductSubCodeList,
                "viennaCodeList": item.viennaCodeList
            }
            items_dict.append(item_dict)
        
        return {
            "total_count": total_count,
            "items": items_dict,  # dict로 변환된 아이템들
            "page": page,
            "size": size,
            "pages_count": (total_count + size - 1) // size if total_count > 0 else 0
        }
        
    except Exception as e:
        # 실제 서비스에서는 로깅 추가
        print(f"검색 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="검색 처리 중 내부 서버 오류가 발생했습니다."
        )

@router.get("/{application_number}")
async def get_trademark_api(
    application_number: str,
    db: AsyncSession = Depends(get_db)
):
    """
    출원번호로 단일 상표 정보 조회 API
    
    Args:
        application_number: 상표 출원번호
    """
    trademark = await get_trademark_by_application_number(db, application_number)
    if not trademark:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"출원번호 '{application_number}'에 해당하는 상표를 찾을 수 없습니다."
        )
    
    # SQLAlchemy 모델을 dict로 변환
    result = {
        "id": trademark.id,
        "productName": trademark.productName,
        "productNameEng": trademark.productNameEng,
        "applicationNumber": trademark.applicationNumber,
        "applicationDate": trademark.applicationDate.isoformat() if trademark.applicationDate else None,
        "registerStatus": trademark.registerStatus,
        "publicationNumber": trademark.publicationNumber,
        "publicationDate": trademark.publicationDate.isoformat() if trademark.publicationDate else None,
        "registrationNumber": trademark.registrationNumber,
        "registrationDate": trademark.registrationDate,
        "registrationPubNumber": getattr(trademark, "registrationPubNumber", None),
        "registrationPubDate": getattr(trademark, "registrationPubDate", None),
        "internationalRegNumbers": trademark.internationalRegNumbers,
        "internationalRegDate": trademark.internationalRegDate.isoformat() if trademark.internationalRegDate else None,
        "priorityClaimNumList": trademark.priorityClaimNumList,
        "priorityClaimDateList": trademark.priorityClaimDateList,
        "asignProductMainCodeList": trademark.asignProductMainCodeList,
        "asignProductSubCodeList": trademark.asignProductSubCodeList,
        "viennaCodeList": trademark.viennaCodeList
    }
    
    return result 