# Java Programming

## JVM Architecture and Memory Model
The Java Virtual Machine (JVM) provides cross-platform execution ('Write Once, Run Anywhere') by executing compiled Java bytecode:
- Heap Memory: Shared runtime memory where all object instances and arrays are allocated. Subject to automated Garbage Collection (Young Gen: Eden, S0, S1; Old/Tenured Gen).
- Stack Memory: Thread-private memory allocating stack frames for method invocations, holding primitive local variables and object reference pointers.
- Metaspace: Stores class metadata, bytecode, and static variables outside the heap in native memory.

## Object-Oriented Programming & Inheritance in Java
Java is an object-oriented programming language built upon inheritance, polymorphism, encapsulation, and abstraction:
- Inheritance Mechanism: Allows a subclass (derived class) to acquire fields and methods from a superclass (base class) using the `extends` keyword.
  - Types of Inheritance: Supports Single (`class B extends A`), Multilevel (`class C extends B`), and Hierarchical (`class B extends A`, `class C extends A`) inheritance.
  - Diamond Problem & Multiple Inheritance: Java does not permit multiple class inheritance (`class C extends A, B`) to avoid method resolution ambiguity (the Diamond Problem). Multiple inheritance of type is cleanly achieved via interfaces using the `implements` keyword.
  - `super` Keyword: Invokes superclass constructors (`super()`) or superclass overridden methods (`super.method()`).
  - Method Overriding (`@Override`): Occurs when a subclass provides a specific implementation of a method declared in its superclass with the exact same name, return type, and signature. Resolution occurs dynamically at runtime (Dynamic Method Dispatch / Runtime Polymorphism).
  - Abstract Classes vs Interfaces: Abstract classes can have state and constructors; interfaces define pure behavioral contracts with default and static methods (Java 8+).

## Collections Framework
- List Interface: Ordered collection allowing duplicate elements:
  - ArrayList: Dynamic array with fast O(1) random access lookup, O(N) worst-case insertions.
  - LinkedList: Doubly-linked list with O(1) insertions/deletions at ends, O(N) traversal.
- Map Interface: Key-value associative mapping:
  - HashMap: Hash-table based, O(1) average lookup/insert. Uses linked list bucket chains that convert to balanced Red-Black Trees when bucket collisions exceed 8 nodes (TREEIFY_THRESHOLD in Java 8+).
  - ConcurrentHashMap: Thread-safe map using bucket-level fine-grained locking (CAS + synchronized nodes) rather than global table locks.

## Exception Handling and Robustness
- Checked Exceptions: Subclasses of `Exception` (excluding `RuntimeException`) checked at compile-time (e.g. `IOException`, `SQLException`), requiring explicit `try-catch` or `throws`.
- Unchecked Exceptions: Subclasses of `RuntimeException` occurring during execution (e.g. `NullPointerException`, `ArrayIndexOutOfBoundsException`).
