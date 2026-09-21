import pytest
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
from database.database import Base, TimestampMixin, get_db_context
from database.repositories.base_repository import BaseRepository

# Define a simple test model for repository verification
class DummyModel(Base, TimestampMixin):
    __tablename__ = "dummy_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    category = Column(String(50), nullable=True)


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database session for unit tests."""
    test_engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_base_repository_crud(db_session):
    repo = BaseRepository(DummyModel, db_session)
    
    # 1. Create
    item = DummyModel(name="Test Item 1", category="DSA")
    created = repo.create(item)
    assert created.id is not None
    assert created.name == "Test Item 1"
    assert created.category == "DSA"
    assert created.created_at is not None

    # 2. Get by ID
    fetched = repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.name == "Test Item 1"

    # 3. List with filters
    item2 = DummyModel(name="Test Item 2", category="DBMS")
    repo.create(item2)
    
    all_items = repo.list()
    assert len(all_items) == 2

    dsa_items = repo.list(category="DSA")
    assert len(dsa_items) == 1
    assert dsa_items[0].name == "Test Item 1"

    # 4. Update
    updated = repo.update(fetched, {"name": "Updated Item 1"})
    assert updated.name == "Updated Item 1"

    # 5. Count
    assert repo.count() == 2
    assert repo.count(category="DBMS") == 1

    # 6. Delete
    deleted = repo.delete(created.id)
    assert deleted is True
    assert repo.get_by_id(created.id) is None
    assert repo.count() == 1
