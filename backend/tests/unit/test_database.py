import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.target import Target

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()

def test_target_creation(db_session):
    target = Target(name="test.com", type="domain", value="test.com")
    db_session.add(target)
    db_session.commit()
    assert target.id is not None
