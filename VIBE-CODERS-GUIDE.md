# What Every Vibe Coder Must Know

> A book for people who can make things work but want to understand *why* they work.
> Written during live teaching sessions. Updated as we learn.

---

## Chapter 1: Data Structures — How Computers Organize Things

### 1.1 The Problem

You tell the computer: "Store this information."

But the computer doesn't know *how* to store it. It's just a machine that follows instructions. You have to tell it exactly what shape to put the data in.

That shape is called a **data structure**.

### 1.2 The Shopping List (Array/List)

**What it is:** A list of items in order.

**Real life:** A shopping list. A to-do list. A playlist.

**How it works:**
- Items have positions (1st, 2nd, 3rd)
- You find things by their position
- You can add things to the end, or insert in the middle

**When to use it:** When order matters. When you need to go through everything.

**When NOT to use it:** When you need to find one specific thing quickly.

### 1.3 The Phone Book (Dictionary/Object/Map)

**What it is:** A collection of key-value pairs.

**Real life:** A phone book (name → number). A dictionary (word → definition). A contact list (name → phone, email, address).

**How it works:**
- You look things up by a "key" (like a name)
- The computer instantly jumps to the value
- Order doesn't matter

**When to use it:** When you need to find things fast by name or ID.

**When NOT to use it:** When order matters, or when you need to do something to every item.

---

## Chapter 2: The Graph — The Most Important Data Structure You've Never Heard Of

### 2.1 The Limitation of Lists and Dictionaries

Lists are great for ordered things. Dictionaries are great for lookups.

But neither handles **connections between things** well.

- If you use a list of files, you lose the information that "file A imports file B."
- If you use a dictionary, you can look up a file, but you can't easily find "what imports this file?"

### 2.2 What Is a Graph?

A graph is a data structure built for **connections**.

**Real life:**
- A city map (cities connected by roads)
- A social network (people connected by friendships)
- The internet (websites connected by links)

**In software:**
- Files connected by imports
- Functions connected by calls
- Services connected by network requests

### 2.3 Nodes and Edges

Every graph has two ingredients:

| Part | What it is | Real-life example |
|------|-----------|-------------------|
| **Node** (also called Vertex) | A thing | A city, a person, a file |
| **Edge** | A connection between two nodes | A highway, a friendship, an import |

### 2.4 Why Folders Aren't Enough

Folders organize files in a **tree** — one parent, no cycles. A file lives in exactly one place.

But real code has many connections:
- A file imports code from other folders
- A file is tested by multiple test files
- A file is owned by a specific team
- A file implements a feature

Folders can only show one of these (where the file lives). A graph can show ALL of them simultaneously.

### 2.5 Dark Matter's Graph

Dark Matter builds a graph of your entire codebase:

```
(auth/login.ts) ──imports──→ (lib/validation.ts)
(auth/login.ts) ──tested_by──→ (tests/login.test.ts)
(Feature: Login) ──implements──→ (auth/login.ts)
(Decision: Use JWT) ──affects──→ (auth/login.ts)
```

With this graph, Dark Matter can answer:
- "What does this file depend on?" → Follow outgoing edges
- "What depends on this file?" → Follow incoming edges
- "Which features are affected by this change?" → Traverse the graph
- "Why was this decision made?" → Follow the decision edge

### 2.6 Why This Matters for Vibe Coders

When you use Cursor, Copilot, or Claude to write code, the AI sees only the files you give it. It doesn't see the **structure** of your project — the connections between files, the decisions that shaped the architecture, the business rules buried in the code.

Dark Matter's graph captures that structure. Any AI that reads the graph instantly understands your project as well as a senior engineer who's worked on it for months.

---

## Chapter 3: The File System — Where Files Actually Live

### 3.1 The User's View vs. The Reality

**You see:** Folders and files in a nice tree.

**Disk sees:** Just a long sequence of 1s and 0s with no structure at all.

The **file system** is the data structure that bridges the two. It's a card catalog that maps "file names and folders" to "positions on the disk."

### 3.2 What Happens When You Open a File

```
       You double-click a file
               │
               ▼
  ┌─────────────────────────┐
  │     Operating System    │  Windows, Mac, Linux
  │  (manages everything)   │
  └─────────┬───────────────┘
            │ "Find this file"
            ▼
  ┌─────────────────────────┐
  │      File System        │  NTFS, APFS, ext4
  │  (the card catalog)     │
  └─────────┬───────────────┘
            │ "It's at disk sectors 442-448"
            ▼
  ┌─────────────────────────┐
  │    Physical Disk        │  The actual hardware
  │  (reads raw bytes)      │
  └─────────┬───────────────┘
            │ "Here are the bytes"
            ▼
  ┌─────────────────────────┐
  │      Your App           │
  │  (gets the content)     │
  └─────────────────────────┘
```

### 3.3 Common File Systems

| Name | Used By | Since | Tradeoffs |
|------|---------|-------|-----------|
| NTFS | Windows | 1993 | Fast, supports huge files, permissions built-in |
| APFS | Mac | 2017 | Optimized for SSDs, snapshots built-in |
| ext4 | Linux | 2008 | Stable, open-source, most Linux servers |
| FAT32 | USB drives | 1996 | Works everywhere, but max file size is 4GB |

### 3.4 Why Dark Matter Doesn't Care

Dark Matter runs on Windows, Mac, and Linux. It works the same on all three because it doesn't talk to the file system directly. It talks to the **operating system**, which talks to the file system.

```
dm scan → OS → File System → Disk
```

This is called an **abstraction layer** — Dark Matter only needs to know how to ask the OS for files. The details of NTFS vs APFS vs ext4 are invisible.

---

## Chapter 4: Processes — Programs That Are Running

### 4.1 Program vs. Process

This is one of the most important distinctions in all of software:

| | **Program** | **Process** |
|---|---|---|
| What it is | A file on disk | A running instance in memory |
| Can you see it? | Yes, it's a `.exe` or `.py` file | Only in Task Manager / Activity Monitor |
| How many? | One file = one program | You can run the same program 10 times = 10 processes |
| Example | `python.exe` sitting on your C drive | The `python.exe` that's running `dm scan` right now |

### 4.2 What Every Process Has

- **Memory** — Its own private chunk of RAM
- **PID** — A unique process ID number
- **State** — Running, sleeping, waiting, or stopped
- **Resources** — CPU time it used, files it has open, network connections

### 4.3 What Happens When You Run a Command

```
You type "python main.py"
       │
       ▼
OS finds python.exe on disk
       │
       ▼
OS carves out a fresh slice of RAM
       │
       ▼
OS loads python.exe into that RAM
       │
       ▼
OS starts executing from the first instruction
       │
       ▼
python.exe reads main.py and starts interpreting it line by line
       │
       ▼
When done, OS reclaims the RAM (process is dead)
```

### 4.4 Why Dark Matter Uses Files

Processes cannot see each other's memory. When `dm scan` runs, it creates data in its own private RAM. When it finishes, that RAM is reclaimed. Everything is lost.

That's why Dark Matter writes to `.darkmatter/` files — they survive on disk after the process dies. Next time you run `dm scan`, it reads those files and continues where it left off.

### 4.5 How Processes Communicate (IPC)

Since processes can't share memory, they send messages:

| Method | How It Works | Used By |
|--------|-------------|---------|
| **Files** | One writes, another reads | Dark Matter, Git, VS Code |
| **Network** | Both send data over localhost | Your browser talking to a local dev server |
| **Pipes** | Direct stream from one to another | `grep | sort` in terminal |
| **Signals** | One says "stop" or "pause" | Ctrl+C kills a running process |

Dark Matter uses method #1 (files). This is the simplest and most universal.

---

## Chapter 5: Interpreters vs. Compilers — The Two Ways Code Runs

### 5.1 The Core Difference

Every programming language falls into one of two camps:

| | **Interpreted** | **Compiled** |
|---|---|---|
| How it runs | Line by line, in real time | Translated to machine code ahead of time |
| Speed | Slower (middleman slows things down) | Faster (CPU runs directly) |
| Development | Change code, run immediately | Change code, compile, then run |
| Examples | Python, JavaScript, Ruby, PHP | C, C++, Rust, Go, Zig |

### 5.2 The Analogy

**Interpreter** is like a live translator at a meeting. The speaker says a sentence, the translator repeats it in another language. You can respond immediately, but it takes twice as long per sentence.

**Compiler** is like translating a book. You spend hours translating the whole thing upfront. But once it's done, anyone can read the translated book instantly with no middleman.

### 5.3 What Dark Matter Actually Is

Dark Matter does both:

```
aether scan     ← Interpreter mode (reads files one by one, builds graph)
aether compile  ← Compiler mode (reads graph, produces repository.ai)
```

- `scan` is the interpreter — live, interactive, file-by-file
- `compile` is the compiler — takes the graph and produces a portable package

### 5.4 Dark Matter Is Both (And How That Works)

Think of Dark Matter as a toolkit containing multiple tools:

| Command | Role | Analogy |
|---------|------|---------|
| `dm scan` | **Interpreter** | Reads your project, file by file, extracts facts |
| `dm compile` | **Compiler** | Takes the finished graph, writes `repository.ai` |

They're separate commands. You can run one, then the other, or just one if that's all you need.

The key insight: being an interpreter or a compiler isn't about the programming language something is *written in*. It's about what it *does* with data. Reads line by line? Interpreter. Takes input and produces a different output? Compiler.

---

## Chapter 6: APIs — How Programs Talk to Each Other

### 6.1 The Problem

Two programs can't see each other's memory. They're separate processes, each in their own private sandbox.

But they need to exchange data — ask questions, send commands, get results.

That's what an **API** (Application Programming Interface) is: the agreed-upon way for two programs to talk.

### 6.2 The Waiter — The Right Analogy

A restaurant has three parts:

| Part | What it is | In software |
|------|-----------|-------------|
| **Kitchen** | Does the actual work | The backend server |
| **Menu** | Lists what's available | The API documentation / spec |
| **Waiter** | Carries orders and food between you and the kitchen | The **API itself** |

The menu is **not** the API. The menu is the *documentation* for the API. People often confuse the two.

**The waiter IS the API.** You give the waiter an order (request). The waiter goes to the kitchen (backend). The kitchen cooks (processes). The waiter brings back food (response).

### 6.3 What a Menu Actually Is

A restaurant menu = a **contract** or **specification**:
- What dishes exist (what endpoints are available)
- What each dish costs (what auth or rate limits apply)
- What comes in each dish (what parameters the endpoint accepts)

The menu tells you what you *could* order. The waiter is how you actually order it.

### 6.4 The Phone Number Analogy

A restaurant's **phone number** is like an **address** — it tells you where to send your order.

```
Phone number:   0-800-RESTAURANT
IP address:     192.168.1.42:8080
```

But the phone number is not the waiter. You dial the number, then you talk to the person who answers — that person is the interface.

### 6.5 The Four Kinds of APIs

| Kind | How It Works | Example |
|------|-------------|---------|
| **CLI** | Run a command, get output | `dm scan` — you type, computer responds |
| **Library** | Call a function from code | `os.listdir()` — your code calls Python's code |
| **Network** | Send a request over HTTP | Your browser talks to a server |
| **File-based** | One writes a file, another reads it | Dark Matter writes `.darkmatter/`, other tools read it |

Dark Matter uses **all four**:
- `dm scan`, `dm compile` → **CLI API** (you talk to Dark Matter)
- Python `import dm` → **Library API** (your code calls Dark Matter's internals)
- Network (planned) → **Network API** (other machines query the graph)
- `.darkmatter/` files → **File-based API** (any tool can read the stored intelligence)

### 6.6 API Keys, Endpoints, and Protocols

These three concepts get tangled. Here's the clean distinction:

| Term | What it is | Restaurant analogy |
|------|-----------|-------------------|
| **Endpoint** | *Where* to send the request | The restaurant's address + which door (takeout vs dine-in) |
| **Protocol** | *How* to format the request | Speaking English vs Spanish, ordering by phone vs in person |
| **API Key** | *Who* is making the request | A membership card that identifies you |

You can have an API without any of these. `dm scan` has no keys, no endpoints, no protocol negotiation — you just type the command. But all three exist when programs talk over a network.

### 6.7 Why This Matters for Dark Matter

Every piece of Dark Matter is connected by APIs:

```
┌──────────┐    CLI API     ┌──────────────┐
│  You     │ ─────────────→ │  dm scan     │
│ (CLI)    │ ←───────────── │  (collector) │
└──────────┘                └──────┬───────┘
                                   │ File-based API
                                   ▼
                            ┌──────────────┐
                            │  .darkmatter/ │
                            │  (evidence)   │
                            └──────┬───────┘
                                   │ Library API
                                   ▼
                            ┌──────────────┐
                            │  GraphService │
                            │  (builds)     │
                            └──────────────┘
```

Each layer only talks through the agreed interface. The collector doesn't care how the graph is built. The graph service doesn't care how files were read. That's the point of APIs — **decoupling**.

### 6.8 tl;dr

- A menu = spec/documentation, NOT the API
- An API = the actual mechanism for communication (the waiter)
- A phone number = an address/endpoint, NOT the API
- There are 4 kinds: CLI, Library, Network, File-based
- Every program boundary is an API

---

## Appendix: The Master Concept Graph

Everything in this book is connected. Here's how.

```
                          ┌──────────────────────────────────────┐
                          │         LEVEL 1: CONCEPT MAP         │
                          └──────────────────────────────────────┘

  CHAPTER 1: DATA STRUCTURES
  ──────────────────────────────────────────────────────────
  [List (Array)] ───ordered──→ [items by position]
     │                            │
     │                         use when: order matters
     │                         avoid when: need fast lookup
     ▼
  [Dict (Map/Object)] ─key-value──→ [fast lookup by name]
     │                                │
     │                             use when: need to find by ID
     │                             avoid when: order matters
     │                                │
     │                                ▼
     │                        [File System: filename→disk location]
     │                                │
     ▼                                ▼
  [Graph] ←────generalization───────┘
     │
     ├──has──→ [Node]  (a thing: file, function, person, city)
     ├──has──→ [Edge]  (a connection: imports, calls, road)
     │
     │  use when: connections between things matter
     │  avoid when: simple list or lookup is enough
     │
     ▼
  CHAPTER 2: GRAPHS vs TREES
  ──────────────────────────────────────────────────────────
  [Folder Tree] ←────comparison──────→ [Graph]
     │                                      │
     │ one parent, no cycles                │ many parents, cycles OK
     │ a file lives in ONE place            │ a file has MANY relationships
     │                                      │
     │ shows: hierarchy only                │ shows: imports, tests, ownership,
     ▼                                      │         features, decisions
  [OS organizes files]                      ▼
     │                              [Dark Matter organizes knowledge]
     │                                      │
     │                                      ├── "What does this depend on?"
     │                                      ├── "What depends on this?"
     │                                      ├── "What features are affected?"
     │                                      └── "Why was this decision made?"
     │
     ▼
  CHAPTER 3: FILE SYSTEM
  ──────────────────────────────────────────────────────────
  [User: "open file"] ──request──→ [OS] ──ask──→ [File System Driver]
     │                                                    │
     │                                        ┌───────────┼───────────┐
     │                                        ▼           ▼           ▼
     │                                   [NTFS]      [APFS]      [ext4]
     │                                   (Windows)   (Mac)       (Linux)
     │                                        │           │           │
     │                                        └───────────┼───────────┘
     │                                                    ▼
     │                                             [Physical Disk]
     │                                                    │
     │               ┌─── "Where is my file?" ────────────┘
     │               │   (uses a Dict: filename → sectors)
     │               ▼
     └─── response: bytes ──────────────────────────────────┘
     │
     ▼
  [Abstraction Layer]
     │
     ├── Dark Matter doesn't care which FS (NTFS/APFS/ext4)
     ├── It asks the OS the same way on every system
     └── This is called: OS abstraction
     │
     ▼
  CHAPTER 4: PROCESSES
  ──────────────────────────────────────────────────────────
  [Program: file on disk] ──────run─────────→ [Process: running in RAM]
     (.exe, .py, binary)                        │
                                                ├──has──→ [PID (unique ID)]
                                                ├──has──→ [Private Memory]
                                                ├──has──→ [State]
                                                │         ├── Running
                                                │         ├── Sleeping
                                                │         ├── Waiting
                                                │         └── Stopped
                                                └──has──→ [Resources
                                                         (CPU, files, network)]
     │
     │  "Run same program 10x → 10 processes"
     │
     ▼
  [IPC: How Processes Talk]
     │
     ├──[Files]    → Dark Matter writes .darkmatter/
     ├──[Network]  → Browser ↔ local dev server
     ├──[Pipes]    → grep | sort
     └──[Signals]  → Ctrl+C kills process
     │
     │  Why DM uses files: simplest, universal, survives reboot
     │
     ▼
  CHAPTER 5: INTERPRETERS vs COMPILERS
  ──────────────────────────────────────────────────────────
  [Source Code (.py, .js, .c, .rs)]
     │
     ├── INTERPRETER ──reads line by line NOW──→ [Python, JavaScript]
     │      │                                            │
     │      │  Analogy: live translator at a meeting     │
     │      │  Tradeoff: slower, but instant feedback    │
     │      │                                            │
     │      └── dm scan is an interpreter ───────────────┘
     │
     └── COMPILER ──translates AHEAD of time──→ [C, Rust, Go]
            │                                            │
            │  Analogy: translating an entire book       │
            │  Tradeoff: faster execution, slower build  │
            │                                            │
            └── dm compile is a compiler ────────────────┘
     │
     │  Key insight: the same program can be both!
     │  Python itself could be compiled (Cython, Nuitka)
     │  It's about what the tool DOES, not what language it's written in
     │
     ▼
  CHAPTER 6: APIs
  ──────────────────────────────────────────────────────────
  [Restaurant]
     │
     ├── [Menu] ──────────is──→ [Spec / Documentation]
     │                            Not the API itself!
     │
     ├── [Waiter] ────────is──→ [The API itself]
     │     You tell waiter your order (request)
     │     Waiter brings food (response)
     │
     └── [Phone Number] ──is──→ [Address / Endpoint]
                                  "Where to send the request"
     │
     ▼
  [4 Kinds of APIs]
     │
     ├── CLI ───────────────→ dm scan, dm compile
     │   (you type, computer responds)
     │
     ├── Library ───────────→ import dm
     │   (your code calls DM's code)
     │
     ├── Network ───────────→ HTTP requests (planned)
     │   (one machine talks to another)
     │
     └── File-based ────────→ .darkmatter/ files
         (one writes, another reads)
     │
     ▼
  [API Concepts (not the same thing!)]
     │
     ├── Endpoint ──"where"──→ The restaurant address
     ├── Protocol  ──"how"──→ Speaking English vs ordering by phone
     └── API Key   ──"who"──→ A membership card identifying you
```

## Cross-Chapter Connections

The most important part — how chapters link together:

```
[List]              → OS uses lists for directory contents
[Dict]              → File System maps filename → disk location
[Graph]             → Dark Matter's core data structure
[Tree]              → File System folder hierarchy
[File System]       → Stores programs on disk
[Program]           → When run, becomes a Process
[Process Memory]    → Lost when process dies → why DM uses files
[IPC: Files]        → Dark Matter persists .darkmatter/ via this
[Interpreter]       → Creates a Process (Python interpreter running)
[Compiler]          → Produces machine code → can run as new Process
[API: CLI]          → How YOU talk to Dark Matter
[API: Library]      → How YOUR CODE talks to Dark Matter
[API: File-based]   → How .darkmatter/ stores graph data
[Interpreter]       → dm scan reads files one by one
[Compiler]          → dm compile turns graph → repository.ai
```

## What This Graph Reveals

A table of contents can't show you these connections:

1. **Ch1→Ch3:** File System is built on a Dict — filename → disk location. You learned dicts, then saw them hiding inside your OS.

2. **Ch4→Ch5:** Interpreters ARE processes. When you run `python main.py`, the interpreter becomes a running process with memory, PID, and state. They're not separate topics — one IS an instance of the other.

3. **Ch4→Ch6:** APIs exist because processes can't share memory. Ch4 teaches the problem (process isolation). Ch6 teaches the solution (APIs). Same coin, two sides.

4. **Every→DM:** Dark Matter touches every concept — graphs (core data structure), file system (reads files), processes (CLI commands), interpreters (scan), compilers (compile), APIs (all 4 kinds).

5. **Turtles all the way down:** Lists need memory (Ch4). Dicts are implemented in code (Ch5). Code needs a file system (Ch3). Files are organized in trees (Ch2). Trees are a kind of graph (Ch1). Everything connects.

---

*This book is written in real-time as the author learns. If something is unclear, it's because we haven't gotten there yet.*
