# KanbanAgent

A compact, cross-platform Kanban board application that enables multiple agents to collaboratively manage and track tasks with simplicity and reliability.

## Overview

KanbanAgent is a lightweight yet robust task management system built around the Kanban methodology. It provides a clean interface for creating tasks, moving them across workflow columns (`To Do`, `In Progress`, `Done`), and updating their metadata — all backed by deterministic, well-tested components. Designed for clarity and maintainability, it separates concerns into two core classes: `KanbanBoard` (workflow orchestration) and `TaskManager` (task lifecycle control). The architecture supports extensibility while enforcing immutability where appropriate and validating state transitions rigorously.

## Key Features

- ✅ **Column-based workflow**: Tasks live in one of three canonical statuses — `To Do`, `In Progress`, or `Done`.
- ✅ **Task creation & metadata management**: Each task has an ID, title, description, and status.
- ✅ **Safe status transitions**: `move_task()` validates existence and prevents invalid or redundant moves.
- ✅ **Partial updates**: Update only title, description, status — or any combination — without overwriting other fields.
- ✅ **Deterministic unit tests**: Comprehensive test suite covering edge cases (e.g., missing tasks, duplicate IDs, no-op moves).
- ✅ **Cross-platform compatibility**: Pure Python implementation with zero external dependencies beyond `unittest`.

## How It Works

The system operates via two tightly coordinated components:

1. **`KanbanBoard`**  
   Represents the visual board layout and orchestrates high-level workflow logic. Internally, it maintains:
   - A `board: Dict[str, List[int]]` mapping each column name to a list of task IDs (preserving insertion order).
   - A `tasks: Dict[int, Dict[str, str]]` registry storing full task details keyed by ID.  
   Its methods (`create_task`, `move_task`, `update_task`) enforce business rules: new tasks always start in `To Do`; moving requires existence checks and column validation; updates are non-destructive and field-specific.

2. **`TaskManager`**  
   Provides low-level, state-agnostic task persistence and mutation. Unlike `KanbanBoard`, it does *not* enforce workflow semantics — it simply stores, retrieves, updates, and deletes tasks by ID. This separation allows reuse in alternative workflows (e.g., custom columns, Scrum backlogs) without modifying core logic.

Together, they enable composability: `KanbanBoard` can delegate storage responsibilities to `TaskManager` if desired, though current implementation embeds its own registry for simplicity and atomicity.

All public methods include type hints, descriptive docstrings, and explicit error handling (e.g., `ValueError` for nonexistent tasks). No global state is used — every instance is fully isolated.

## Setup & Installation

1. Ensure Python 3.8+ is installed.
2. Clone the repository:
   ```bash
   git clone https://github.com/your-org/kanbanagent.git
   cd kanbanagent
   ```
3. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # OR
   .venv\Scripts\activate  # Windows
   ```

No additional dependencies are required — the project uses only the Python standard library.

## Running Tests

Execute the full test suite using Python’s built-in `unittest` framework:

```bash
python -m unittest test_main.py -v
```

This runs all test cases defined in `TestKanbanBoard` and `TestTaskManager`, including:
- Task creation and initial column placement
- Valid and invalid status transitions
- Partial and full task updates
- Duplicate ID rejection
- Idempotent operations (e.g., moving to same column)
- Exception safety guarantees

All tests are deterministic and side-effect-free — no filesystem I/O, network calls, or randomness.

## Project Structure

```
kanbanagent/
├── kanban_board.py    # Core Kanban workflow logic
├── task_manager.py    # Generic task CRUD operations
├── test_main.py       # Unit tests for both modules
├── README.md          # This file
└── .gitignore         # Standard Python ignore patterns
```

## License

MIT License — see [LICENSE](LICENSE) for full terms.