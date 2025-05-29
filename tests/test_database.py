import pytest
from app.database.db_connector import get_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy import text


@pytest.fixture
def engine():
    return get_engine()


def test_connect_to_db(engine):
    try:
        with engine.connect() as connection:
            query = "SELECT 1"
            result = connection.execute(text(query))
            assert result.scalar() == 1
    except OperationalError:
        pytest.fail('Connection failed')
