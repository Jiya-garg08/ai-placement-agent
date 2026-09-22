import pytest
from database.database import SessionLocal, init_db, get_db_context
from database.models.student import User, StudentProfile
from database.models.practice import PracticeAttempt, PracticeStreak
from database.models.learning_plan import LearningPlan, LearningPlanItem


@pytest.fixture
def clean_db():
    init_db()
    db = SessionLocal()
    yield db
    db.close()


def test_atomic_transaction_commit_success(clean_db):
    """Verify that multiple operations commit atomically when no error occurs."""
    db = clean_db
    user = User(name="Atomic Test User", email="atomic.test@example.com")
    db.add(user)
    db.flush()

    profile = StudentProfile(
        user_id=user.id,
        target_role="Software Development Engineer",
        primary_skills=["Python", "DSA"]
    )
    db.add(profile)
    db.commit()

    # Query back to verify persistence
    saved_user = db.query(User).filter_by(email="atomic.test@example.com").first()
    assert saved_user is not None
    assert saved_user.profile is not None
    assert saved_user.profile.target_role == "Software Development Engineer"

    # Cleanup
    db.delete(saved_user)
    db.commit()


def test_transaction_rollback_on_failure(clean_db):
    """Verify that an uncommitted transaction rolls back on exception without persisting partial records."""
    db = clean_db
    user = User(name="Rollback User", email="rollback.test@example.com")
    db.add(user)
    db.flush()

    # Attempt to insert an invalid record to trigger rollback
    try:
        # User id duplicate or invalid foreign key
        invalid_profile = StudentProfile(user_id=9999999, target_role="Invalid")
        db.add(invalid_profile)
        # Manually force a rollback simulation
        raise ValueError("Simulated database write error")
    except ValueError:
        db.rollback()

    # Verify user was NOT saved
    assert db.query(User).filter_by(email="rollback.test@example.com").first() is None


def test_get_db_context_manager_rollback(clean_db):
    """Verify get_db_context automatically rolls back when an exception is raised inside the with block."""
    with pytest.raises(RuntimeError):
        with get_db_context() as session:
            user = User(name="Context User", email="context.test@example.com")
            session.add(user)
            raise RuntimeError("Failure within context block")

    # Verify record was rolled back
    verify_session = SessionLocal()
    try:
        assert verify_session.query(User).filter_by(email="context.test@example.com").first() is None
    finally:
        verify_session.close()


def test_cascading_deletion(clean_db):
    """Verify cascading delete deletes student profile when user is deleted."""
    db = clean_db
    user = User(name="Cascade User", email="cascade.test@example.com")
    db.add(user)
    db.flush()

    profile = StudentProfile(user_id=user.id, target_role="SDE")
    db.add(profile)
    db.commit()

    prof_id = profile.id

    # Delete parent user
    db.delete(user)
    db.commit()

    # Verify profile was also deleted via cascade
    assert db.query(StudentProfile).filter_by(id=prof_id).first() is None
