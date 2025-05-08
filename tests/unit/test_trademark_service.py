"""TrademarkService 단위 테스트"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call

from app.services.trademark_service import (
    TrademarkService, 
    TrademarkRepository, 
    SearchParams
)


class TestTrademarkService:
    """TrademarkService 클래스 테스트"""
    
    @pytest.mark.asyncio
    async def test_search_trademarks(self, mock_db_session, sample_trademark_orm):
        """상표 검색 기능 테스트"""
        # 준비 (Arrange)
        # 리포지토리 메서드 목 설정
        with patch.object(
            TrademarkRepository, 
            'search', 
            return_value=([sample_trademark_orm], 1)
        ) as mock_search:
            
            # 검색 파라미터 설정
            params = SearchParams(
                keyword="테스트",
                status="등록",
                page=1,
                size=10
            )
            
            # 실행 (Act)
            service = TrademarkService(mock_db_session)
            result = await service.search_trademarks(params)
            
            # 검증 (Assert)
            # 리포지토리의 search 메서드가 올바른 파라미터로 호출되었는지 확인
            mock_search.assert_awaited_once_with(params)
            
            # 결과가 예상대로인지 확인
            assert result["total_count"] == 1
            assert len(result["items"]) == 1
            assert result["page"] == 1
            assert result["size"] == 10
            assert result["pages_count"] == 1
            
            # 반환된 아이템이 딕셔너리로 변환되었는지 확인
            item = result["items"][0]
            assert item["id"] == sample_trademark_orm.id
            assert item["productName"] == sample_trademark_orm.productName
            assert item["applicationNumber"] == sample_trademark_orm.applicationNumber
    
    @pytest.mark.asyncio
    async def test_search_trademarks_empty_result(self, mock_db_session):
        """검색 결과가 없는 경우 테스트"""
        # 준비 (Arrange)
        with patch.object(
            TrademarkRepository, 
            'search', 
            return_value=([], 0)
        ) as mock_search:
            
            params = SearchParams(keyword="존재하지않는상표")
            
            # 실행 (Act)
            service = TrademarkService(mock_db_session)
            result = await service.search_trademarks(params)
            
            # 검증 (Assert)
            assert result["total_count"] == 0
            assert len(result["items"]) == 0
            assert result["pages_count"] == 0
    
    @pytest.mark.asyncio
    async def test_get_trademark_by_application_number(self, mock_db_session, sample_trademark_orm):
        """출원번호로 상표 조회 테스트"""
        # 준비 (Arrange)
        app_number = "4020200012345"
        
        with patch.object(
            TrademarkRepository, 
            'get_by_application_number', 
            return_value=sample_trademark_orm
        ) as mock_get:
            
            # 실행 (Act)
            service = TrademarkService(mock_db_session)
            result = await service.get_trademark_by_application_number(app_number)
            
            # 검증 (Assert)
            mock_get.assert_awaited_once_with(app_number)
            assert result["id"] == sample_trademark_orm.id
            assert result["productName"] == sample_trademark_orm.productName
            assert result["applicationNumber"] == app_number
    
    @pytest.mark.asyncio
    async def test_get_trademark_not_found(self, mock_db_session):
        """존재하지 않는 상표 조회 테스트"""
        # 준비 (Arrange)
        app_number = "9999999999999"
        
        with patch.object(
            TrademarkRepository, 
            'get_by_application_number', 
            return_value=None
        ) as mock_get:
            
            # 실행 (Act)
            service = TrademarkService(mock_db_session)
            result = await service.get_trademark_by_application_number(app_number)
            
            # 검증 (Assert)
            mock_get.assert_awaited_once_with(app_number)
            assert result is None
    
    def test_convert_to_dict(self, mock_db_session, sample_trademark_orm):
        """ORM 모델을 딕셔너리로 변환하는 기능 테스트"""
        # 준비 (Arrange)
        service = TrademarkService(mock_db_session)
        
        # 실행 (Act)
        result = service._convert_to_dict(sample_trademark_orm)
        
        # 검증 (Assert)
        assert result["id"] == sample_trademark_orm.id
        assert result["productName"] == sample_trademark_orm.productName
        assert result["productNameEng"] == sample_trademark_orm.productNameEng
        assert result["applicationNumber"] == sample_trademark_orm.applicationNumber
        assert result["asignProductMainCodeList"] == sample_trademark_orm.asignProductMainCodeList 