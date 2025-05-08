"""TrademarkRepository 단위 테스트"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.trademark_service import TrademarkRepository, SearchParams, TrademarkQueryBuilder


class TestTrademarkRepository:
    """TrademarkRepository 클래스 테스트"""
    
    @pytest.mark.asyncio
    async def test_count(self, mock_db_session):
        """레포지토리 count 메서드 테스트"""
        # 준비 (Arrange)
        # DB 실행 결과 목 설정
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = 5
        mock_db_session.execute.return_value = mock_result
        
        # 테스트 쿼리 생성
        test_stmt = select(1)
        
        # 실행 (Act)
        repo = TrademarkRepository(mock_db_session)
        count = await repo.count(test_stmt)
        
        # 검증 (Assert)
        mock_db_session.execute.assert_called_once()
        assert count == 5
    
    @pytest.mark.asyncio
    async def test_search(self, mock_db_session, sample_trademark_orm):
        """레포지토리 search 메서드 테스트"""
        # 준비 (Arrange)
        # 쿼리 빌더 목 설정
        with patch.object(
            TrademarkQueryBuilder, 
            'build', 
            return_value=select(1)  # 테스트를 위한 간단한 쿼리
        ) as mock_build:
            
            # DB 실행 결과 목 설정 (count 메서드용)
            mock_count_result = MagicMock()
            mock_count_result.scalar_one_or_none.return_value = 1
            
            # DB 실행 결과 목 설정 (검색 결과용)
            mock_search_result = MagicMock()
            mock_search_result.scalars.return_value.all.return_value = [sample_trademark_orm]
            
            # DB 실행 순서대로 반환값 설정
            mock_db_session.execute.side_effect = [
                mock_count_result,  # 첫 번째 호출: count 쿼리
                mock_search_result  # 두 번째 호출: 데이터 쿼리
            ]
            
            # 검색 파라미터 생성
            params = SearchParams(
                keyword="테스트",
                page=1,
                size=10
            )
            
            # 실행 (Act)
            repo = TrademarkRepository(mock_db_session)
            items, count = await repo.search(params)
            
            # 검증 (Assert)
            # 쿼리 빌더가 두 번 호출되었는지 (count용, 데이터용)
            assert mock_build.call_count == 2
            
            # DB session execute가 두 번 호출되었는지
            assert mock_db_session.execute.call_count == 2
            
            # 반환 값이 예상대로인지
            assert count == 1
            assert len(items) == 1
            assert items[0] == sample_trademark_orm
    
    @pytest.mark.asyncio
    async def test_get_by_application_number(self, mock_db_session, sample_trademark_orm):
        """출원번호로 상표 조회 테스트"""
        # 준비 (Arrange)
        app_number = "4020200012345"
        
        # DB 실행 결과 목 설정
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_trademark_orm
        mock_db_session.execute.return_value = mock_result
        
        # 실행 (Act)
        repo = TrademarkRepository(mock_db_session)
        result = await repo.get_by_application_number(app_number)
        
        # 검증 (Assert)
        mock_db_session.execute.assert_called_once()
        assert result == sample_trademark_orm
    
    @pytest.mark.asyncio
    async def test_get_by_application_number_not_found(self, mock_db_session):
        """존재하지 않는 출원번호 조회 테스트"""
        # 준비 (Arrange)
        app_number = "9999999999999"
        
        # DB 실행 결과 목 설정
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # 실행 (Act)
        repo = TrademarkRepository(mock_db_session)
        result = await repo.get_by_application_number(app_number)
        
        # 검증 (Assert)
        mock_db_session.execute.assert_called_once()
        assert result is None 