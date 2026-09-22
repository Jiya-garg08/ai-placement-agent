from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class PracticeQuestionResponse(BaseModel):
    """Clean question presentation model for student practice sessions."""
    id: int
    topic: str
    subtopic: Optional[str] = None
    question_text: str
    code_snippet: Optional[str] = None
    options: List[str]
    difficulty: str

    model_config = ConfigDict(from_attributes=True)


class CodingSnippetChallenge(BaseModel):
    """Conceptual coding challenge with code starters, validation cases, and optimal references."""
    id: str
    title: str
    topic: str
    difficulty: str
    problem_statement: str
    code_starter: str
    test_cases: List[Dict[str, Any]] = Field(default_factory=list)
    hint: str
    optimal_solution: str
    time_complexity: str
    space_complexity: str


class PracticeSubmissionRequest(BaseModel):
    """Submission payload for evaluating a student practice or coding attempt."""
    student_id: int
    question_id: Optional[int] = None
    snippet_id: Optional[str] = None
    selected_option_index: Optional[int] = None
    user_answer: Optional[str] = None
    code_submission: Optional[str] = None
    time_spent_seconds: int = Field(default=0, ge=0)


class PracticeSubmissionResponse(BaseModel):
    """Instant evaluation feedback, explanation, and streak progress."""
    is_correct: bool
    correct_option_index: Optional[int] = None
    correct_answer_text: Optional[str] = None
    explanation: str
    points_awarded: int
    current_streak: int
    total_solved: int
    feedback: str


class PracticeSummaryResponse(BaseModel):
    """Comprehensive telemetry and streak metrics for student practice dashboard."""
    student_id: int
    current_streak: int
    longest_streak: int
    total_questions_solved: int
    total_correct: int
    overall_accuracy: float
    topic_breakdown: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
