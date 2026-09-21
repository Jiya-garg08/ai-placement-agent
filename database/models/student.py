from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.database import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User account entity representing a student account."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)

    # Relationships
    profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"


class StudentProfile(Base, TimestampMixin):
    """Detailed academic and placement preparation profile for a student."""
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    
    # Career targets
    target_role = Column(String(150), nullable=False, default="Software Development Engineer (SDE)")
    career_goal = Column(String(255), nullable=True)
    target_company_tier = Column(String(50), nullable=True, default="Tier 1 / Product")
    
    # Academic background
    college = Column(String(255), nullable=True)
    graduation_year = Column(Integer, nullable=True)
    current_semester = Column(Integer, nullable=True)
    
    # Initial skills declared by candidate (stored as JSON array of strings)
    primary_skills = Column(JSON, default=list, nullable=False)

    # Relationship back to user
    user = relationship("User", back_populates="profile")

    def __repr__(self) -> str:
        return f"<StudentProfile(id={self.id}, user_id={self.user_id}, target_role='{self.target_role}')>"
