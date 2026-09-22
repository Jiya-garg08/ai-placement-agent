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
    ],
    "Product_Management": [
        "Product Management", "Roadmapping", "User Research", "Agile", "Scrum",
        "PRD", "Feature Prioritization", "Stakeholder Management", "A/B Testing",
        "KPI Tracking", "Go-To-Market", "Customer Discovery", "Product Strategy"
    ],
    "Data_Analytics": [
        "Business Intelligence", "PowerBI", "Tableau", "Excel", "Spreadsheets",
        "Statistics", "Data Visualization", "ETL", "Google Analytics", "Looker", "Dashboarding"
    ],
    "Business_Finance": [
        "Financial Modeling", "Accounting", "Budgeting", "Valuation", "Corporate Finance",
        "Auditing", "Risk Management", "Business Strategy", "Market Research",
        "P&L Management", "Forecasting", "Financial Analysis", "Cash Flow"
    ],
    "Marketing_Growth": [
        "Digital Marketing", "SEO", "Content Strategy", "Social Media Marketing",
        "Copywriting", "Email Marketing", "Brand Management", "Performance Marketing",
        "SEM", "Public Relations", "Campaign Management", "Conversion Optimization"
    ],
    "Design_Creative": [
        "UI/UX Design", "Figma", "User Experience", "Wireframing", "Prototyping",
        "Interaction Design", "Graphic Design", "Adobe Creative Suite", "Design Thinking",
        "Usability Testing", "Information Architecture"
    ],
    "HR_People": [
        "Talent Acquisition", "Human Resources", "Recruitment", "Employee Relations",
        "HRIS", "Performance Management", "Onboarding", "HR Policies", "Organizational Development"
    ],
    "Sales_Operations": [
        "B2B Sales", "Lead Generation", "CRM", "Salesforce", "Customer Success",
        "Negotiation", "Supply Chain", "Operations Management", "Process Optimization",
        "Logistics", "Project Management", "Vendor Management", "Contract Negotiation"
    ]
}

# Flat list of normalized lowercase skill keywords for fast regex extraction
ALL_TAXONOMY_SKILLS = set(
    skill.lower() for sublist in STANDARD_SKILL_TAXONOMY.values() for skill in sublist
)
