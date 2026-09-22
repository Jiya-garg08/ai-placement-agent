import pytest
from database.database import SessionLocal, init_db
from database.models.student import User, StudentProfile
from mcp_service.tools.profile_tool import get_student_profile, update_student_target_role
from mcp_service.server.server import create_mcp_server


@pytest.fixture(autouse=True)
def setup_test_student():
    """Setup a sample student in the database."""
    init_db()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "mcp.student@example.com").first()
        if not user:
            user = User(email="mcp.student@example.com", name="MCP Student")
            db.add(user)
            db.commit()
            profile = StudentProfile(
                user_id=user.id,
                target_role="Software Development Engineer (SDE)",
                primary_skills=["Python", "Algorithms"]
            )
            db.add(profile)
            db.commit()
            db.refresh(user)
        return user
    finally:
        db.close()


def test_mcp_get_student_profile_success():
    db = SessionLocal()
    user = db.query(User).filter(User.email == "mcp.student@example.com").first()
    db.close()

    res = get_student_profile(user.id)
    assert res["status"] == "success"
    assert res["name"] == "MCP Student"
    assert res["target_role"] == "Software Development Engineer (SDE)"
    assert "Python" in res["primary_skills"]


def test_mcp_get_student_profile_not_found():
    res = get_student_profile(999999)
    assert res["status"] == "error"
    assert "not found" in res["message"]


def test_mcp_update_student_target_role():
    db = SessionLocal()
    user = db.query(User).filter(User.email == "mcp.student@example.com").first()
    db.close()

    res = update_student_target_role(
        student_id=user.id,
        target_role="Lead Backend Engineer",
        target_company_tier="Tier 1 / Product"
    )
    assert res["status"] == "success"
    assert res["target_role"] == "Lead Backend Engineer"

    # Verify persisted in database
    verified = get_student_profile(user.id)
    assert verified["target_role"] == "Lead Backend Engineer"


def test_create_mcp_server_initialization():
    server = create_mcp_server()
    assert server is not None
    assert server.name == "placement-prep-agent"
