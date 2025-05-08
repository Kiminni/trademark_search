"""테스트를 위한 공통 픽스처와 설정"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trademark import TradeMark


@pytest.fixture
def mock_db_session():
    """데이터베이스 세션을 목업하는 픽스처"""
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def sample_trademark_data():
    """샘플 상표 데이터"""
    return {
        "id": 1,
        "productName": "테스트상표",
        "productNameEng": "Test Trademark",
        "applicationNumber": "4020200012345",
        "applicationDate": "2020-01-01",
        "registerStatus": "등록",
        "publicationNumber": "4020200054321",
        "publicationDate": "2020-02-01",
        "registrationNumber": "4000123456",
        "registrationDate": "2020-03-01",
        "internationalRegNumbers": None,
        "internationalRegDate": None,
        "priorityClaimNumList": ["US123456", "EU654321"],
        "priorityClaimDateList": ["2019-12-01", "2019-12-15"],
        "asignProductMainCodeList": ["G01", "G02"],
        "asignProductSubCodeList": ["G0101", "G0201"],
        "viennaCodeList": ["01.01", "02.01"]
    }


@pytest.fixture
def sample_trademark_orm():
    """ORM 모델 형태의 샘플 상표 데이터"""
    trademark = MagicMock(spec=TradeMark)
    trademark.id = 1
    trademark.productName = "테스트상표"
    trademark.productNameEng = "Test Trademark"
    trademark.applicationNumber = "4020200012345"
    trademark.applicationDate = "2020-01-01"
    trademark.registerStatus = "등록"
    trademark.publicationNumber = "4020200054321"
    trademark.publicationDate = "2020-02-01"
    trademark.registrationNumber = "4000123456"
    trademark.registrationDate = "2020-03-01"
    trademark.internationalRegNumbers = None
    trademark.internationalRegDate = None
    trademark.priorityClaimNumList = ["US123456", "EU654321"]
    trademark.priorityClaimDateList = ["2019-12-01", "2019-12-15"]
    trademark.asignProductMainCodeList = ["G01", "G02"]
    trademark.asignProductSubCodeList = ["G0101", "G0201"]
    trademark.viennaCodeList = ["01.01", "02.01"]
    return trademark 