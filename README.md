# LangGraph Startup Builder — 3 AI Employees in Multi-Turn Conversation

A LangGraph workflow where **3 specialized AI employees debate each other** across 3 turns to validate, build, and launch a satellite imagery startup — then produce a concrete action plan with task ownership.

## The Team

| Employee | Role | Skill |
|----------|------|-------|
| 🔴 **Startup Validator** | Ruthless CSO | Stress-tests ideas, forces Lean Canvas, demands evidence |
| 🔵 **Senior Engineer** | Elite CTO | Scopes simplest MVP, picks tech stack, refuses over-engineering |
| 🟢 **Growth Marketer** | Viral CMO | Customer-focused messaging, StoryBrand framework, no jargon |

## Multi-Turn Conversation Flow

```
        ┌──────────────────────────────────────┐
        │  Turn 1: Initial Reactions            │
        │  Validator → Engineer → Marketer      │
        ├──────────────────────────────────────┤
        │  Turn 2: Debate & Refine             │
        │  Validator → Engineer → Marketer      │
        ├──────────────────────────────────────┤
        │  Turn 3: Converge & Commit           │
        │  Validator → Engineer → Marketer      │
        ├──────────────────────────────────────┤
        │  Plan Compiler → FINAL ACTION PLAN   │
        └──────────────────────────────────────┘
```

Each agent sees the **full conversation history** — they respond to each other's arguments, challenge assumptions, and refine their positions across turns.

## Project Structure

```
Langgraph_Skills/
├── skills/                      # Employee skill definitions
│   ├── __init__.py              # Exports all 3 skills
│   ├── startup_validator.py     # 🔴 CSO persona, prompt, responsibilities
│   ├── senior_engineer.py       # 🔵 CTO persona, prompt, responsibilities
│   └── growth_marketer.py       # 🟢 CMO persona, prompt, responsibilities
├── workflow/                    # LangGraph workflow
│   ├── __init__.py              # Exports graph builders
│   ├── state.py                 # StartupState TypedDict definition
│   └── graph.py                 # Nodes, edges, cyclic graph, runners
├── main.py                      # CLI entry point
├── notebook.ipynb               # Jupyter notebook with rich output
├── requirements.txt             # Python dependencies
├── .env                         # Azure OpenAI credentials (git-ignored)
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure `.env`:**
   ```
   AZURE_API_KEY=your_key
   AZURE_ENDPOINT=https://your-endpoint.openai.azure.com/
   DEPLOYMENT_NAME=gpt-4o
   API_VERSION=2025-01-01-preview
   ```

3. **Run:**
   ```bash
   python main.py                    # CLI with streaming output
   jupyter notebook notebook.ipynb   # Interactive notebook
   ```

## How It Works

- **Skills** (`skills/`): Each employee is defined as a Python dict with `name`, `emoji`, `system_prompt`, and `plan_responsibilities`. This makes it easy to add or modify employees.
- **State** (`workflow/state.py`): A shared `StartupState` carries conversation history, turn counter, and each agent's latest output.
- **Graph** (`workflow/graph.py`): A **cyclic** LangGraph `StateGraph` with conditional edges. After each full turn (all 3 agents), a router checks `turn < max_turns` — if yes, loops back; if no, routes to the plan compiler.
- **Plan Compiler**: A final node that reads all 3 agents' outputs and produces a structured action plan with tasks, owners, timelines, and priorities.

## Customization

- **Change the pitch**: Edit `SATELLITE_IMAGERY_PITCH` in `main.py` or call `run_startup_workflow("your pitch")`
- **Modify personas**: Edit the system prompts in `skills/*.py`
- **Add a 4th employee**: Create a new skill file, add a node in `graph.py`, wire it into the edges
- **Change turn count**: Pass `max_turns=N` to `run_startup_workflow()` or `stream_startup_workflow()`
