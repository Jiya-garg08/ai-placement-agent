import pytest
from services.jd_parser import JobDescriptionParser


SAMPLE_SDE_JD = """
Company: Innovatech Solutions
Position: SDE-1 (Backend Engineer)
Location: Bangalore, India / Remote

About the Role:
We are looking for an ambitious new grad or fresher (0-1 years of experience) to join our core backend engineering team.
You will work on highly scalable distributed systems and RESTful APIs.

Key Responsibilities:
- Design and build microservices with clean code principles.
- Work closely with senior engineers in an Agile / Scrum development environment.
- Participate in code reviews and unit testing.

Must-Have Requirements:
- Strong problem-solving skills in Data Structures and Algorithms (Arrays, Trees, Graphs, DP).
- Proficient in Python or Java.
- Solid knowledge of DBMS and relational databases like PostgreSQL or MySQL.
- Good understanding of Operating Systems and Computer Networks.

Nice to Have / Bonus:
- Familiarity with Docker and CI/CD pipelines.
- Experience with React or frontend technologies.
"""


def test_detect_role():
    role = JobDescriptionParser.detect_role(SAMPLE_SDE_JD)
    assert "Software Development Engineer" in role or "Backend Engineer" in role


def test_detect_experience():
    exp = JobDescriptionParser.detect_experience_level(SAMPLE_SDE_JD)
    assert "Entry-Level / Fresher" in exp


def test_skill_separation_required_vs_preferred():
    required, preferred = JobDescriptionParser.extract_skills_and_preferences(SAMPLE_SDE_JD)
    
    # Required skills
    assert "Python" in required or "Java" in required
    assert "Postgresql" in required or "Mysql" in required
    assert "Operating Systems" in required
    assert "Computer Networks" in required
    
    # Preferred skills should contain Docker and/or React
    assert "Docker" in preferred
    assert "React" in preferred


def test_domain_keywords():
    keywords = JobDescriptionParser.extract_domain_keywords(SAMPLE_SDE_JD)
    assert "Microservices" in keywords
    assert "RESTful APIs" in keywords
    assert "Agile" in keywords
    assert "CI/CD" in keywords


def test_full_jd_parse():
    parsed = JobDescriptionParser.parse(SAMPLE_SDE_JD, company_name="Innovatech")
    assert parsed.company_name == "Innovatech"
    assert len(parsed.required_skills) >= 4
    assert len(parsed.preferred_skills) >= 2
    assert len(parsed.domain_keywords) >= 3


def test_non_engineering_jd_parse():
    pm_jd = """
Company: Global Growth Corp
Position: Associate Product Manager (APM)
Experience: Entry-Level / Fresher (0-1 yrs)

About the Role:
Drive customer discovery and lead agile sprint execution for our mobile app portfolio.

Requirements:
- Strong understanding of Product Management, Roadmapping, and User Research.
- Experience with Feature Prioritization and PRD documentation.
- Working knowledge of Agile and Scrum.

Bonus:
- Familiarity with A/B Testing, Google Analytics, and KPI Tracking.
"""
    parsed = JobDescriptionParser.parse(pm_jd, company_name="Global Growth Corp")
    assert parsed.role_title == "Product Manager"
    assert "Product Management" in parsed.required_skills
    assert "Roadmapping" in parsed.required_skills
    assert "A/B Testing" in parsed.preferred_skills or "A/B Testing" in parsed.required_skills

