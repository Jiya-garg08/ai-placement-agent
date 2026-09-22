# Operating Systems

## Processes and Threads
- Process: An instance of an executing program with an independent virtual memory address space (Text, Data, Heap, Stack). Managed via a Process Control Block (PCB).
- Thread: The smallest unit of execution within a process. Threads within the same process share the heap, code segment, and open files, but maintain private stacks, program counters, and registers.
- Context Switching: The CPU state-saving and restoration cost when switching execution from one process or thread to another.

## Deadlocks and Coffman Conditions
A deadlock is a permanent state where two or more processes are blocked waiting for resources held by each other.
- The 4 Coffman Conditions (all must hold simultaneously):
  1. Mutual Exclusion: At least one non-shareable resource must be held by a process.
  2. Hold and Wait: A process holding resources can request additional resources without releasing current ones.
  3. No Preemption: Resources cannot be forcibly taken away from a process; they must be released voluntarily.
  4. Circular Wait: A closed chain of processes exists such that each process holds resources needed by the next.
- Avoidance: Banker's Algorithm ensures the system remains in a safe state before granting resource requests.

## Virtual Memory, Paging, and Thrashing
- Virtual Memory: Decouples process logical memory addresses from physical RAM addresses, allowing execution of processes larger than physical memory.
- Paging: Memory is divided into fixed-size blocks called pages (logical) and frames (physical). A Page Table maps pages to frames.
- Page Fault: Occurs when a referenced page is not present in physical RAM, prompting the OS to fetch it from secondary storage (swap).
- Thrashing: Occurs when high multiprogramming causes processes to spend more time swapping pages in and out of disk than executing useful CPU instructions.
