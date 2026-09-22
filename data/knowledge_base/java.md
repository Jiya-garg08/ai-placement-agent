# Java Programming

## JVM Architecture and Memory Model
The Java Virtual Machine (JVM) provides cross-platform execution ('Write Once, Run Anywhere') by executing compiled Java bytecode:
- Heap Memory: Shared runtime memory where all object instances and arrays are allocated. Subject to automated Garbage Collection (Young Gen: Eden, S0, S1; Old/Tenured Gen).
- Stack Memory: Thread-private memory allocating stack frames for method invocations, holding primitive local variables and object reference pointers.
- Metaspace: Stores class metadata, bytecode, and static variables outside the heap in native memory.

## Collections Framework
- List Interface: Ordered collection allowing duplicate elements:
  - ArrayList: Dynamic array with fast O(1) random access lookup, O(N) worst-case insertions.
  - LinkedList: Doubly-linked list with O(1) insertions/deletions at ends, O(N) traversal.
- Map Interface: Key-value associative mapping:
  - HashMap: Hash-table based, O(1) average lookup/insert. Uses linked list bucket chains that convert to balanced Red-Black Trees when bucket collisions exceed 8 nodes (TREEIFY_THRESHOLD in Java 8+).
  - ConcurrentHashMap: Thread-safe map using bucket-level fine-grained locking (CAS + synchronized nodes) rather than global table locks.
