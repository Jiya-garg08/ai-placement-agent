import pytest
from agents.tutor_agent.tutor_agent import RAGTutorAgent
from schemas.rag_schema import TutorQueryRequest, TutorResponse


def test_tutor_agent_grounded_answer():
    agent = RAGTutorAgent(mock_mode=True)
    req = TutorQueryRequest(
        student_id=1,
        query="Explain Boyce-Codd Normal Form BCNF and functional dependencies",
        topic_context="Database Management Systems"
    )

    resp = agent.answer_query(req)

    assert isinstance(resp, TutorResponse)
    assert resp.grounded is True
    assert len(resp.citations) >= 1
    assert "Database" in resp.citations[0].title
    assert "Boyce-Codd" in resp.citations[0].section or "Normalization" in resp.citations[0].section
    assert "[Source:" in resp.answer


def test_tutor_agent_dsa_trees_query():
    agent = RAGTutorAgent(mock_mode=True)
    req = TutorQueryRequest(
        student_id=1,
        query="What is the worst-case time complexity of Binary Search Trees BST?",
        topic_context="Data Structures & Algorithms"
    )

    resp = agent.answer_query(req)

    assert resp.grounded is True
    assert len(resp.citations) >= 1
    assert any("Data Structures" in c.title for c in resp.citations)
    assert "Binary Search Trees" in resp.answer or "BST" in resp.answer


def test_tutor_agent_out_of_domain_rejection():
    agent = RAGTutorAgent(mock_mode=True)
    req = TutorQueryRequest(
        student_id=1,
        query="How do I bake sourdough bread with yeast?"
    )

    resp = agent.answer_query(req)
    assert resp.grounded is False
    assert len(resp.citations) == 0
    assert "cannot find sufficient verified information" in resp.answer
