"""Seed database with curated placement preparation questions across 10 domains."""

import sys
from pathlib import Path

_repo_root = str(Path(__file__).resolve().parent.parent)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

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

    # 9. Machine Learning & AI
    {
        "topic": "Machine Learning",
        "subtopic": "Model Evaluation",
        "question_text": "When evaluating a medical diagnosis model where False Negatives are critical, which metric should be prioritized?",
        "options": ["Precision", "Recall (Sensitivity)", "Accuracy", "Specificity"],
        "correct_option_index": 1,
        "explanation": "Recall = TP / (TP + FN). Maximizing recall minimizes False Negatives.",
        "difficulty": "Medium"
    },
    {
        "topic": "Machine Learning",
        "subtopic": "Regularization",
        "question_text": "What is the primary difference between L1 (Lasso) and L2 (Ridge) regularization in linear models?",
        "options": [
            "L1 regularization shrinks weights to zero causing sparse feature selection; L2 shrinks weights toward zero without setting them to zero",
            "L2 produces sparse models while L1 preserves all coefficients",
            "L1 is only used in unsupervised learning, while L2 is for supervised learning",
            "L1 penalizes squared weights, while L2 penalizes absolute weights"
        ],
        "correct_option_index": 0,
        "explanation": "L1 (Lasso) uses absolute weight penalties which drive non-essential coefficients to exact zeros, acting as a feature selector. L2 (Ridge) uses squared penalties which shrink coefficients proportionally.",
        "difficulty": "Medium"
    },
    {
        "topic": "Machine Learning",
        "subtopic": "Bias-Variance Tradeoff",
        "question_text": "A complex model achieves 99.8% training accuracy but drops to 68.2% on cross-validation test data. What is this model exhibiting?",
        "options": ["High Bias (Underfitting)", "High Variance (Overfitting)", "Low Variance and Low Bias", "Optimal Generalization"],
        "correct_option_index": 1,
        "explanation": "A massive gap between high training performance and low validation performance is a hallmark of High Variance (Overfitting).",
        "difficulty": "Easy"
    },
    {
        "topic": "Machine Learning",
        "subtopic": "Optimization",
        "question_text": "In gradient descent optimization, what happens if the learning rate (alpha) is set too high?",
        "options": [
            "The model converges monotonically to the global minimum in one step",
            "The loss will oscillate and may diverge completely without finding a minimum",
            "Gradient descent turns into stochastic gradient descent",
            "The weights become sparse and vanish"
        ],
        "correct_option_index": 1,
        "explanation": "A learning rate that is too large overshoots the valley of the cost function, causing divergence or erratic oscillations.",
        "difficulty": "Easy"
    },
    {
        "topic": "Machine Learning",
        "subtopic": "Ensemble Methods",
        "question_text": "How do Random Forests and Gradient Boosted Decision Trees (GBDT) differ in their ensemble strategy?",
        "options": [
            "Random Forest trains trees sequentially to correct errors; GBDT trains independent trees in parallel",
            "Random Forest uses Bagging (parallel bootstrap aggregation); GBDT uses Boosting (sequential residual correction)",
            "Random Forest is only for classification; GBDT is only for regression",
            "There is no difference; they are identical algorithms"
        ],
        "correct_option_index": 1,
        "explanation": "Random Forest builds independent trees concurrently (Bagging) to reduce variance. GBDT builds trees sequentially where each new tree fits the residual errors of prior trees (Boosting).",
        "difficulty": "Hard"
    },
    {
        "topic": "Machine Learning",
        "subtopic": "Deep Learning Architecture",
        "question_text": "In Transformer neural network architectures, what is the core mechanism enabling dynamic contextual token relationships?",
        "options": ["Recurrent LSTM gates", "Multi-Head Scaled Dot-Product Self-Attention", "Convolutional pooling", "Max-Margin separation"],
        "correct_option_index": 1,
        "explanation": "Self-attention computes dynamic Query-Key-Value affinities across all input tokens simultaneously regardless of token distance.",
        "difficulty": "Hard"
    },

    # 10. Data Science & Python
    {
        "topic": "Data Science",
        "subtopic": "Feature Engineering",
        "question_text": "Why must feature scaling (e.g. StandardScaler fit) be performed ONLY on training data before transforming test data?",
        "options": [
            "To prevent data leakage from the test set into the model training pipeline",
            "Because test data cannot have mean and variance computed",
            "It is required by scikit-learn syntax only",
            "To speed up GPU matrix operations"
        ],
        "correct_option_index": 0,
        "explanation": "Fitting scalers on test data introduces data leakage by exposing unseen distribution parameters (mean, standard deviation) during training.",
        "difficulty": "Medium"
    },
    {
        "topic": "Data Science",
        "subtopic": "Imbalanced Datasets",
        "question_text": "When training a classifier on an imbalanced dataset (99% negative, 1% positive), which technique synthesizes new minority samples?",
        "options": ["Random Undersampling", "SMOTE (Synthetic Minority Over-sampling Technique)", "PCA Dimensionality Reduction", "One-Hot Encoding"],
        "correct_option_index": 1,
        "explanation": "SMOTE interpolates between nearest neighbors of minority class samples to synthesize plausible new feature representations.",
        "difficulty": "Medium"
    },
    {
        "topic": "Python",
        "subtopic": "Pandas Indexing",
        "question_text": "In Python Pandas, what is the primary distinction between `df.loc[]` and `df.iloc[]`?",
        "options": [
            "`loc` uses label-based indexing; `iloc` uses 0-based integer position indexing",
            "`loc` is for columns only; `iloc` is for rows only",
            "`iloc` supports string column names; `loc` only takes integers",
            "`loc` modifies the DataFrame in-place; `iloc` creates a copy"
        ],
        "correct_option_index": 0,
        "explanation": "`loc` accesses rows/columns by explicit index/column labels; `iloc` accesses them by integer position indices.",
        "difficulty": "Easy"
    },

    # 11. Product Management & Strategy
    {
        "topic": "Product Management",
        "subtopic": "Prioritization",
        "question_text": "In product roadmap planning, how is the RICE prioritization score computed?",
        "options": [
            "Revenue * Impact * Cost / Efficiency",
            "(Reach * Impact * Confidence) / Effort",
            "Risk + Investment + Customers - Expense",
            "Reach / (Impact * Cost * Effort)"
        ],
        "correct_option_index": 1,
        "explanation": "RICE framework calculates score as (Reach * Impact * Confidence) / Effort to objectively rank feature backlogs.",
        "difficulty": "Easy"
    },
    {
        "topic": "Product Management",
        "subtopic": "Experimentation",
        "question_text": "In A/B testing, what does a p-value less than 0.05 typically signify?",
        "options": [
            "The test variant is guaranteed to increase revenue by 95%",
            "There is less than a 5% probability that the observed conversion difference occurred by random chance (Statistically Significant)",
            "The test had 5% sample size power",
            "The experiment needs to run for 5 more weeks"
        ],
        "correct_option_index": 1,
        "explanation": "A p-value < 0.05 indicates statistical significance: we reject the null hypothesis with >95% confidence.",
        "difficulty": "Medium"
    },

    # 12. Corporate Finance & Strategy
    {
        "topic": "Corporate Finance",
        "subtopic": "Valuation",
        "question_text": "In a Discounted Cash Flow (DCF) valuation, what impact does an increase in the Weighted Average Cost of Capital (WACC) have on Enterprise Value?",
        "options": [
            "Increases Enterprise Value because cost of capital is an asset",
            "Decreases Enterprise Value because future cash flows are discounted at a higher rate",
            "Has no effect on Enterprise Value",
            "Doubles the terminal value"
        ],
        "correct_option_index": 1,
        "explanation": "WACC serves as the discount rate denominator. A higher discount rate reduces the present value of future projected cash flows.",
        "difficulty": "Medium"
    },

    # 13. Aptitude
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

    added = 0
    for q_data in SEED_QUESTIONS:
        exists = session.query(Question).filter(Question.question_text == q_data["question_text"]).first()
        if not exists:
            q = Question(**q_data)
            session.add(q)
            added += 1
    session.commit()
    return session.query(Question).count()


if __name__ == "__main__":
    from database.database import SessionLocal, init_db
    init_db()
    db = SessionLocal()
    try:
        num = seed_questions(db)
        print(f"Successfully seeded {num} questions into placement question bank.")
    finally:
        db.close()
