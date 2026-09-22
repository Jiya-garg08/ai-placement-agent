"""Comprehensive mock fixtures and simulation helpers for Azure OpenAI / Foundry."""

from typing import Dict, Any, List, Optional
from unittest.mock import MagicMock
from schemas.resume_schema import ExtractedResume, EducationItem, ProjectItem, ExperienceItem
from schemas.plan_schema import LearningPlanStructure, LearningPlanItemSchema


def get_mock_resume_extraction() -> ExtractedResume:
    """Return realistic mock Azure OpenAI structured resume extraction."""
    return ExtractedResume(
        candidate_name="Jiya Garg",
        summary="Final-year CS student targeting Tier 1 Product SDE placement with expertise in Python and Systems.",
        skills=["Python", "Java", "C++", "SQL", "Data Structures", "Algorithms", "Docker", "FastAPI"],
        education=[
            EducationItem(
                institution="National Institute of Technology",
                degree="Bachelor of Technology in Computer Science",
                graduation_year=2026,
                cgpa_or_percentage="8.8/10.0"
            )
        ],
        projects=[
            ProjectItem(
                title="AI Placement Preparation Agent",
                technologies=["Python", "FastAPI", "Azure AI Search", "MCP"],
                description="Engineered an enterprise multi-agent placement accelerator with grounded RAG."
            ),
            ProjectItem(
                title="Distributed In-Memory Cache",
                technologies=["Python", "Consistent Hashing", "LRU"],
                description="Built high-performance distributed key-value store with consistent hashing."
            )
        ],
        experience=[
            ExperienceItem(
                company="Tech Innovators Corp",
                role="Software Engineering Intern",
                duration="Summer 2025",
                highlights=["Optimized asynchronous database pipelines, reducing query latency by 45%."]
            )
        ]
    )


def get_mock_planner_structure() -> LearningPlanStructure:
    """Return realistic mock Azure OpenAI structured learning plan."""
    return LearningPlanStructure(
        plan_name="4-Week Accelerated SDE Placement Roadmap",
        target_role="Software Development Engineer (SDE 1)",
        total_weeks=4,
        daily_hours_target=2.5,
        items=[
            LearningPlanItemSchema(
                week_number=1,
                order_index=1,
                topic="Data Structures & Algorithmic Patterns",
                subtopics=["Binary Search", "Two Pointers", "Trees & Hash Maps"],
                priority="High",
                learning_objectives="Master core algorithmic patterns frequently asked in Tier 1 technical screens.",
                practice_goal_count=15,
                status="Completed"
            ),
            LearningPlanItemSchema(
                week_number=2,
                order_index=2,
                topic="Operating Systems & Concurrency Invariants",
                subtopics=["Process Synchronization", "Semaphores", "Deadlocks"],
                priority="High",
                learning_objectives="Bridge critical OS systems knowledge required for backend engineering interviews.",
                practice_goal_count=15,
                status="In Progress"
            ),
            LearningPlanItemSchema(
                week_number=3,
                order_index=3,
                topic="Low-Level Design & OOP Principles",
                subtopics=["SOLID Principles", "Factory Pattern", "Observer Pattern"],
                priority="Medium",
                learning_objectives="Implement robust class hierarchies and clean object-oriented architecture.",
                practice_goal_count=12,
                status="Pending"
            ),
            LearningPlanItemSchema(
                week_number=4,
                order_index=4,
                topic="System Design & Mock Interview Sprints",
                subtopics=["Horizontal Scalability", "Caching Layers", "Database Sharding"],
                priority="High",
                learning_objectives="Synthesize end-to-end technical readiness under timed mock interview conditions.",
                practice_goal_count=20,
                status="Pending"
            )
        ]
    )


def create_mock_openai_client(chat_return_text: str = "Mock OpenAI response") -> MagicMock:
    """Build a mock AzureOpenAI client with mocked completions and parsed response."""
    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = chat_return_text
    mock_choice.message.parsed = get_mock_resume_extraction()
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client.chat.completions.create.return_value = mock_response
    mock_client.beta.chat.completions.parse.return_value = mock_response
    return mock_client
