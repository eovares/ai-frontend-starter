# AI-Assisted Project Starter

A lightweight, stack-agnostic starter workspace architected for universal AI coding assistants (**Antigravity**, **Claude Code**, **Cursor**, **GitHub Copilot**, **Windsurf**, **Codex / OpenAI**, and **Gemini CLI**) using **multi-configuration patterns** and a canonical **Single Source of Truth (SSOT)**.

---

## Architecture Overview

This template implements a **Single Source of Truth (SSOT)** model to coordinate multiple AI tools without duplicating configuration, prompts, or instruction files.

```text
.
├── AGENTS.md                  # Canonical rules and architecture (SSOT)
├── CLAUDE.md                  # Claude Code adapter -> AGENTS.md
├── GEMINI.md                  # Antigravity & Gemini CLI adapter -> AGENTS.md
├── .cursorrules               # Cursor adapter -> AGENTS.md
├── .windsurfrules             # Windsurf (Cascade) adapter -> AGENTS.md
├── .cursorignore              # Cursor ignore adapter -> .agents/aiignore
├── .claudeignore              # Claude Code ignore adapter -> .agents/aiignore
├── .editorconfig              # Cross-editor formatting standards (SSOT)
├── .github/
│   ├── copilot-instructions.md# GitHub Copilot adapter -> AGENTS.md
│   └── workflows/             # CI automated validation
├── .agents/                   # Universal agent resources directory
│   ├── aiignore               # Universal AI assistant ignore rules (SSOT)
│   ├── agents/                # Custom agent personas and subagents
│   ├── hooks/                 # Lifecycle execution hooks
│   ├── instructions/          # Extended modular instructions
│   ├── plugins/               # Namespaced plugin bundles
│   ├── prompts/               # Reusable prompt templates
│   ├── schemas/               # JSON Schemas for registry and MCP validation
│   ├── scripts/               # Automation scripts (agents-manager.py)
│   ├── skills/                # Reusable procedural skills
│   ├── mcp.json               # Canonical MCP server definitions
│   └── registry.json          # Source & provenance registry
└── docs/                      # Architectural strategy and guides
```

---

## Multi-Configuration Architecture

This workspace orchestrates multiple AI assistants, toolsets, and environments through standardized **Multi-Configuration Patterns**:

```text
                               ┌────────────────────────────────────────────────────────┐
                               │               Universal SSOT: AGENTS.md                │
                               │               (.agents/ Architecture)                  │
                               └───────────────────────────┬────────────────────────────┘
                                                           │
          ┌─────────────────────┬──────────────────────────┼──────────────────────────┬─────────────────────┐
          ▼                     ▼                          ▼                          ▼                     ▼
┌──────────────────┐  ┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐  ┌──────────────────┐
│   Antigravity /  │  │   Claude Code    │       │      Cursor      │       │     Windsurf     │  │  GitHub Copilot  │
│    Gemini CLI    │  │   (CLAUDE.md)    │       │  (.cursorrules)  │       │ (.windsurfrules) │  │ (.github/copilot)│
│   (GEMINI.md)    │  └──────────────────┘       └──────────────────┘       └──────────────────┘  └──────────────────┘
└──────────────────┘            ▲                          ▲                          ▲
                                │                          │                          │
                                └──────────────────────────┴──────────────────────────┘
                                                           │
                                ┌──────────────────────────┴──────────────────────────┐
                                │          Canonical MCP: .agents/mcp.json            │
                                └──────────────────────────┬──────────────────────────┘
                                                           │ (python3 agents-manager.py mcp sync)
                                ┌──────────────────────────┴──────────────────────────┐
                                ▼                                                     ▼
                     ┌─────────────────────┐                               ┌─────────────────────┐
                     │  .vscode/mcp.json   │                               │      .mcp.json      │
                     │  (VS Code / Copilot)│                               │    (Claude Code)    │
                     └─────────────────────┘                               └─────────────────────┘
```

### 1. Cross-Assistant Adapter Matrix (SSOT)
Instead of maintaining fragmented vendor rules (`.cursor/`, `.claude/`, `.gemini/`), all assistants share a single source of truth:

| AI Coding Assistant | Configuration Entrypoint | Pattern | Action Required |
| :--- | :--- | :--- | :--- |
| **Antigravity** | [`GEMINI.md`](./GEMINI.md) | Lightweight Shim | Auto-loads [`AGENTS.md`](./AGENTS.md) |
| **Claude Code** | [`CLAUDE.md`](./CLAUDE.md) | Lightweight Shim | Auto-loads [`AGENTS.md`](./AGENTS.md) |
| **Cursor** | [`.cursorrules`](./.cursorrules) | Lightweight Shim | Auto-loads [`AGENTS.md`](./AGENTS.md) |
| **GitHub Copilot** | [`.github/copilot-instructions.md`](./.github/copilot-instructions.md) | Lightweight Shim | Auto-loads [`AGENTS.md`](./AGENTS.md) |
| **Windsurf** (Cascade) | [`.windsurfrules`](./.windsurfrules) | Lightweight Shim | Auto-loads [`AGENTS.md`](./AGENTS.md) |
| **Codex / OpenAI** | [`AGENTS.md`](./AGENTS.md) | Native Standard | Direct consumption |
| **Gemini CLI** | [`GEMINI.md`](./GEMINI.md) | Lightweight Shim | Auto-loads [`AGENTS.md`](./AGENTS.md) |

### 2. Autonomous MCP Tool Synchronization
Model Context Protocol (MCP) servers are configured once in [`.agents/mcp.json`](file:///Users/eovares/code/ai-frontend-starter/.agents/mcp.json). Running the syncer mirrors this configuration in lockstep to all client-specific adapters:
* **VS Code & GitHub Copilot**: Synchronized into `.vscode/mcp.json`.
* **Claude Code & Cursor**: Synchronized into `.mcp.json`.

```bash
python3 .agents/scripts/agents-manager.py mcp sync
```

### 3. Unified AI Context Exclusions (`aiignore`)
Security credentials, build outputs, and large data dumps are excluded across all tools simultaneously:
* **Canonical SSOT**: [`.agents/aiignore`](file:///Users/eovares/code/ai-frontend-starter/.agents/aiignore)
* **Client Adapters**: Auto-synced to `.cursorignore` and `.claudeignore` via:
```bash
python3 .agents/scripts/agents-manager.py ignore sync
```

### 4. Lightweight Workspace Profile Isolation
Prevent extension bloat and CPU/RAM overhead by isolating project-specific extensions into dedicated VS Code profiles.
* 📖 See **[VS Code Profiles Setup Guide](./docs/vscode-profiles.md)** for step-by-step instructions.

---

## Quick Start

1. **Define Your Stack & Context**:
   Open [`AGENTS.md`](./AGENTS.md) and fill in:
   - `## 1. Project Context`: Project name, tech stack, and goals.
   - `## 2. Standards and Coding Conventions`: Architecture, conventions, and style rules for your chosen technologies.
   - `## 3. Development Workflow and Tooling`: Build, lint, format, and test commands.

2. **Work with Any Assistant**:
   All adapters (`CLAUDE.md`, `GEMINI.md`, `.cursorrules`, `.windsurfrules`, `copilot-instructions.md`) automatically reference [`AGENTS.md`](./AGENTS.md). You only ever need to edit `AGENTS.md` to update instructions for all assistants.

---

## Managing Agent Resources

The bundled utility `.agents/scripts/agents-manager.py` manages the entire lifecycle of agent resources across all 9 types (skills, agents, instructions, plugins, prompts, schemas, scripts, hooks, and MCP servers).

> 📖 **Detailed Lifecycle Guide:** See the **[Agent Resources Lifecycle & Provenance Guide](./docs/agent-resources-lifecycle.md)** for architecture, schema specifications, and workflow examples.

```bash
# 🚀 Init: Initialize workspace context and project goals in AGENTS.md
python3 .agents/scripts/agents-manager.py init [--name <name>] [--stack <stack>]

# 🩺 Doctor: Deep diagnostic health check on environment, adapters & security
python3 .agents/scripts/agents-manager.py doctor

# 🛡️ Ignore: Synchronize .agents/aiignore SSOT to .cursorignore & .claudeignore
python3 .agents/scripts/agents-manager.py ignore sync

# 🧭 Discover: Scan a remote repo and get intelligent import recommendations
python3 .agents/scripts/agents-manager.py discover <github-url> [--import-recommended]

# 🔌 MCP: Configure & sync Model Context Protocol servers across assistants
python3 .agents/scripts/agents-manager.py mcp templates
python3 .agents/scripts/agents-manager.py mcp add-template filesystem
python3 .agents/scripts/agents-manager.py mcp sync

# 🛠️ Creator: Scaffold standardized user resource (skill, agent, hook, instruction, plugin, prompt, schema, script, mcp)
python3 .agents/scripts/agents-manager.py create <type> <name>

# 🔍 Verifier: Audit integrity, frontmatter, permissions, and structure
python3 .agents/scripts/agents-manager.py verify [--fix]

# 📊 Analyzer: Token consumption and cross-agent compatibility matrix
python3 .agents/scripts/agents-manager.py analyze [name]

# 🌐 Importer: Import external resources from GitHub with provenance tracking & neutralization
python3 .agents/scripts/agents-manager.py add <type> <name> --url <github-url>

# 📦 Exporter: Package resource(s) into portable .tar.gz or .zip bundles
python3 .agents/scripts/agents-manager.py export [name] [--format tar.gz|zip]

# 🔄 Updater: Update tracked remote resources from GitHub (skills, agents, hooks, mcp, etc.)
python3 .agents/scripts/agents-manager.py update [name]

# 🗃️ Syncer: Index untracked workspace files into registry.json
python3 .agents/scripts/agents-manager.py sync

# ℹ️ Inspector: Display detailed metadata card of a resource
python3 .agents/scripts/agents-manager.py info <name>
```

---

## License

This project is licensed under the terms described in the [LICENSE](./LICENSE) file.
