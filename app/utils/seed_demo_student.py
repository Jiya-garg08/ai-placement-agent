from datetime import datetime, timezone, date, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from database.database import SessionLocal, init_db
from database.models.student import User, StudentProfile
from database.models.assessment import Question, Assessment
from database.models.assessment_attempt import AssessmentAttempt, AssessmentAnswer
from database.models.practice import PracticeAttempt, PracticeStreak
from database.models.skill_gap import SkillGap
from database.models.learning_plan import LearningPlan, LearningPlanItem
from scripts.seed_data import seed_questions
from services.next_action_service import NextActionService


def seed_demo_candidate(session: Optional[Session] = None) -> StudentProfile:
    """Seed comprehensive demo candidate data for instant, rich dashboard visualization."""
    owns_session = session is None
    db = session if session is not None else SessionLocal()

    try:
        init_db()
        seed_questions(db)

        # Check if demo student already exists
        existing_user = db.query(User).filter_by(email="jiya.garg@example.com").first()
        if existing_user and existing_user.profile:
            # Ensure next actions exist
            next_action_svc = NextActionService(session=db)
            saved = next_action_svc.get_saved_actions(existing_user.profile.id)
            if not saved:
                next_action_svc.generate_next_actions(existing_user.profile.id)
            prof = existing_user.profile
            return prof

        # 1. Create User
        user = User(
            name="Jiya Garg",
            email="jiya.garg@example.com"
        )
        db.add(user)
        db.flush()

        # 2. Create Student Profile
        profile = StudentProfile(
            user_id=user.id,
            target_role="Software Development Engineer (SDE 1)",
            career_goal="Secure a Tier 1 Product SDE role with high proficiency in DSA and Distributed Systems",
            target_company_tier="Tier 1 / Product",
            college="National Institute of Technology",
            graduation_year=2026,
            current_semester=7,
            primary_skills=["Python", "Java", "Data Structures", "Algorithms", "SQL", "Git", "FastAPI"]
        )
        db.add(profile)
        db.flush()

        # 3. Create Diagnostic Assessment & Answers
        assessment = Assessment(
            title="SDE Core Technical Diagnostic",
            target_role="Software Development Engineer (SDE 1)",
            topic="Core CS Fundamentals",
            difficulty="Intermediate",
            total_questions=10,
            time_limit_mins=30
        )
        db.add(assessment)
        db.flush()

        questions = db.query(Question).limit(10).all()
        score = 0
        total_questions = len(questions)

        attempt = AssessmentAttempt(
            profile_id=profile.id,
            assessment_id=assessment.id,
            total_questions=total_questions,
            total_correct=0,
            score_percentage=0.0,
            topic_scores=[
                {"topic": "Data Structures & Algorithms", "score": 85.0},
                {"topic": "Database Management Systems", "score": 80.0},
                {"topic": "SQL", "score": 100.0},
                {"topic": "Operating Systems", "score": 60.0},
                {"topic": "Java", "score": 90.0},
                {"topic": "Python", "score": 85.0}
            ]
        )
        db.add(attempt)
        db.flush()

        for idx, q in enumerate(questions):
            # 8 out of 10 correct
            is_correct = idx not in [1, 5]  # miss DP and OOP questions
            selected = q.correct_option_index if is_correct else (q.correct_option_index + 1) % 4
            if is_correct:
                score += 1

            ans = AssessmentAnswer(
                attempt_id=attempt.id,
                question_id=q.id,
                selected_option_index=selected,
                is_correct=is_correct
            )
            db.add(ans)

        attempt.total_correct = score
        attempt.score_percentage = round((score / max(total_questions, 1)) * 100.0, 1)

        # 4. Create Practice Attempts
        practice_topics = [
            ("Data Structures & Algorithms", True, 240),
            ("Data Structures & Algorithms", True, 310),
            ("Database Management Systems", True, 180),
            ("Operating Systems", False, 120),
            ("SQL", True, 150),
            ("Python", True, 130),
            ("Java", True, 200),
            ("Aptitude", True, 90)
        ]
        now = datetime.now(timezone.utc)
        for i, (top, corr, sec) in enumerate(practice_topics):
            q_id = questions[i % len(questions)].id if questions else None
            pa = PracticeAttempt(
                student_id=profile.id,
                question_id=q_id,
                topic=top,
                subtopic="Core Fundamentals",
                question_type="MCQ" if i % 2 == 0 else "CODE_SNIPPET",
                user_answer="Correct selection" if corr else "Suboptimal selection",
                is_correct=corr,
                time_spent_seconds=sec,
                feedback="Mastered core concept" if corr else "Review edge cases and invariants.",
                points_awarded=10 if corr else 0,
                created_at=now - timedelta(days=i % 4, hours=i * 2)
            )
            db.add(pa)

        # 5. Create Practice Streak
        streak = PracticeStreak(
            student_id=profile.id,
            current_streak=5,
            longest_streak=7,
            last_practice_date=date.today(),
            total_questions_solved=len(practice_topics),
            total_correct=sum(1 for _, c, _ in practice_topics if c)
        )
        db.add(streak)

        # 6. Create Skill Gap Record
        skill_gap = SkillGap(
            profile_id=profile.id,
            strong_skills=["Data Structures", "Algorithms", "Python", "SQL", "Git"],
            weak_skills=["Operating Systems (Concurrency)", "Dynamic Programming"],
            missing_skills=["System Design (Distributed Caching)", "Docker & Microservices"],
            priority_topics=["Operating Systems", "Dynamic Programming", "System Design"],
            overall_readiness_score=78.5
        )
        db.add(skill_gap)
        db.flush()

        # 7. Create 4-Week Learning Plan
        plan = LearningPlan(
            profile_id=profile.id,
            plan_name="4-Week Accelerated SDE Placement Roadmap",
            target_role="Software Development Engineer (SDE 1)",
            total_weeks=4,
            daily_hours_target=2.5,
            is_active=True
        )
        db.add(plan)
        db.flush()

        plan_items = [
            (1, 1, "Data Structures & Algorithmic Patterns", ["Binary Search", "Two Pointers", "Trees"], "High", "Master arrays, hash maps, BSTs and time complexity", 8, "Completed"),
            (2, 2, "Operating Systems & Concurrency", ["Processes", "Deadlocks", "Threads"], "High", "Process synchronization, semaphores, deadlock prevention", 8, "In Progress"),
            (3, 3, "Low-Level Design & OOP Principles", ["SOLID", "Design Patterns"], "Medium", "SOLID principles, factory and observer design patterns", 6, "Pending"),
            (4, 4, "System Design & Mock Interview Sprints", ["Caching", "Scalability"], "High", "Horizontal scaling, CDN, sharding, mock drills", 5, "Pending"),
        ]
        for w_num, ord_idx, top, sub, prio, obj, goal, stat in plan_items:
            item = LearningPlanItem(
                plan_id=plan.id,
                week_number=w_num,
                order_index=ord_idx,
                topic=top,
                subtopics=sub,
                priority=prio,
                learning_objectives=obj,
                practice_goal_count=goal,
                status=stat
            )
            db.add(item)

        db.commit()

        # 8. Generate Next Best Actions
        next_action_svc = NextActionService(session=db)
        next_action_svc.generate_next_actions(profile.id)

        return profile
    finally:
        if owns_session:
            db.close()
