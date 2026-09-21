# AI Placement Preparation Agent: System Architecture & Technical Specification

## Overview
The **AI Placement Preparation Agent** is an end-to-end multi-agent system designed to guide engineering students through career placement preparation. It combines deterministic business logic (for parsing, scoring, matrix comparison, and database integrity) with AI orchestration (using Microsoft Foundry Agents, Azure OpenAI, and Model Context Protocol) and grounded knowledge retrieval via Azure AI Search RAG.

---

## 1. High-Level Architecture
```mermaid
graph TB
    subgraph Client Layer
        UI["Streamlit Multi-Page Web App (Port 8501)"]
    end

    subgraph Agent Layer [Microsoft Foundry]
        Orchestrator["Placement Orchestrator Agent"]
        A1["Resume Analysis Agent"]
        A2["Assessment Agent"]
        A3["Skill Gap Agent"]
        A4["Learning Planner Agent"]
        A5["RAG Tutor Agent"]
        A6["Evaluation Agent"]
        A7["Next Best Action Agent"]
    end

    subgraph Tooling Layer [Model Context Protocol - MCP]
        MCPServer["Custom MCP Server"]
        T1["StudentProfileTool"]
        T2["ProgressPerformanceTool"]
        T3["LearningPlanTool"]
        T4["GitHubDemoTool"]
    end

    subgraph Business Logic Layer [Python Backend]
        AuthService["Student Service"]
        ResumeService["Resume/JD Parsing Engine"]
        AssessmentService["Assessment Engine"]
        SkillGapService["Skill Gap Matrix Engine"]
        PlannerService["Roadmap Scheduler"]
        EvaluationService["Analytics Aggregator"]
    end

    subgraph RAG Pipeline
        EmbedEngine["Azure OpenAI text-embedding-3-small / Local Mock"]
        SearchEngine["Azure AI Search (Hybrid BM25 + Vector)"]
        KB[("Knowledge Base: DSA, OS, DBMS, SQL, Java, Python, CN, ML")]
    end

    subgraph Data Layer
        DB[("SQLite Database via SQLAlchemy")]
    end

    UI --> Orchestrator
    UI --> AuthService
    UI --> ResumeService
    UI --> AssessmentService
    UI --> SkillGapService

    Orchestrator --> A1
    Orchestrator --> A2
    Orchestrator --> A3
    Orchestrator --> A4
    Orchestrator --> A5
    Orchestrator --> A6
    Orchestrator --> A7

    Orchestrator --> MCPServer
    MCPServer --> T1
    MCPServer --> T2
    MCPServer --> T3
    MCPServer --> T4

    T1 --> DB
    T2 --> DB
    T3 --> DB

    A5 --> SearchEngine
    KB --> EmbedEngine --> SearchEngine
```

---

## 2. Component Directory Layout
- `app/`: Streamlit front-end with 10 dedicated pages for every step of the candidate lifecycle.
- `agents/`: Microsoft Foundry Agent Orchestrator and specialized subagents.
- `rag/`: Document chunking, embedding generation, Azure AI Search indexing, hybrid retrieval, and citation verification.
- `mcp/`: FastMCP-based tool definitions providing sandboxed database operations.
- `database/`: SQLAlchemy 2.0 ORM models and clean repository abstractions.
- `services/`: Deterministic business logic (scoring, set operations, file sanitization).
- `schemas/`: Pydantic schemas validating all data flows across agents and tools.
- `config/`: Centralized settings loaded via Pydantic BaseSettings.
- `tests/`: Automated unit and integration test suites with offline mock mode.
