# Data Structures and Algorithms

## Arrays and Two-Pointer Techniques
An array is a contiguous memory allocation of fixed or dynamic elements. Common patterns include the Two-Pointer Technique (used for sorted pair sums, removing duplicates, and container with most water) and the Sliding Window Technique (used for contiguous subarray problems like minimum size subarray sum or longest substring without repeating characters).
- Time Complexity: Lookup by index is O(1). Insertion or deletion at arbitrary position is O(N) due to element shifting.
- Space Complexity: O(N) for storing N elements.

## Binary Search Trees (BST) and Balanced Trees
A Binary Search Tree satisfies the binary search invariant: for every node X, all values in X's left subtree are strictly less than X.val, and all values in X's right subtree are strictly greater than X.val.
- Balanced BST (AVL, Red-Black): Guarantees O(log N) height. Operations including search, insert, and delete take O(log N) time.
- Unbalanced / Skewed BST: Height degrades to O(N), causing operations to degrade to linear time O(N).
- Inorder Traversal: An inorder traversal (Left, Root, Right) of a BST produces elements in strictly monotonically increasing sorted order.

## Dynamic Programming (DP)
Dynamic Programming is an algorithmic paradigm that solves complex problems by breaking them down into simpler overlapping subproblems and storing the intermediate solutions to avoid redundant computations (Memoization in Top-Down, Tabulation in Bottom-Up).
- Key Properties Required:
  1. Overlapping Subproblems: The problem re-evaluates the same subproblems repeatedly (unlike Divide and Conquer where subproblems are disjoint).
  2. Optimal Substructure: An optimal solution to the global problem can be constructed from optimal solutions to its subproblems.
- Classic Paradigms: 0/1 Knapsack, Longest Common Subsequence (LCS), Longest Increasing Subsequence (LIS), Matrix Chain Multiplication, Coin Change Problem.

## Graph Algorithms
Graphs consist of vertices (V) and edges (E) that can be directed or undirected, weighted or unweighted.
- Breadth-First Search (BFS): Uses a queue to explore layer-by-layer. Guarantees the shortest path in unweighted graphs in O(V + E) time.
- Depth-First Search (DFS): Uses recursion or an explicit stack to explore as deep as possible. Ideal for cycle detection, topological sorting, and strongly connected components.
- Dijkstra's Algorithm: Finds the single-source shortest path in graphs with non-negative edge weights using a Min-Priority Queue in O((V + E) log V) time.
- Bellman-Ford Algorithm: Computes single-source shortest paths and detects negative weight cycles in O(V * E) time.
