# CLAUDE.md — Superpowers Repository Guide

This file documents the codebase structure, development workflows, and conventions for AI assistants working in this repository.

---

## Project Overview

**Superpowers** is a skills library and plugin system that enhances AI agent behavior by injecting documented best practices and workflows into system prompts. It works with:

- **Claude Code** (primary platform, via `.claude-plugin/`)
- **OpenCode.ai** (via `.opencode/`)
- **OpenAI Codex** (via `.codex/`)

**Version:** 4.1.1 | **License:** MIT | **Upstream:** https://github.com/obra/superpowers

Skills are Markdown documents (not code) that change how AI agents behave. They are loaded into system prompts through plugin hooks and a session-start hook.

---

## Repository Structure

```
superpowers/
├── .claude-plugin/          # Claude Code plugin metadata
│   ├── plugin.json          # Name, version, author, keywords
│   └── marketplace.json     # Local marketplace config
├── .codex/                  # OpenAI Codex integration
├── .opencode/               # OpenCode.ai plugin
│   └── plugins/superpowers.js  # Plugin loader (Node.js)
├── agents/                  # Agent templates (e.g., code-reviewer.md)
├── commands/                # Slash commands (/brainstorm, /execute-plan, /write-plan)
├── docs/                    # Installation guides, design docs, testing docs
│   ├── testing.md
│   ├── DOCKER.md
│   └── plans/               # Architecture decision records
├── examples/                # Working example projects
├── hooks/
│   ├── hooks.json           # SessionStart hook config
│   └── session-start.sh     # Injects using-superpowers skill on startup
├── lib/
│   └── skills-core.js       # YAML frontmatter parsing & skill discovery
├── skills/                  # 14 core skills (main content)
├── tests/                   # Integration tests (shell-based)
│   ├── claude-code/
│   ├── explicit-skill-requests/
│   ├── opencode/
│   ├── skill-triggering/
│   └── subagent-driven-dev/
├── .env.example             # LLM API key template
├── docker-compose.yml
├── Dockerfile               # node:20-slim + Python 3 + Git
├── README.md
└── RELEASE-NOTES.md
```

---

## Skills — The Core Content

Skills live in `skills/<skill-name>/SKILL.md`. There are 14 skills:

| Skill | Purpose |
|---|---|
| `brainstorming` | Explore requirements before implementation |
| `dispatching-parallel-agents` | Run subagents concurrently |
| `executing-plans` | Execute plans with review checkpoints |
| `finishing-a-development-branch` | Complete git workflows |
| `receiving-code-review` | Process review feedback |
| `requesting-code-review` | Ask for reviews properly |
| `subagent-driven-development` | Multi-agent development coordination |
| `systematic-debugging` | Root cause investigation before fixes |
| `test-driven-development` | Write tests first |
| `using-git-worktrees` | Parallel branch management |
| `using-superpowers` | How to invoke and use skills |
| `verification-before-completion` | Pre-completion checklist |
| `writing-plans` | Create detailed implementation plans |
| `writing-skills` | Author new skills (meta-skill) |

### Skill File Structure

```
skills/skill-name/
├── SKILL.md           # Required — main skill document
└── supporting-files   # Optional: .md, .ts, .sh, .js examples
```

### SKILL.md Format

Every `SKILL.md` must have a YAML frontmatter header:

```yaml
---
name: skill-name
description: Use when [triggering condition] — [what it does]
---
```

Followed by these sections (in order):
1. **Overview** — Core principle (1–3 sentences)
2. **When to Use** — Triggering conditions
3. **Core Pattern** — Before/after comparison or step list
4. **Quick Reference** — Scanning table (optional but preferred)
5. **Implementation** — Detailed steps (inline or linked)
6. **Common Mistakes** — Pitfalls and corrections
7. **Red Flags** — When to stop and reconsider

**Descriptions must start with "Use when..."** — this is how Claude Code discovers which skill to invoke. Descriptions are search-indexed, so include relevant keywords, error messages, and symptoms.

**Target length:** 500–2000 words per skill. Frequently loaded skills should be <150 words.

---

## Development Conventions

### Naming

- Skill directories: `kebab-case` (e.g., `test-driven-development`)
- Skill files: `SKILL.md` (uppercase)
- Supporting files: lowercase with hyphens
- Cross-references: `superpowers:skill-name` format

### TDD Philosophy

This project applies TDD to both code *and* documentation:

> **NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST**
> **NO SKILL WITHOUT A FAILING TEST FIRST**

When adding a new skill, write a test prompt first (in `tests/explicit-skill-requests/prompts/` or `tests/skill-triggering/prompts/`) that verifies the agent uses the skill correctly.

### Flowcharts

Use GraphViz `.dot` format (see `skills/writing-skills/graphviz-conventions.dot`) only for:
- Non-obvious decision flows
- Process loops

Never use flowcharts for linear instructions — use numbered lists instead.

### Claude Search Optimization (CSO)

- Frontmatter `description` must be scan-optimized (symptoms/conditions first)
- Keep skill names in `kebab-case` — they become search tokens
- Token budget: frequently loaded skills target <150 words total
- Reference other skills by name, don't duplicate content

---

## Running Tests

Tests are shell-script-based integration tests. No `npm test` or `make test` command exists.

### Prerequisites

- `claude` CLI installed and authenticated
- Superpowers plugin registered in `~/.claude/settings.json` with local dev marketplace enabled

### Test Suites

```bash
# OpenCode plugin unit tests (fastest)
cd tests/opencode
./run-tests.sh

# Explicit skill invocation tests
cd tests/explicit-skill-requests
./run-all.sh

# Skill auto-triggering tests
cd tests/skill-triggering
./run-all.sh

# Claude Code integration tests (slow, requires live API)
cd tests/claude-code
./test-subagent-driven-development-integration.sh

# Full subagent-driven-dev integration (10–30 min)
cd tests/subagent-driven-dev
./run-test.sh
```

### Token Analysis

```bash
python3 tests/claude-code/analyze-token-usage.py
```

---

## Running the Project (Docker)

```bash
# Build and start container
docker compose build
docker compose up -d

# Open shell in container
docker compose exec superpowers bash
```

The Dockerfile uses `node:20-slim` + Python 3 + Git. No `npm install` step (no `package.json`).

---

## Plugin Architecture

### Claude Code Plugin

Registered via `.claude-plugin/plugin.json`. On session start, `hooks/session-start.sh` runs and injects the `using-superpowers` skill into the session context as a JSON hook payload.

```bash
hooks/session-start.sh   # Reads using-superpowers/SKILL.md, outputs JSON
```

### OpenCode Plugin

`/.opencode/plugins/superpowers.js` is a Node.js plugin that:
1. Discovers skills via `lib/skills-core.js`
2. Injects skill context into the system prompt via a transformation hook

### Codex Integration

`.codex/superpowers-bootstrap.md` and the `superpowers-codex` CLI tool provide a simpler context injection for Codex environments.

### Shared Library

`lib/skills-core.js` handles:
- YAML frontmatter extraction from `SKILL.md` files
- Recursive skill directory discovery
- Metadata collection (name, description, source type)

---

## Environment Configuration

Copy `.env.example` to `.env` and fill in your API keys:

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
# etc.
```

`.env` and `.env.local` are gitignored.

---

## Git Workflow

This repo follows standard GitHub flow:
- Default branch: `main`
- Feature branches: `kebab-case` descriptive names
- Commits: imperative mood, describe *what* and *why*

`.worktrees/`, `.private-journal/`, and `.claude/` are gitignored — use `.worktrees/` for `git worktree` parallel development (see `skills/using-git-worktrees/`).

---

## Adding a New Skill

1. Create `skills/<new-skill-name>/SKILL.md` with valid YAML frontmatter
2. Write a test prompt in `tests/explicit-skill-requests/prompts/` or `tests/skill-triggering/prompts/`
3. Verify the skill triggers correctly with `./run-test.sh`
4. Optionally add supporting files (examples, scripts, reference docs) in the same directory
5. Update `RELEASE-NOTES.md` with the change

Refer to `skills/writing-skills/SKILL.md` for the full skill authoring methodology.

---

## Key Files Quick Reference

| File | Purpose |
|---|---|
| `skills/using-superpowers/SKILL.md` | Entry point — how agents use this library |
| `skills/writing-skills/SKILL.md` | How to author new skills |
| `lib/skills-core.js` | Skill discovery & YAML parsing |
| `hooks/session-start.sh` | Claude Code session initialization |
| `.opencode/plugins/superpowers.js` | OpenCode.ai plugin entry |
| `hooks/hooks.json` | Hook event bindings |
| `.claude-plugin/plugin.json` | Plugin metadata |
| `docs/testing.md` | Full testing guide |
| `RELEASE-NOTES.md` | Changelog (semantic versioning) |
