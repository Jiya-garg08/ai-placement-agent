"""Taxonomy and domain constants for placement preparation."""

CORE_PLACEMENT_DOMAINS = [
    "Data Structures & Algorithms",
    "Database Management Systems",
    "SQL",
    "Java",
    "Python",
    "Object-Oriented Programming",
    "Computer Networks",
    "Operating Systems",
    "Machine Learning",
    "Aptitude & Logical Reasoning"
]

STANDARD_SKILL_TAXONOMY = {
    "DSA": [
        "Arrays", "Strings", "Linked Lists", "Stacks", "Queues", "Binary Trees",
        "Binary Search Trees", "Heaps", "Graphs", "Dynamic Programming",
        "Recursion", "Backtracking", "Sorting", "Searching", "Bit Manipulation"
    ],
    "DBMS_SQL": [
        "DBMS", "RDBMS", "SQL", "MySQL", "PostgreSQL", "Normalization", "ACID Properties",
        "Indexing", "B+ Trees", "Transactions", "Joins", "Aggregate Functions",
        "Subqueries", "Window Functions", "Stored Procedures", "Triggers"
    ],
    "Languages": [
        "Python", "Java", "C", "C++", "JavaScript", "TypeScript", "Go", "Rust"
    ],
    "Core_CS": [
        "Operating Systems", "Computer Networks", "OOP", "Object-Oriented Programming",
        "Design Patterns", "SOLID Principles", "System Design", "Multithreading",
        "Concurrency", "Virtual Memory", "Deadlocks", "TCP/IP", "HTTP", "DNS"
    ],
    "Web_Cloud": [
        "HTML", "CSS", "React", "Node.js", "Express", "FastAPI", "Django", "Flask",
        "REST API", "Docker", "Kubernetes", "AWS", "Azure", "Git", "GitHub", "CI/CD"
    ],
    "AI_ML": [
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Scikit-Learn",
        "TensorFlow", "PyTorch", "Pandas", "NumPy", "Data Analysis"
    ]
}

# Flat list of normalized lowercase skill keywords for fast regex extraction
ALL_TAXONOMY_SKILLS = set(
    skill.lower() for sublist in STANDARD_SKILL_TAXONOMY.values() for skill in sublist
)
