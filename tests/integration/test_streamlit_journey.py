import io
import pytest
from database.database import SessionLocal, init_db
from database.models.student import User, StudentProfile
from database.models.skill_gap import SkillGap
from database.models.learning_plan import LearningPlan, LearningPlanItem
from database.models.recommendation import NextBestAction
from app.utils.seed_demo_student import seed_demo_candidate
from services.resume_service import ResumeService
from services.jd_parser import JobDescriptionParser
from services.assessment_service import AssessmentService
from services.skill_gap_service import SkillGapService
from services.practice_service import PracticeService
from services.next_action_service import NextActionService
from agents.resume_agent.resume_agent import ResumeAnalysisAgent
from agents.planner_agent.planner_agent import LearningPlannerAgent
from agents.tutor_agent.tutor_agent import RAGTutorAgent
from agents.evaluation_agent.evaluation_agent import PerformanceEvaluationAgent
from agents.recommendation_agent.recommendation_agent import NextActionRecommendationAgent
from schemas.assessment_schema import AssessmentSubmission, AssessmentAnswerSubmission
from schemas.practice_schema import PracticeSubmissionRequest
from schemas.rag_schema import TutorQueryRequest


@pytest.fixture(scope="module")
def journey_student():
    init_db()
    db = SessionLocal()
    profile = seed_demo_candidate(session=db)
    pid = profile.id
    db.close()
    return pid


def test_journey_stage1_dashboard_telemetry(journey_student):
    """Stage 1: Verify dashboard data pipeline renders all KPIs, radar data, and velocity."""
    db = SessionLocal()
    try:
        from services.analytics_service import AnalyticsService
        analytics = AnalyticsService(session=db)
        mastery = analytics.get_topic_mastery_breakdown(journey_student)
        assert len(mastery) >= 5

        radar = analytics.get_radar_chart_data(mastery)
        assert len(radar) >= 5

        readiness = analytics.compute_placement_readiness_index(mastery, "Software Development Engineer (SDE 1)")
        assert 0.0 <= readiness <= 100.0

        velocity = analytics.calculate_learning_velocity(journey_student)
        assert velocity.streak_days >= 0
    finally:
        db.close()


def test_journey_stage2_student_profile_update(journey_student):
    """Stage 2: Verify candidate profile modification and persistence."""
    db = SessionLocal()
    try:
        prof = db.query(StudentProfile).filter_by(id=journey_student).first()
        assert prof is not None
        orig_goal = prof.career_goal

        prof.career_goal = "Targeting Staff Systems Engineer Offer"
        db.commit()

        updated_prof = db.query(StudentProfile).filter_by(id=journey_student).first()
        assert updated_prof.career_goal == "Targeting Staff Systems Engineer Offer"

        # Restore
        prof.career_goal = orig_goal
        db.commit()
    finally:
        db.close()


def test_journey_stage3_resume_jd_analysis():
    """Stage 3: Verify resume & JD ATS parsing, PII redaction, and competency extraction."""
    sample_resume = (
        "Alice Smith\nEmail: alice@example.com\nPhone: 123-456-7890\n"
        "Technical Skills: Python, Java, SQL, Data Structures, Algorithms, Docker\n"
        "Experience: Software Engineer Intern at CloudCorp"
    )
    sample_jd = (
        "Role: Software Development Engineer (SDE 1)\n"
        "Required Skills: Python, SQL, Data Structures\n"
        "Preferred Skills: Docker, Kubernetes"
    )

    stream = io.BytesIO(sample_resume.encode("utf-8"))
    parsed_resume = ResumeService.parse_resume(stream, "test_resume.txt")
    assert "alice@example.com" not in parsed_resume.redacted_text
    assert "[EMAIL_REDACTED]" in parsed_resume.redacted_text

    parsed_jd = JobDescriptionParser.parse(sample_jd)
    assert "Software Development Engineer" in parsed_jd.role_title
    assert "Python" in parsed_jd.required_skills

    agent = ResumeAnalysisAgent(mock_mode=True)
    extracted = agent.analyze(parsed_resume)
    assert len(extracted.skills) >= 2


def test_journey_stage4_diagnostic_assessment(journey_student):
    """Stage 4: Verify diagnostic exam creation, answer submission, and telemetry logging."""
    db = SessionLocal()
    try:
        svc = AssessmentService(session=db)
        exam = svc.create_diagnostic_assessment("Software Development Engineer (SDE)", total_questions=5)
        assert exam.id is not None
        assert len(exam.questions) == 5

        # Submit answers
        answers = [
            AssessmentAnswerSubmission(question_id=q.id, selected_option_index=q.correct_option_index)
            for q in exam.questions
        ]
        sub = AssessmentSubmission(assessment_id=exam.id, profile_id=journey_student, answers=answers)
        attempt = svc.record_submission(sub)
        assert attempt.score_percentage == 100.0
        assert attempt.total_correct == 5
    finally:
        db.close()


def test_journey_stage5_skill_gap_triangulation(journey_student):
    """Stage 5: Verify four-way skill gap triangulation and prioritized learning topics."""
    db = SessionLocal()
    try:
        svc = SkillGapService(session=db)
        prof = db.query(StudentProfile).filter_by(id=journey_student).first()
        gap = svc.analyze_and_persist_gaps(profile=prof)
        assert gap.id is not None
        assert 0.0 <= gap.overall_readiness_score <= 100.0
        assert len(gap.strong_skills) > 0
    finally:
        db.close()


def test_journey_stage6_learning_plan_generation(journey_student):
    """Stage 6: Verify adaptive 4-week preparation plan synthesis."""
    db = SessionLocal()
    try:
        planner = LearningPlannerAgent(mock_mode=True)
        gap = db.query(SkillGap).filter_by(profile_id=journey_student).first()
        plan_struct = planner.generate_plan("Software Development Engineer (SDE)", skill_gap=gap)
        assert plan_struct.total_weeks == 4
        assert len(plan_struct.items) == 4
        assert plan_struct.items[0].week_number == 1
    finally:
        db.close()


def test_journey_stage7_rag_tutor_grounded_citations():
    """Stage 7: Verify grounded tutoring response with verified source citations."""
    tutor = RAGTutorAgent(mock_mode=True)
    req = TutorQueryRequest(
        student_id=1,
        query="Explain Binary Search Trees",
        topic_context="Data Structures & Algorithms"
    )
    resp = tutor.answer_query(req)
    assert resp.grounded is True
    assert len(resp.citations) >= 1
    assert "Binary Search Tree" in resp.answer or "BST" in resp.answer


def test_journey_stage8_interactive_practice(journey_student):
    """Stage 8: Verify MCQ drill submission, point award, and streak advancement."""
    db = SessionLocal()
    try:
        svc = PracticeService(session=db)
        qs = svc.get_practice_questions(limit=1)
        assert len(qs) == 1
        q = qs[0]

        sub = PracticeSubmissionRequest(
            student_id=journey_student,
            question_id=q.id,
            selected_option_index=2,  # test submission
            time_spent_seconds=30
        )
        res = svc.submit_practice_attempt(sub)
        assert res.points_awarded > 0
        assert res.current_streak >= 1
    finally:
        db.close()


def test_journey_stage9_performance_evaluation(journey_student):
    """Stage 9: Verify hiring manager appraisal and qualitative critique synthesis."""
    db = SessionLocal()
    try:
        agent = PerformanceEvaluationAgent(mock_mode=True)
        eval_res = agent.evaluate_student(journey_student, session=db)
        assert eval_res.readiness_tier in ["Interview Ready", "Competitive", "Early Stage", "Not Ready"]
        assert len(eval_res.strengths) >= 1
        assert len(eval_res.recommended_focus_areas) >= 1
    finally:
        db.close()


def test_journey_stage10_next_best_action_execution(journey_student):
    """Stage 10: Verify tactical recommendations generation and completion marking."""
    db = SessionLocal()
    try:
        rec_agent = NextActionRecommendationAgent(action_service=NextActionService(session=db), mock_mode=True)
        rec = rec_agent.get_recommendations(journey_student)
        assert len(rec.actions) >= 1
        first_act = rec.actions[0]
        assert first_act.priority in ["HIGH", "MEDIUM", "LOW"]

        # Mark action as completed
        svc = NextActionService(session=db)
        success = svc.mark_action_completed(first_act.id)
        assert success is True
    finally:
        db.close()
