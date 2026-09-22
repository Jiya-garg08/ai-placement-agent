# Python Programming

## Memory Management and Garbage Collection
Python uses automatic memory management consisting of:
- Reference Counting: Every Python object tracks how many references point to it. When the count drops to zero, the memory is deallocated immediately.
- Cyclic Garbage Collector (Generational GC): Periodically detects and resolves reference cycles (e.g. object A references B, and B references A) across three generations (Gen 0, Gen 1, Gen 2).

## Global Interpreter Lock (GIL)
CPython (the reference implementation of Python) utilizes the Global Interpreter Lock:
- Mutex lock preventing multiple native OS threads from executing Python bytecodes simultaneously.
- Purpose: Simplifies memory management and guarantees thread safety for C extension modules and reference counts.
- Concurrency Impact: Multi-threaded Python programs achieve true parallelism for I/O-bound tasks (network, disk) where threads release the GIL. For CPU-bound tasks, multiprocessing or process pools are required to bypass the GIL across multiple CPU cores.

## Generators, Iterators, and Decorators
- Iterators: Objects implementing `__iter__()` and `__next__()` protocols.
- Generators: Functions containing the `yield` statement. They return lazy generator iterators that compute values on-the-fly without holding entire sequences in memory, providing high memory efficiency.
- Decorators: Higher-order functions that take a function as an argument, wrap additional behavior around it (e.g. caching, logging, authentication), and return the modified function without altering the original source code.
