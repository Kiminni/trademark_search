"""라우터 단위 테스트"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from app.routers.trademark_routes import search_trademarks_api, get_trademark_api
from app.services.trademark_service import SearchParams, TrademarkService


class TestTrademarkRoutes:
    """상표 라우터 테스트"""
    
    @pytest.mark.asyncio
    async def test_search_trademarks_api(self, mock_db_session):
        """상표 검색 API 테스트"""
        # 준비 (Arrange)
        expected_result = {
            "items": [{"id": 1, "productName": "테스트상표"}],
            "total_count": 1,
            "page": 1,
            "size": 10,
            "pages_count": 1
        }
        
        # TrademarkService.search_trademarks 메서드 목 설정
        with patch.object(
            TrademarkService, 
            'search_trademarks', 
            return_value=expected_result
        ) as mock_search:
            
            # 실행 (Act)
            result = await search_trademarks_api(
                keyword="테스트",
                status="등록",
                application_date_from="20200101",
                application_date_to="20201231",
                product_code="G01",
                page=1,
                size=10,
                db=mock_db_session
            )
            
            # 검증 (Assert)
            assert mock_search.call_count == 1
            
            # mock_search가 호출되었는지만 검증 (파라미터 세부 검증은 생략)
            mock_search.assert_called_once()
            
            # 결과가 예상대로인지 확인
            assert result == expected_result
    
    @pytest.mark.asyncio
    async def test_search_trademarks_api_error(self, mock_db_session):
        """상표 검색 API 오류 처리 테스트"""
        # 준비 (Arrange)
        # 예외 발생 상황 시뮬레이션
        with patch.object(
            TrademarkService, 
            'search_trademarks', 
            side_effect=Exception("검색 오류")
        ) as mock_search:
            
            # 실행 및 검증 (Act & Assert)
            with pytest.raises(HTTPException) as excinfo:
                await search_trademarks_api(
                    keyword="테스트",
                    db=mock_db_session
                )
            
            # 올바른 상태 코드로 예외가 발생했는지 확인
            assert excinfo.value.status_code == 500
            assert "내부 서버 오류" in excinfo.value.detail
    
    @pytest.mark.asyncio
    async def test_get_trademark_api(self, mock_db_session, sample_trademark_data):
        """출원번호로 상표 조회 API 테스트"""
        # 준비 (Arrange)
        app_number = "4020200012345"
        
        # TrademarkService.get_trademark_by_application_number 메서드 목 설정
        with patch.object(
            TrademarkService, 
            'get_trademark_by_application_number', 
            return_value=sample_trademark_data
        ) as mock_get:
            
            # 실행 (Act)
            result = await get_trademark_api(
                application_number=app_number,
                db=mock_db_session
            )
            
            # 검증 (Assert)
            mock_get.assert_awaited_once_with(app_number)
            assert result == sample_trademark_data
    
    @pytest.mark.asyncio
    async def test_get_trademark_api_not_found(self, mock_db_session):
        """존재하지 않는 상표 조회 API 테스트"""
        # 준비 (Arrange)
        app_number = "9999999999999"
        
        # TrademarkService.get_trademark_by_application_number 메서드 목 설정
        with patch.object(
            TrademarkService, 
            'get_trademark_by_application_number', 
            return_value=None
        ) as mock_get:
            
            # 실행 및 검증 (Act & Assert)
            with pytest.raises(HTTPException) as excinfo:
                await get_trademark_api(
                    application_number=app_number,
                    db=mock_db_session
                )
            
            # 올바른 상태 코드로 예외가 발생했는지 확인
            assert excinfo.value.status_code == 404
            assert app_number in excinfo.value.detail 