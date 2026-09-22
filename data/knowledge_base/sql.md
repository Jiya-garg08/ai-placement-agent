# Structured Query Language (SQL)

## SQL Joins
SQL joins combine rows from two or more tables based on a related column between them:
- INNER JOIN: Returns records that have matching values in both tables.
- LEFT (OUTER) JOIN: Returns all records from the left table, and the matched records from the right table. Unmatched right columns contain NULL.
- RIGHT (OUTER) JOIN: Returns all records from the right table, and matched records from the left table.
- FULL (OUTER) JOIN: Returns all records when there is a match in either the left or right table.
- CROSS JOIN: Produces the Cartesian product of rows from both tables.

## Aggregate Functions and Group By
Aggregation processes multiple values to return a single summary result:
- Functions: COUNT(), SUM(), AVG(), MIN(), MAX().
- GROUP BY: Groups rows with identical values in specified columns into summary rows.
- HAVING Clause: Filters groups produced by GROUP BY based on aggregate conditions (e.g. HAVING COUNT(*) > 5). Note: WHERE filters rows before grouping; HAVING filters groups after aggregation.

## Window Functions
Window functions perform calculations across a set of table rows related to the current row without collapsing the rows into a single summary output:
- Syntax: FUNCTION() OVER (PARTITION BY col1 ORDER BY col2).
- Ranking Functions:
  - ROW_NUMBER(): Assigns unique sequential integers starting at 1 with no ties.
  - RANK(): Assigns rank with gaps for ties (e.g. 1, 2, 2, 4).
  - DENSE_RANK(): Assigns rank without gaps for ties (e.g. 1, 2, 2, 3).
- Value Functions: LEAD() accesses rows ahead, LAG() accesses rows behind, FIRST_VALUE(), LAST_VALUE().
