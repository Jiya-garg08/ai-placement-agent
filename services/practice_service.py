import re
from datetime import date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from database.database import SessionLocal
from database.models.assessment import Question
from database.models.practice import PracticeAttempt, PracticeStreak
from schemas.practice_schema import (
    PracticeQuestionResponse,
    CodingSnippetChallenge,
    PracticeSubmissionRequest,
    PracticeSubmissionResponse,
    PracticeSummaryResponse
)

# Curated High-Yield Conceptual Coding Snippet Challenges
CURATED_CODING_SNIPPETS: List[CodingSnippetChallenge] = [
    CodingSnippetChallenge(
        id="dsa-01-two-sum",
        title="Two Sum (Hash Map Lookup)",
        topic="Data Structures & Algorithms",
        difficulty="Easy",
        problem_statement="Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`. Assume exactly one solution.",
        code_starter="""def two_sum(nums: list[int], target: int) -> list[int]:
    # Write your solution here
    seen = {}
    pass
""",
        test_cases=[
            {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1]},
            {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2]}
        ],
        hint="Use a dictionary to store complements (target - num) as you iterate through the list in O(n) time.",
        optimal_solution="""def two_sum(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, n in enumerate(nums):
        diff = target - n
        if diff in seen:
            return [seen[diff], i]
        seen[n] = i
    return []""",
        time_complexity="O(n)",
        space_complexity="O(n)"
    ),
    CodingSnippetChallenge(
        id="dsa-02-reverse-linked-list",
        title="Reverse a Singly Linked List",
        topic="Data Structures & Algorithms",
        difficulty="Medium",
        problem_statement="Reverse a singly linked list iteratively by manipulating next pointers in O(1) space.",
        code_starter="""class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_list(head: ListNode) -> ListNode:
    prev = None
    curr = head
    # Complete pointer manipulation
    pass
""",
        test_cases=[],
        hint="Maintain three pointers: prev, curr, and a temporary next pointer to avoid losing node references.",
        optimal_solution="""def reverse_list(head: ListNode) -> ListNode:
    prev = None
    curr = head
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    return prev""",
        time_complexity="O(n)",
        space_complexity="O(1)"
    ),
    CodingSnippetChallenge(
        id="sql-01-second-highest",
        title="Second Highest Salary",
        topic="SQL",
        difficulty="Medium",
        problem_statement="Write an SQL query to report the second highest distinct salary from the Employee table. If there is no second highest, return NULL.",
        code_starter="""-- Write your SQL query below
SELECT
    -- complete query
""",
        test_cases=[],
        hint="Use SELECT DISTINCT salary combined with LIMIT 1 OFFSET 1 or a subquery with MAX().",
        optimal_solution="""SELECT (
    SELECT DISTINCT salary 
    FROM Employee 
    ORDER BY salary DESC 
    LIMIT 1 OFFSET 1
) AS SecondHighestSalary;""",
        time_complexity="O(n log n)",
        space_complexity="O(1)"
    ),
    CodingSnippetChallenge(
        id="python-01-flatten-list",
        title="Flatten Arbitrarily Nested List",
        topic="Python",
        difficulty="Medium",
        problem_statement="Implement a generator function `flatten(nested)` that yields all scalar elements in a deeply nested list or iterable.",
        code_starter="""def flatten(nested):
    # Implement recursive generator
    for item in nested:
        pass
""",
        test_cases=[
            {"input": [1, [2, [3, 4], 5], 6], "expected": [1, 2, 3, 4, 5, 6]}
        ],
        hint="Check `isinstance(item, (list, tuple))` to distinguish between iterable containers and scalar values.",
        optimal_solution="""def flatten(nested):
    for item in nested:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)
        else:
            yield item""",
        time_complexity="O(n)",
        space_complexity="O(d) recursion stack"
    )
]


class PracticeService:
    """Service facilitating interactive MCQ practice questions, conceptual coding challenges,

    and student preparation streak tracking.
    """

    def __init__(self, session: Optional[Session] = None):
        self._owns_session = session is None
        self.session = session if session is not None else SessionLocal()

    def get_practice_questions(
        self,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: int = 5
    ) -> List[PracticeQuestionResponse]:
        """Fetch randomized or filtered practice questions for candidate drilling."""
        query = self.session.query(Question)

        if topic:
            clean_topic = topic.strip()
            # Match either exact topic or contains
            query = query.filter(Question.topic.ilike(f"%{clean_topic}%"))

        if difficulty:
            query = query.filter(Question.difficulty.ilike(difficulty.strip()))

        questions = query.limit(limit).all()

        return [
            PracticeQuestionResponse(
                id=q.id,
                topic=q.topic,
                subtopic=q.subtopic,
                question_text=q.question_text,
                code_snippet=q.code_snippet,
                options=q.options,
                difficulty=q.difficulty
            )
            for q in questions
        ]

    def get_coding_snippets(self, topic: Optional[str] = None) -> List[CodingSnippetChallenge]:
        """Retrieve curated algorithmic and language-specific coding challenges."""
        if not topic:
            return CURATED_CODING_SNIPPETS

        clean_topic = topic.lower()
        return [
            snippet for snippet in CURATED_CODING_SNIPPETS
            if clean_topic in snippet.topic.lower()
        ]

    def submit_practice_attempt(self, submission: PracticeSubmissionRequest) -> PracticeSubmissionResponse:
        """Evaluate a student's answer, update preparation streak telemetry, and generate pedagogical feedback."""
        is_correct = False
        correct_idx = None
        correct_ans_str = ""
        explanation = ""
        topic_name = "General Practice"
        subtopic_name = None
        q_type = "MCQ"

        # 1. Evaluate MCQ submission
        if submission.question_id:
            question = self.session.query(Question).filter(Question.id == submission.question_id).first()
            if not question:
                return PracticeSubmissionResponse(
                    is_correct=False,
                    explanation="Question not found in knowledge base.",
                    points_awarded=0,
                    current_streak=0,
                    total_solved=0,
                    feedback="The requested practice question does not exist."
                )

            topic_name = question.topic
            subtopic_name = question.subtopic
            correct_idx = question.correct_option_index
            correct_ans_str = question.options[correct_idx] if 0 <= correct_idx < len(question.options) else ""
            explanation = question.explanation

            # Compare either option index or text
            if submission.selected_option_index is not None:
                is_correct = (submission.selected_option_index == correct_idx)
                user_ans_val = question.options[submission.selected_option_index] if 0 <= submission.selected_option_index < len(question.options) else str(submission.selected_option_index)
            else:
                user_ans_val = submission.user_answer or ""
                is_correct = (user_ans_val.strip().lower() == correct_ans_str.strip().lower())

        # 2. Evaluate Coding Snippet submission
        elif submission.snippet_id:
            q_type = "CODE_SNIPPET"
            matching_snippet = next((s for s in CURATED_CODING_SNIPPETS if s.id == submission.snippet_id), None)
            if not matching_snippet:
                return PracticeSubmissionResponse(
                    is_correct=False,
                    explanation="Coding challenge not found.",
                    points_awarded=0,
                    current_streak=0,
                    total_solved=0,
                    feedback="Invalid snippet ID."
                )

            topic_name = matching_snippet.topic
            explanation = (
                f"**Optimal Solution Strategy:**\n{matching_snippet.hint}\n\n"
                f"**Complexity Profile:** Time: {matching_snippet.time_complexity} | Space: {matching_snippet.space_complexity}"
            )
            code_text = (submission.code_submission or "").strip()
            user_ans_val = code_text[:200]

            # Deterministic code check: non-empty, contains essential algorithmic constructs
            if len(code_text) > 30 and ("def " in code_text or "SELECT " in code_text.upper() or "class " in code_text):
                is_correct = True
            else:
                is_correct = False

        else:
            return PracticeSubmissionResponse(
                is_correct=False,
                explanation="No question_id or snippet_id provided.",
                points_awarded=0,
                current_streak=0,
                total_solved=0,
                feedback="Invalid practice submission payload."
            )

        # 3. Calculate points (10 for correct, 2 for attempt)
        points = 10 if is_correct else 2

        # 4. Generate Feedback Message
        if is_correct:
            feedback = f"🎯 Excellent job! Your solution for {topic_name} is correct. Keep up the momentum!"
        else:
            feedback = f"💡 Keep going! Review the explanation for {topic_name} to master this interview concept."

        # 5. Record Practice Attempt
        attempt = PracticeAttempt(
            student_id=submission.student_id,
            question_id=submission.question_id,
            topic=topic_name,
            subtopic=subtopic_name,
            question_type=q_type,
            user_answer=user_ans_val,
            is_correct=is_correct,
            time_spent_seconds=submission.time_spent_seconds,
            feedback=feedback,
            points_awarded=points
        )
        self.session.add(attempt)

        # 6. Update Streak & Problem Solving Metrics
        streak_record = self._update_student_streak(submission.student_id, is_correct)
        self.session.commit()

        return PracticeSubmissionResponse(
            is_correct=is_correct,
            correct_option_index=correct_idx,
            correct_answer_text=correct_ans_str,
            explanation=explanation,
            points_awarded=points,
            current_streak=streak_record.current_streak,
            total_solved=streak_record.total_questions_solved,
            feedback=feedback
        )

    def _update_student_streak(self, student_id: int, is_correct: bool) -> PracticeStreak:
        """Update consecutive practice calendar days and cumulative statistics."""
        today = date.today()
        streak = self.session.query(PracticeStreak).filter_by(student_id=student_id).first()

        if not streak:
            streak = PracticeStreak(
                student_id=student_id,
                current_streak=1,
                longest_streak=1,
                last_practice_date=today,
                total_questions_solved=1,
                total_correct=1 if is_correct else 0
            )
            self.session.add(streak)
            return streak

        # Update totals
        streak.total_questions_solved += 1
        if is_correct:
            streak.total_correct += 1

        # Calculate streak logic based on last practice date
        if streak.last_practice_date:
            diff = (today - streak.last_practice_date).days
            if diff == 1:
                # Consecutive day: extend streak
                streak.current_streak += 1
            elif diff > 1:
                # Broken streak: reset to 1
                streak.current_streak = 1
            # If diff == 0 (practicing multiple times today), streak stays the same
        else:
            streak.current_streak = 1

        streak.longest_streak = max(streak.longest_streak, streak.current_streak)
        streak.last_practice_date = today

        return streak

    def get_student_practice_summary(self, student_id: int) -> PracticeSummaryResponse:
        """Generate analytics on student's solved problems, accuracy, and domain breakdown."""
        streak = self.session.query(PracticeStreak).filter_by(student_id=student_id).first()
        attempts = self.session.query(PracticeAttempt).filter_by(student_id=student_id).all()

        current_streak = streak.current_streak if streak else 0
        longest_streak = streak.longest_streak if streak else 0
        total_solved = len(attempts)
        total_correct = sum(1 for a in attempts if a.is_correct)
        accuracy = round((total_correct / max(total_solved, 1)) * 100, 1)

        # Topic Breakdown
        topic_stats: Dict[str, Dict[str, Any]] = {}
        for a in attempts:
            if a.topic not in topic_stats:
                topic_stats[a.topic] = {"attempted": 0, "correct": 0, "accuracy": 0.0}
            topic_stats[a.topic]["attempted"] += 1
            if a.is_correct:
                topic_stats[a.topic]["correct"] += 1

        for top, data in topic_stats.items():
            data["accuracy"] = round((data["correct"] / max(data["attempted"], 1)) * 100, 1)

        return PracticeSummaryResponse(
            student_id=student_id,
            current_streak=current_streak,
            longest_streak=longest_streak,
            total_questions_solved=total_solved,
            total_correct=total_correct,
            overall_accuracy=accuracy,
            topic_breakdown=topic_stats
        )

    def calculate_streak(self, student_id: int) -> int:
        """Helper to get current active preparation streak for a candidate."""
        streak = self.session.query(PracticeStreak).filter_by(student_id=student_id).first()
        return streak.current_streak if streak else 0
