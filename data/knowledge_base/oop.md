# Object-Oriented Programming (OOP)

## Four Core Pillars of OOP
- Encapsulation: Bundling data (attributes) and methods that operate on that data within a single unit (class), restricting direct unauthorized access using access modifiers (private, protected, public).
- Abstraction: Hiding internal implementation details and exposing only essential functional interfaces (via abstract classes and interfaces).
- Inheritance: Mechanism where a new class (derived/subclass) acquires properties and behaviors from an existing class (base/superclass), promoting code reuse.
- Polymorphism: The ability of an entity to take on multiple forms:
  - Compile-Time / Static: Method Overloading and Operator Overloading.
  - Run-Time / Dynamic: Method Overriding achieved via virtual methods and dynamic dispatch.

## SOLID Principles of Software Design
- Single Responsibility Principle (SRP): A class should have only one reason to change, meaning it should perform a single cohesive function.
- Open/Closed Principle (OCP): Software artifacts should be open for extension, but closed for modification.
- Liskov Substitution Principle (LSP): Subtypes must be substitutable for their base types without altering program correctness.
- Interface Segregation Principle (ISP): Clients should not be forced to depend on interfaces they do not use (prefer small, role-specific interfaces).
- Dependency Inversion Principle (DIP): High-level modules should not depend on low-level modules; both should depend on abstractions.
