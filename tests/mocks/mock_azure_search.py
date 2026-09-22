"""Comprehensive mock fixtures and simulation helpers for Azure AI Search."""

from typing import Dict, Any, List, Optional
from unittest.mock import MagicMock
from schemas.rag_schema import SearchResultItem


def get_mock_search_results(query: str = "DSA") -> List[Dict[str, Any]]:
    """Return mock search document dictionaries matching Azure Search client outputs."""
    return [
        {
            "id": "chunk-dsa-001",
            "title": "Data Structures & Algorithms - Trees",
            "topic": "Data Structures & Algorithms",
            "section": "Binary Search Trees",
            "content": "A Binary Search Tree (BST) maintains the invariant that left < node < right. Worst case lookup is O(N) when skewed, but O(log N) in balanced AVL or Red-Black trees.",
            "source_file": "DSA_CheatSheet.md",
            "@search.score": 0.89
        },
        {
            "id": "chunk-dbms-001",
            "title": "Database Management Systems - ACID",
            "topic": "Database Management Systems",
            "section": "Transaction Invariants",
            "content": "Atomicity, Consistency, Isolation, and Durability (ACID) guarantee reliable processing of database transactions.",
            "source_file": "DBMS_CheatSheet.md",
            "@search.score": 0.82
        },
        {
            "id": "chunk-os-001",
            "title": "Operating Systems - Virtual Memory",
            "topic": "Operating Systems",
            "section": "Thrashing & Paging",
            "content": "Thrashing occurs when the system spends more time paging memory to disk than executing process instructions.",
            "source_file": "OS_CheatSheet.md",
            "@search.score": 0.77
        }
    ]


def create_mock_search_client(results: Optional[List[Dict[str, Any]]] = None) -> MagicMock:
    """Build a mock Azure SearchClient returning iterable search hits."""
    mock_client = MagicMock()
    hits = results if results is not None else get_mock_search_results()
    mock_client.search.return_value = iter(hits)
    return mock_client
