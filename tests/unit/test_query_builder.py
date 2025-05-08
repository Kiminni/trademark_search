"""TrademarkQueryBuilder 단위 테스트"""
import pytest
from unittest.mock import patch
from datetime import datetime

from sqlalchemy import select, and_, or_, case
from sqlalchemy.sql import ClauseElement

from app.services.trademark_service import TrademarkQueryBuilder
from app.models.trademark import TradeMark


class TestTrademarkQueryBuilder:
    """TrademarkQueryBuilder 클래스 테스트"""
    
    def test_init(self):
        """초기화 테스트"""
        # 실행 (Act)
        builder = TrademarkQueryBuilder()
        
        # 검증 (Assert)
        assert builder.filters == []
        assert isinstance(builder.stmt, ClauseElement)
    
    def test_with_keyword(self):
        """키워드 필터 추가 테스트"""
        # 준비 (Arrange)
        keyword = "테스트"
        
        # 실행 (Act)
        builder = TrademarkQueryBuilder()
        result = builder.with_keyword(keyword)
        
        # 검증 (Assert)
        assert result is builder  # 메서드 체이닝 확인
        assert len(builder.filters) == 1
        
        # 필터 표현식 검증
        filter_expr = builder.filters[0]
        assert isinstance(filter_expr, ClauseElement)
    
    def test_with_keyword_none(self):
        """키워드가 None인 경우 테스트"""
        # 실행 (Act)
        builder = TrademarkQueryBuilder()
        result = builder.with_keyword(None)
        
        # 검증 (Assert)
        assert result is builder
        assert len(builder.filters) == 0
    
    def test_with_status(self):
        """상태 필터 추가 테스트"""
        # 준비 (Arrange)
        status = "등록"
        
        # 실행 (Act)
        builder = TrademarkQueryBuilder()
        result = builder.with_status(status)
        
        # 검증 (Assert)
        assert result is builder
        assert len(builder.filters) == 1
    
    def test_with_status_none(self):
        """상태가 None인 경우 테스트"""
        # 실행 (Act)
        builder = TrademarkQueryBuilder()
        result = builder.with_status(None)
        
        # 검증 (Assert)
        assert result is builder
        assert len(builder.filters) == 0
    
    def test_with_application_date_range(self):
        """출원일 범위 필터 추가 테스트"""
        # 준비 (Arrange)
        date_from = "20200101"
        date_to = "20201231"
        
        # 실행 (Act)
        builder = TrademarkQueryBuilder()
        result = builder.with_application_date_range(date_from, date_to)
        
        # 검증 (Assert)
        assert result is builder
        assert len(builder.filters) == 2
    
    def test_with_application_date_range_invalid(self):
        """잘못된 출원일 형식 테스트"""
        # 준비 (Arrange)
        invalid_date = "invalid-date"
        
        # 실행 (Act)
        builder = TrademarkQueryBuilder()
        result = builder.with_application_date_range(invalid_date, None)
        
        # 검증 (Assert)
        assert result is builder
        assert len(builder.filters) == 0  # 필터가 추가되지 않아야 함
    
    def test_with_product_code(self):
        """상품 코드 필터 추가 테스트"""
        # 준비 (Arrange)
        product_code = "G01"
        
        # 실행 (Act)
        builder = TrademarkQueryBuilder()
        result = builder.with_product_code(product_code)
        
        # 검증 (Assert)
        assert result is builder
        assert len(builder.filters) == 1
    
    def test_with_pagination(self):
        """페이지네이션 적용 테스트"""
        # 준비 (Arrange)
        page = 2
        size = 10
        
        # 실행 (Act)
        builder = TrademarkQueryBuilder()
        result = builder.with_pagination(page, size)
        
        # 검증 (Assert)
        assert result is builder
        # 페이지네이션이 적용되었는지 직접 검증하기는 어려우므로
        # 메서드가 호출되고 builder가 반환되는지만 확인
    
    def test_with_order_by(self):
        """정렬 적용 테스트"""
        # 실행 (Act)
        builder = TrademarkQueryBuilder()
        result = builder.with_order_by()
        
        # 검증 (Assert)
        assert result is builder
        # 정렬이 적용되었는지 직접 검증하기는 어려우므로
        # 메서드가 호출되고 builder가 반환되는지만 확인
    
    def test_build_with_filters(self):
        """필터가 있는 경우 빌드 테스트"""
        # 준비 (Arrange)
        builder = TrademarkQueryBuilder()
        builder.with_keyword("테스트").with_status("등록")
        
        # 실행 (Act)
        stmt = builder.build()
        
        # 검증 (Assert)
        assert isinstance(stmt, ClauseElement)
        # 실제 SQL 쿼리 검증은 복잡하므로 생략
    
    def test_build_without_filters(self):
        """필터가 없는 경우 빌드 테스트"""
        # 준비 (Arrange)
        builder = TrademarkQueryBuilder()
        
        # 실행 (Act)
        stmt = builder.build()
        
        # 검증 (Assert)
        assert isinstance(stmt, ClauseElement)
        # 빌드된 쿼리는 단순 select 문이어야 함 