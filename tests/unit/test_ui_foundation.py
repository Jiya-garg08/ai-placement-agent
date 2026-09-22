import pytest
from pathlib import Path
from database.database import SessionLocal, init_db
from app.utils.ui_helpers import (
    ensure_seed_data,
    get_student_profile_data,
    list_all_students,
    render_kpi_card
)
from app.utils.seed_demo_student import seed_demo_candidate
from services.analytics_service import AnalyticsService
from services.next_action_service import NextActionService


@pytest.fixture(scope="module")
def setup_test_db():
    init_db()
    db = SessionLocal()
    pid = ensure_seed_data()
    yield pid
    db.close()


def test_ensure_seed_data(setup_test_db):
    pid = setup_test_db
    assert pid is not None
    assert pid > 0


def test_get_student_profile_data(setup_test_db):
    pid = setup_test_db
    data = get_student_profile_data(pid)
    assert data is not None
    assert data["name"] == "Jiya Garg"
    assert data["email"] == "jiya.garg@example.com"
    assert "Software Development Engineer" in data["target_role"]
    assert data["readiness_score"] > 0
    assert data["current_streak"] >= 0
    assert isinstance(data["strong_skills"], list)


def test_list_all_students(setup_test_db):
    students = list_all_students()
    assert len(students) >= 1
    first = students[0]
    assert "name" in first
    assert "target_role" in first
    assert "email" in first


def test_custom_css_file_exists():
    css_path = Path("app/assets/style.css")
    assert css_path.exists()
    content = css_path.read_text(encoding="utf-8")
    assert ".kpi-card" in content
    assert ".action-card" in content


def test_render_kpi_card():
    html = render_kpi_card(
        title="Readiness Index",
        value="82.4%",
        delta="+5.2%",
        delta_type="positive"
    )
    assert "kpi-card" in html
    assert "Readiness Index" in html
    assert "82.4%" in html
    assert "+5.2%" in html
    assert "delta-positive" in html


def test_dashboard_data_pipeline(setup_test_db):
    pid = setup_test_db
    db = SessionLocal()
    try:
        analytics = AnalyticsService(session=db)
        masteries = analytics.get_topic_mastery_breakdown(pid)
        assert len(masteries) >= 5

        velocity = analytics.calculate_learning_velocity(pid)
        assert velocity.streak_days >= 0
        assert velocity.trend in ["Accelerating", "Consistent", "Decelerating"]

        radar = analytics.get_radar_chart_data(masteries)
        assert "DSA" in radar
        assert "DBMS" in radar

        next_action_svc = NextActionService(session=db, analytics_service=analytics)
        actions = next_action_svc.get_saved_actions(pid)
        assert len(actions) >= 1
        first_act = actions[0]
        assert first_act.priority in ["HIGH", "MEDIUM", "LOW"]
        assert first_act.target_page in ["Practice", "Assessments", "Tutor", "Roadmap"]
    finally:
        db.close()
