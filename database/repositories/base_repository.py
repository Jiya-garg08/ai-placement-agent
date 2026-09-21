from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from sqlalchemy.orm import Session
from database.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic base repository providing clean CRUD operations for SQLAlchemy models."""

    def __init__(self, model: Type[ModelType], session: Session):
        self.model = model
        self.session = session

    def get_by_id(self, id: Any) -> Optional[ModelType]:
        """Fetch a single record by primary key."""
        return self.session.query(self.model).filter(self.model.id == id).first()

    def list(self, skip: int = 0, limit: int = 100, **filters: Any) -> List[ModelType]:
        """List records with optional limit, offset, and simple equality filtering."""
        query = self.session.query(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.filter(getattr(self.model, key) == value)
        return query.offset(skip).limit(limit).all()

    def create(self, obj_in: ModelType) -> ModelType:
        """Persist a new model instance."""
        self.session.add(obj_in)
        self.session.commit()
        self.session.refresh(obj_in)
        return obj_in

    def update(self, db_obj: ModelType, update_data: Dict[str, Any]) -> ModelType:
        """Update fields of an existing model instance."""
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def delete(self, id: Any) -> bool:
        """Delete a record by primary key. Returns True if deleted, False if not found."""
        obj = self.get_by_id(id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
            return True
        return False

    def count(self, **filters: Any) -> int:
        """Count total records matching optional equality filters."""
        query = self.session.query(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.filter(getattr(self.model, key) == value)
        return query.count()
