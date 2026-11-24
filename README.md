# AI-Assisted Project Starter

A lightweight, stack-agnostic starter workspace configured for universal AI coding assistants (**Claude Code**, **Antigravity**, **GitHub Copilot**, and **Cursor**).

---

## Architecture Overview

This template implements a **Single Source of Truth (SSOT)** model to coordinate multiple AI tools without duplicating configuration or instruction files.

```
.
├── AGENTS.md                  # Canonical rules and architecture (SSOT)
├── CLAUDE.md                  # Claude Code adapter -> AGENTS.md
├── GEMINI.md                  # Antigravity adapter -> AGENTS.md
├── .cursorrules               # Cursor adapter -> AGENTS.md
├── .cursorignore              # Cursor ignore adapter -> .agents/aiignore
├── .claudeignore              # Claude Code ignore adapter -> .agents/aiignore
├── .editorconfig              # Cross-editor formatting standards (SSOT)
├── .github/
│   ├── copilot-instructions.md# GitHub Copilot adapter -> AGENTS.md
│   └── workflows/             # CI automated validation
├── .agents/                   # Universal agent resources directory
│   ├── aiignore               # Universal AI assistant ignore rules (SSOT)
│   ├── agents/                # Custom agent personas
│   ├── hooks/                 # Lifecycle hooks
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

## Quick Start

1. **Define Your Stack & Context**:
   Open [`AGENTS.md`](./AGENTS.md) and fill in:
   - `## 1. Project Context`: Project name, tech stack, and goals.
   - `## 2. Standards and Coding Conventions`: Architecture, conventions, and style rules for your chosen technologies.
   - `## 3. Development Workflow and Tooling`: Build, lint, format, and test commands.

2. **Work with Any Assistant**:
   All adapters (`CLAUDE.md`, `GEMINI.md`, `.cursorrules`, `copilot-instructions.md`) automatically reference [`AGENTS.md`](./AGENTS.md). You only ever need to edit `AGENTS.md` to update instructions for all assistants.

---

## Managing Agent Resources

The bundled utility `.agents/scripts/agents-manager.py` manages the entire lifecycle of agent resources across all 9 types (skills, agents, instructions, plugins, prompts, schemas, scripts, hooks, and MCP servers).

> 📖 **Detailed Guide:** See the **[Agent Resources Lifecycle & Provenance Guide](./docs/agent-resources-lifecycle.md)** for architecture, schema specifications, and workflow examples.

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
