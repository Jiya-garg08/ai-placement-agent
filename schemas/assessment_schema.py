from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict


class QuestionResponse(BaseModel):
    id: int
    topic: str
    subtopic: Optional[str] = None
    question_text: str
    code_snippet: Optional[str] = None
    options: List[str]
    difficulty: str

    model_config = ConfigDict(from_attributes=True)


class QuestionDetail(QuestionResponse):
    correct_option_index: int
    explanation: str


class AssessmentResponse(BaseModel):
    id: int
    title: str
    target_role: str
    topic: str
    difficulty: str
    total_questions: int
    time_limit_mins: int
    questions: List[QuestionResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class AssessmentAnswerSubmission(BaseModel):
    question_id: int
    selected_option_index: int


class AssessmentSubmission(BaseModel):
    assessment_id: int
    profile_id: int
    answers: List[AssessmentAnswerSubmission]


class TopicScore(BaseModel):
    topic: str
    correct: int
    total: int
    percentage: float


class AssessmentResultResponse(BaseModel):
    attempt_id: int
    assessment_id: int
    profile_id: int
    total_questions: int
    total_correct: int
    score_percentage: float
    topic_breakdown: List[TopicScore] = Field(default_factory=list)
