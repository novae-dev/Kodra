# Kodra

> A provider-agnostic AI coding environment built to help developers understand, modify, and work with real codebases from one workspace.

Kodra is an early-stage developer tool that combines a desktop-style code workspace with an AI engineering agent. The goal is simple: **open a project, understand it, talk to Kodra, make a change, review exactly what changed, and apply it when ready.**

Kodra is being built as a modular system so the AI provider, project intelligence layer, and developer experience can evolve independently.

## Status

**Active development — MVP**

The current build includes:

- React + TypeScript desktop-style IDE interface
- Project explorer and code editor shell
- Integrated terminal-style panel
- Kodra AI chat interface
- Python/FastAPI agent backend
- Frontend ↔ backend communication
- Project file discovery endpoint
- Health/status endpoint

The next major milestone is real project intelligence: reading source files, understanding their relationships, generating changes, displaying diffs, and letting the developer accept or reject those changes.

## Why Kodra?

Modern coding assistants are increasingly capable, but the development experience can still feel fragmented between an editor, terminal, chat window, Git, documentation, and AI tools.

Kodra is exploring a different workflow:

```text
Project
   ↓
Understand
   ↓
Ask
   ↓
Plan
   ↓
Change
   ↓
Review diff
   ↓
Apply
   ↓
Test
```

The developer remains in control of the changes rather than blindly accepting generated code.

## Core Goals

- **Project-aware AI** — understand the actual repository instead of answering from isolated snippets.
- **Provider-agnostic architecture** — avoid tying Kodra's core workflow to a single AI provider.
- **Reviewable changes** — show what the agent wants to modify before applying it.
- **Controlled execution** — keep potentially destructive operations behind explicit developer actions.
- **Developer-first workflow** — combine project navigation, code, AI, terminal output, and future Git tooling in one environment.
- **Extensible architecture** — make room for planners, memory, multi-agent workflows, testing, and additional developer tools.

## Architecture

```text
Kodra/
├── desktop/                 # React + TypeScript frontend
│   ├── src/
│   │   ├── App.tsx
│   │   ├── App.css
│   │   └── index.css
│   ├── package.json
│   └── vite.config.ts
│
├── agent/                   # Python AI/backend service
│   ├── main.py
│   └── .venv/               # Local only; not committed
│
├── packages/                # Planned shared packages
└── docs/                    # Planned technical documentation
```

### Request flow

```text
Kodra Desktop
     │
     │ HTTP
     ▼
FastAPI Agent
     │
     ├── Project inspection
     ├── AI orchestration (planned)
     ├── File operations (planned)
     ├── Diff generation (planned)
     └── Tool execution (planned)
```

## Tech Stack

### Frontend

- React
- TypeScript
- Vite
- Lucide React
- CSS

### Agent / Backend

- Python
- FastAPI
- Uvicorn

### Planned infrastructure

- AI provider adapters
- Project indexing/context engine
- File read/write layer
- Diff engine
- Git integration
- Testing and diagnostics
- Persistent project memory
- Multi-agent orchestration

## Current API

The FastAPI agent currently exposes a small foundation API.

### `GET /`

Returns basic agent information.

### `GET /health`

Used to verify that the agent is running.

Example response:

```json
{
  "status": "healthy"
}
```

### `GET /project`

Scans the Kodra project and returns discovered files while ignoring generated/dependency directories such as `node_modules`, `.git`, `.venv`, `dist`, and `__pycache__`.

### `POST /chat`

Accepts a chat message from the desktop application and returns a response from the connected Kodra agent.

Example request:

```json
{
  "message": "Explain this project"
}
```

## Getting Started

### Requirements

- Node.js 20+
- npm
- Python 3.11+
- Git

### 1. Clone the repository

```bash
git clone https://github.com/novae-dev/Kodra.git
cd Kodra
```

### 2. Start the frontend

```powershell
cd desktop
npm install
npm run dev
```

The Vite development server runs at:

```text
http://localhost:5173
```

### 3. Create the Python environment

From the repository root:

```powershell
cd agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install fastapi uvicorn
```

If PowerShell execution policy prevents activation, run the environment's Python directly or allow the policy for the current process.

### 4. Start the agent

From `agent/`:

```powershell
python -m uvicorn main:app --reload --port 8000
```

The agent will be available at:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

## Development Workflow

Kodra is being developed in small but meaningful milestones.

### Phase 1 — Foundation

- [x] Repository setup
- [x] React + TypeScript desktop shell
- [x] IDE-style layout
- [x] Explorer panel
- [x] Editor panel
- [x] Terminal panel
- [x] AI chat panel
- [x] FastAPI agent
- [x] Frontend/backend connection

### Phase 2 — Project Intelligence

- [x] Discover project files
- [ ] Open real files
- [ ] Read source contents
- [ ] Build project context
- [ ] Detect framework and language
- [ ] Ignore generated/vendor files intelligently
- [ ] Project indexing

### Phase 3 — AI Engineer

- [ ] Real AI provider adapter
- [ ] Project-aware chat
- [ ] Planning step
- [ ] File modification proposals
- [ ] Unified diffs
- [ ] Accept/reject changes
- [ ] Multi-file edits
- [ ] Error-aware iteration

### Phase 4 — Developer Tools

- [ ] Real terminal integration
- [ ] Git status and diff
- [ ] Branch management
- [ ] Test runner
- [ ] Build/error diagnostics
- [ ] Logs
- [ ] Environment management

### Phase 5 — Intelligence Layer

- [ ] Persistent project memory
- [ ] Agent memory
- [ ] Task planning
- [ ] Specialized sub-agents
- [ ] Context optimization
- [ ] Provider routing

## Design Principles

### Developer remains in control

Kodra should explain and preview meaningful changes before modifying a project.

### Inspect before changing

The agent should understand relevant project context before attempting a modification.

### Small, verifiable operations

Important operations should be observable, reviewable, and recoverable.

### Provider independence

Kodra's application architecture should not assume that one model or provider will always be the right choice.

### Local-first project awareness

The coding agent needs access to the actual project structure and source files to provide useful engineering assistance.

## Security Direction

Kodra is intentionally **not** being designed around an unrestricted AI-controlled shell.

Future tool execution should use explicit capabilities and boundaries so that actions such as file writes, command execution, dependency installation, and Git operations can be controlled and reviewed.

This is especially important because an AI coding agent can affect the developer's source code and local environment.

## Roadmap

The long-term vision is to turn Kodra into an AI-native development environment with:

- Deep codebase understanding
- Natural-language development workflows
- Reviewable multi-file edits
- Automated debugging loops
- Test and build integration
- Git-aware development
- Persistent project memory
- Multiple AI providers
- Specialized engineering agents
- Developer-controlled automation

The project is intentionally being built incrementally rather than attempting to implement the entire vision at once.

## Contributing

Kodra is currently a personal project under active development. The architecture and APIs may change significantly while the MVP is being built.

If you want to experiment with the project:

1. Fork the repository.
2. Create a feature branch.
3. Make a focused change.
4. Run the frontend build and relevant backend checks.
5. Open a pull request with a clear description of the change.

## License

License information will be added as the project approaches its first public release.

## Author

**NOVA — Abdul Mateen**

Full-stack developer and computer systems networking student building Kodra as an exploration of AI-native developer tooling.

GitHub: [@novae-dev](https://github.com/novae-dev)
