import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.database import Base
from database.models.student import User, StudentProfile
from database.models.skill_gap import SkillGap
from database.models.learning_plan import LearningPlan, LearningPlanItem
from database.repositories.plan_repository import LearningPlanRepository
from agents.planner_agent.planner_agent import LearningPlannerAgent
from schemas.plan_schema import LearningPlanStructure


@pytest.fixture
def db_session():
    """Create in-memory SQLite database session."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        user = User(email="planner.test@example.com", name="Plan Tester")
        session.add(user)
        session.commit()
        profile = StudentProfile(user_id=user.id, target_role="Software Development Engineer (SDE)")
        session.add(profile)
        session.commit()
        yield session
    finally:
        session.close()


def test_planner_agent_mock_generation():
    agent = LearningPlannerAgent(mock_mode=True)
    gap = SkillGap(
        profile_id=1,
        weak_skills=["Operating Systems (33%)"],
        missing_skills=["Computer Networks", "Redis"],
        priority_topics=[
            {"topic": "Operating Systems", "urgency": "High", "rationale": "Test failure"},
            {"topic": "Computer Networks", "urgency": "High", "rationale": "Missing JD skill"}
        ],
        strong_skills=["Python", "SQL"]
    )

    plan = agent.generate_plan(target_role="Software Development Engineer (SDE)", skill_gap=gap)

    assert isinstance(plan, LearningPlanStructure)
    assert plan.total_weeks == 4
    assert len(plan.items) >= 4
    
    # Check that week 1 or week 2 targets the weak/missing topics
    topics = [item.topic for item in plan.items]
    assert any("Operating Systems" in t for t in topics)
    assert any("Computer Networks" in t for t in topics)


def test_plan_repository_persistence_and_status_update(db_session):
    agent = LearningPlannerAgent(mock_mode=True)
    structure = agent.generate_plan(target_role="Backend Engineer")

    repo = LearningPlanRepository(db_session)
    saved_plan = repo.create_plan_with_items(profile_id=1, structure=structure)

    assert saved_plan.id is not None
    assert saved_plan.is_active is True
    assert len(saved_plan.items) == len(structure.items)

    first_item = saved_plan.items[0]
    assert first_item.status == "In Progress"

    # Update item status to Completed
    updated = repo.update_item_status(first_item.id, "Completed")
    assert updated is not None
    assert updated.status == "Completed"

    # Test creating another plan deactivates previous
    new_structure = agent.generate_plan(target_role="Full Stack Engineer")
    plan2 = repo.create_plan_with_items(profile_id=1, structure=new_structure)
    
    assert plan2.id != saved_plan.id
    assert plan2.is_active is True
    
    # Reload saved_plan from DB to confirm it is now inactive
    old_plan = repo.get_by_id(saved_plan.id)
    assert old_plan.is_active is False
