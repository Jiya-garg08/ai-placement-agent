# Database Management Systems

## ACID Properties of Transactions
A transaction is an atomic logical unit of work in a DBMS. To ensure data integrity, the system must guarantee the four ACID properties:
- Atomicity: 'All-or-nothing'. Either all operations of the transaction complete successfully, or the database is rolled back to its initial state.
- Consistency: The database must remain in a valid state satisfying all defined integrity constraints before and after transaction execution.
- Isolation: Concurrent transactions must execute without interfering with one another. Isolation levels include Read Uncommitted, Read Committed, Repeatable Read, and Serializable.
- Durability: Once a transaction commits, its modifications are permanently recorded on non-volatile storage (WAL / redo logs) even across power failures.

## Normalization and Normal Forms
Normalization eliminates data redundancy and update anomalies (insertion, deletion, modification anomalies) by decomposing relations:
- First Normal Form (1NF): All attributes must hold atomic (indivisible) values with no repeating groups or arrays.
- Second Normal Form (2NF): Must be in 1NF and have no partial functional dependencies (every non-prime attribute must be fully functionally dependent on the entire candidate key).
- Third Normal Form (3NF): Must be in 2NF and have no transitive functional dependencies (no non-prime attribute determines another non-prime attribute).
- Boyce-Codd Normal Form (BCNF): A stricter version of 3NF. For every non-trivial functional dependency X -> Y, X must be a super key.

## Database Indexing and B+ Trees
Indexing creates an auxiliary search data structure to speed up data retrieval without scanning every record.
- Clustered Index: Determines the physical order of data on disk. Only one clustered index per table (typically the Primary Key).
- Non-Clustered / Secondary Index: Contains a copy of the indexed columns paired with row pointers back to the clustered index or heap.
- B+ Trees: The de facto storage structure for relational indexes. All data records/pointers reside strictly in the leaf nodes, which are doubly linked for rapid range queries. Non-leaf nodes only store routing keys. Height remains low (O(log B N)), providing consistent I/O performance.
