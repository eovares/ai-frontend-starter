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
├── .github/
│   └── copilot-instructions.md# GitHub Copilot adapter -> AGENTS.md
├── .agents/                   # Universal agent resources directory
│   ├── agents/                # Custom agent personas
│   ├── hooks/                 # Lifecycle hooks
│   ├── instructions/          # Extended modular instructions
│   ├── plugins/               # Namespaced plugin bundles
│   ├── prompts/               # Reusable prompt templates
│   ├── scripts/               # Automation scripts (agents-manager.py)
│   ├── skills/                # Reusable procedural skills
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

The bundled utility `.agents/scripts/agents-manager.py` manages the entire lifecycle of agent resources:

```bash
# 🧭 Discover: Scan a remote repo and get intelligent import recommendations
python3 .agents/scripts/agents-manager.py discover <github-url> [--import-recommended]

# 🔌 MCP: Configure & sync Model Context Protocol servers across assistants
python3 .agents/scripts/agents-manager.py mcp templates
python3 .agents/scripts/agents-manager.py mcp add-template filesystem
python3 .agents/scripts/agents-manager.py mcp sync

# 🛠️ Creator: Scaffold standardized user resource
python3 .agents/scripts/agents-manager.py create <type> <name>

# 🔍 Verifier: Audit integrity, frontmatter, permissions, and structure
python3 .agents/scripts/agents-manager.py verify [--fix]

# 📊 Analyzer: Token consumption and cross-agent compatibility matrix
python3 .agents/scripts/agents-manager.py analyze [name]

# 🌐 Importer: Import external skills from GitHub with model lock neutralization
python3 .agents/scripts/agents-manager.py add <type> <name> --url <github-url>

# 📦 Exporter: Package resource(s) into portable .tar.gz or .zip bundles
python3 .agents/scripts/agents-manager.py export [name] [--format tar.gz|zip]

# 🔄 Updater: Update tracked remote resources from GitHub
python3 .agents/scripts/agents-manager.py update [name]

# 🗃️ Syncer: Index untracked workspace files into registry.json
python3 .agents/scripts/agents-manager.py sync

# ℹ️ Inspector: Display detailed metadata card of a resource
python3 .agents/scripts/agents-manager.py info <name>
```

---

## License

This project is licensed under the terms described in the [LICENSE](./LICENSE) file.
