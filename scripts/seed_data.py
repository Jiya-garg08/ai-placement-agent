"""Seed database with curated placement preparation questions across 10 domains."""

SEED_QUESTIONS = [
    # 1. DSA
    {
        "topic": "Data Structures & Algorithms",
        "subtopic": "Binary Search Trees",
        "question_text": "What is the worst-case time complexity of searching for an element in a Binary Search Tree (BST)?",
        "options": ["O(1)", "O(log N)", "O(N)", "O(N log N)"],
        "correct_option_index": 2,
        "explanation": "In an unbalanced (skewed) BST, searching degrades to linear time O(N), equivalent to searching a linked list.",
        "difficulty": "Easy"
    },
    {
        "topic": "Data Structures & Algorithms",
        "subtopic": "Dynamic Programming",
        "question_text": "Which condition must a problem satisfy to be solvable using Dynamic Programming?",
        "options": [
            "Greedy Choice Property only",
            "Optimal Substructure and Overlapping Subproblems",
            "Linear time complexity and Divide & Conquer",
            "Circular dependencies between subproblems"
        ],
        "correct_option_index": 1,
        "explanation": "Dynamic programming applies when subproblems overlap and an optimal solution to the problem contains optimal solutions to its subproblems.",
        "difficulty": "Medium"
    },
    {
        "topic": "Data Structures & Algorithms",
        "subtopic": "Graphs",
        "question_text": "Which algorithm is best suited to find the shortest path in an unweighted graph?",
        "options": ["Dijkstra's Algorithm", "Breadth-First Search (BFS)", "Depth-First Search (DFS)", "Bellman-Ford Algorithm"],
        "correct_option_index": 1,
        "explanation": "BFS explores nodes layer by layer, guaranteeing the shortest path in an unweighted graph in O(V + E) time.",
        "difficulty": "Easy"
    },

    # 2. DBMS
    {
        "topic": "Database Management Systems",
        "subtopic": "ACID Properties",
        "question_text": "Which ACID property guarantees that a transaction executes completely or not at all?",
        "options": ["Atomicity", "Consistency", "Isolation", "Durability"],
        "correct_option_index": 0,
        "explanation": "Atomicity ensures 'all-or-nothing' execution of transaction operations.",
        "difficulty": "Easy"
    },
    {
        "topic": "Database Management Systems",
        "subtopic": "Normalization",
        "question_text": "A relation is in Boyce-Codd Normal Form (BCNF) if and only if for every functional dependency X -> Y:",
        "options": [
            "Y is a prime attribute",
            "X is a super key",
            "X is a foreign key",
            "Y is functionally dependent on the candidate key"
        ],
        "correct_option_index": 1,
        "explanation": "BCNF requires that for every non-trivial functional dependency X -> Y, X must be a super key.",
        "difficulty": "Hard"
    },

    # 3. SQL
    {
        "topic": "SQL",
        "subtopic": "Joins",
        "question_text": "Which SQL join returns all rows from the left table and matched rows from the right table, filling nulls if no match exists?",
        "options": ["INNER JOIN", "FULL OUTER JOIN", "LEFT OUTER JOIN", "CROSS JOIN"],
        "correct_option_index": 2,
        "explanation": "LEFT OUTER JOIN returns all records from the left table and matched records from the right table.",
        "difficulty": "Easy"
    },
    {
        "topic": "SQL",
        "subtopic": "Window Functions",
        "question_text": "Which SQL window function assigns ranks without gaps in the ranking sequence for tied values?",
        "options": ["RANK()", "DENSE_RANK()", "ROW_NUMBER()", "NTILE()"],
        "correct_option_index": 1,
        "explanation": "DENSE_RANK() does not skip rank values when ties occur (e.g. 1, 2, 2, 3), whereas RANK() skips (1, 2, 2, 4).",
        "difficulty": "Medium"
    },

    # 4. Java
    {
        "topic": "Java",
        "subtopic": "JVM Memory",
        "question_text": "Where are Java object instances allocated in memory at runtime?",
        "options": ["Stack Memory", "Heap Memory", "PermGen / Metaspace only", "Code Segment"],
        "correct_option_index": 1,
        "explanation": "In Java, all objects and array instances are allocated on the Heap memory.",
        "difficulty": "Easy"
    },
    {
        "topic": "Java",
        "subtopic": "Collections",
        "question_text": "What is the underlying data structure of Java's HashMap in Java 8+ when a hash bucket contains more than 8 colliding nodes?",
        "options": ["Singly Linked List", "Red-Black Tree", "B+ Tree", "AVL Tree"],
        "correct_option_index": 1,
        "explanation": "When collisions exceed TREEIFY_THRESHOLD (8), Java 8 replaces the linked list with a balanced Red-Black Tree, improving worst-case lookup from O(N) to O(log N).",
        "difficulty": "Hard"
    },

    # 5. Python
    {
        "topic": "Python",
        "subtopic": "Concurrency",
        "question_text": "What is the Global Interpreter Lock (GIL) in CPython?",
        "options": [
            "A mechanism that prevents multiple processes from running simultaneously",
            "A mutex that prevents multiple native threads from executing Python bytecodes at once",
            "A garbage collection lock that freezes memory deallocation",
            "A security feature that prevents unauthorized script execution"
        ],
        "correct_option_index": 1,
        "explanation": "CPython's GIL ensures only one thread executes Python bytecodes at a time, simplifying thread safety at the expense of CPU-bound multi-threaded parallelism.",
        "difficulty": "Medium"
    },

    # 6. OOP
    {
        "topic": "Object-Oriented Programming",
        "subtopic": "SOLID Principles",
        "question_text": "Which SOLID principle states that subclasses should be substitutable for their base classes without altering program correctness?",
        "options": [
            "Single Responsibility Principle",
            "Open/Closed Principle",
            "Liskov Substitution Principle",
            "Dependency Inversion Principle"
        ],
        "correct_option_index": 2,
        "explanation": "Liskov Substitution Principle (LSP) requires subtype objects to be replaceable with supertype objects without breaking application behavior.",
        "difficulty": "Medium"
    },

    # 7. Operating Systems
    {
        "topic": "Operating Systems",
        "subtopic": "Deadlocks",
        "question_text": "Which of the following is NOT one of Coffman's four conditions required for a deadlock to occur?",
        "options": ["Mutual Exclusion", "Hold and Wait", "Preemption allowed", "Circular Wait"],
        "correct_option_index": 2,
        "explanation": "Deadlock requires NO PREEMPTION. If preemption is allowed, resources can be forcibly reclaimed, breaking the deadlock.",
        "difficulty": "Medium"
    },
    {
        "topic": "Operating Systems",
        "subtopic": "Virtual Memory",
        "question_text": "What is 'Thrashing' in an operating system?",
        "options": [
            "A state where the CPU spends more time paging than executing processes",
            "When high network traffic crashes the TCP stack",
            "Excessive file system fragmentation",
            "Rapid context-switching between kernel and user mode"
        ],
        "correct_option_index": 0,
        "explanation": "Thrashing occurs when a computer's virtual memory subsystem is in a constant state of paging, rapidly exchanging data in memory for data on disk.",
        "difficulty": "Medium"
    },

    # 8. Computer Networks
    {
        "topic": "Computer Networks",
        "subtopic": "TCP/IP",
        "question_text": "How many packets are exchanged in a standard TCP connection teardown handshake?",
        "options": ["2 packets", "3 packets", "4 packets", "5 packets"],
        "correct_option_index": 2,
        "explanation": "TCP termination uses a 4-way handshake: FIN, ACK, FIN, ACK.",
        "difficulty": "Easy"
    },

    # 9. Machine Learning
    {
        "topic": "Machine Learning",
        "subtopic": "Model Evaluation",
        "question_text": "When evaluating a medical diagnosis model where False Negatives are critical, which metric should be prioritized?",
        "options": ["Precision", "Recall (Sensitivity)", "Accuracy", "Specificity"],
        "correct_option_index": 1,
        "explanation": "Recall = TP / (TP + FN). Maximizing recall minimizes False Negatives.",
        "difficulty": "Medium"
    },

    # 10. Aptitude
    {
        "topic": "Aptitude & Logical Reasoning",
        "subtopic": "Probability",
        "question_text": "A fair coin is tossed 3 times. What is the probability of getting at least two heads?",
        "options": ["1/8", "3/8", "1/2", "5/8"],
        "correct_option_index": 2,
        "explanation": "Total outcomes = 8. Favorable outcomes (HHH, HHT, HTH, THH) = 4. Probability = 4/8 = 1/2.",
        "difficulty": "Easy"
    }
]


def seed_questions(session):
    """Seed questions into the database if not already populated."""
    from database.models.assessment import Question

    count = session.query(Question).count()
    if count >= len(SEED_QUESTIONS):
        return count

    added = 0
    for q_data in SEED_QUESTIONS:
        exists = session.query(Question).filter(Question.question_text == q_data["question_text"]).first()
        if not exists:
            q = Question(**q_data)
            session.add(q)
            added += 1
    session.commit()
    return added


if __name__ == "__main__":
    from database.database import SessionLocal, init_db
    init_db()
    db = SessionLocal()
    try:
        num = seed_questions(db)
        print(f"Successfully seeded {num} questions into placement question bank.")
    finally:
        db.close()
