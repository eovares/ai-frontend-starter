---
name: manage-agent-resources
description: >-
  Universal toolkit to discover, create, verify, update, analyze, import, export,
  manage agent resources and configure MCP servers inside .agents/ (skills, agents,
  instructions, plugins, prompts, scripts, hooks, mcp). Supports cross-agent compatibility
  (Claude Code, Antigravity, Copilot, Cursor).
---

# Manage Agent Resources Skill

Comprehensive toolkit for the full lifecycle of agent resources and Model Context Protocol (MCP) integrations in the canonical `.agents/` directory.

Use this skill when you need to:
- **Discover & Suggest**: Scan remote repositories, detect potential agent assets, and get intelligent import recommendations based on token footprint and structure.
- **Configure MCP**: Configure, template, and synchronize Model Context Protocol (MCP) servers across Claude Code, Cursor, and VS Code.
- **Create (Scaffold)**: Scaffold standardized skills, agent personas, prompts, instructions, hooks, plugins, or scripts.
- **Verify (Audit & Lint)**: Audit registry integrity, frontmatter compliance, executable permissions, and detect leaked paths.
- **Update (Update & Sync)**: Refresh remote resources from upstream Git repos and synchronize untracked files into `registry.json`.
- **Analyze (Analyze & Audit)**: Deep-inspect context token consumption, file complexity, and cross-agent compatibility.
- **Import (Import)**: Import skills and tools from GitHub, Git URLs, or subpaths with automated model lock neutralization.
- **Export (Export & Package)**: Bundle individual resources or the entire `.agents/` library into portable `.tar.gz` or `.zip` archives.
- **Manage (Maintain)**: Inspect metadata cards (`info`), list categorized assets, neutralize model locks, or remove resources cleanly.

---

## 1. Quick Reference Commands

All operations are executed via the bundled Python utility:

```bash
# 🧭 DISCOVER & SUGGEST (Scan remote repository and get best import recommendations)
python3 .agents/scripts/agents-manager.py discover <github_url> [--import-recommended]

# 🔌 MCP (Model Context Protocol Server Management)
python3 .agents/scripts/agents-manager.py mcp list
python3 .agents/scripts/agents-manager.py mcp templates
python3 .agents/scripts/agents-manager.py mcp add-template <preset_name>
python3 .agents/scripts/agents-manager.py mcp add <name> --cmd <executable> [--args ...] [--env KEY=VAL]
python3 .agents/scripts/agents-manager.py mcp sync
python3 .agents/scripts/agents-manager.py mcp remove <name>

# 🛠️ CREATE (Scaffold new user resource)
python3 .agents/scripts/agents-manager.py create <type> <name> [--author "<name>"] [--description "..."]

# 🔍 VERIFY (Audit and verify workspace integrity)
python3 .agents/scripts/agents-manager.py verify [--fix]

# 📊 ANALYZE (Token cost, line count, and cross-agent compatibility matrix)
python3 .agents/scripts/agents-manager.py analyze [name]

# 🌐 IMPORT (Import from GitHub with neutralization prompt)
python3 .agents/scripts/agents-manager.py add <type> <name> --url <github_url> [--subpath <path>] [--ref <branch>]

# 📦 EXPORT (Package resource or library to portable bundle)
python3 .agents/scripts/agents-manager.py export [name] [--output <path>] [--format tar.gz|zip]

# 🔄 UPDATE (Update remote resources from GitHub)
python3 .agents/scripts/agents-manager.py update [name]

# 🗃️ SYNC (Register existing untracked files into registry)
python3 .agents/scripts/agents-manager.py sync

# ℹ️ INFO (Detailed resource metadata card)
python3 .agents/scripts/agents-manager.py info <name>

# 📋 LIST (Categorized view: remote vs user-created)
python3 .agents/scripts/agents-manager.py list

# 🛡️ NEUTRALIZE (Audit & neutralize model/vendor locks)
python3 .agents/scripts/agents-manager.py neutralize <name>

# 🗑️ REMOVE (Cleanly delete files and deregister)
python3 .agents/scripts/agents-manager.py remove <name>
```

Supported `<type>` values: `skill`, `agent`, `instruction`, `plugin`, `prompt`, `script`, `hook`.

---

## 2. Resource Hierarchy & Canonical Paths

Every resource must strictly reside in `.agents/`:

| Resource Type | Path | Invariants & Rules |
| :--- | :--- | :--- |
| **Skill** | `.agents/skills/<name>/SKILL.md` | Directory containing `SKILL.md` with valid YAML frontmatter (`name`, `description`). |
| **Agent** | `.agents/agents/<name>.md` | Markdown document defining persona, purpose, and operational responsibilities. |
| **Instruction** | `.agents/instructions/<topic>.md` | Modular guideline referenced by `AGENTS.md`. |
| **Plugin** | `.agents/plugins/<name>/` | Directory containing a valid `plugin.json` manifest. |
| **Prompt** | `.agents/prompts/<name>.md` | Markdown template with clear input parameters. |
| **Script** | `.agents/scripts/<name>` | Executable helper script (`chmod +x`). |
| **Hook** | `.agents/hooks/<name>` | Lifecycle trigger executable (`chmod +x`). |
| **MCP Config** | `.agents/mcp.json` | Model Context Protocol servers synced to `.vscode/mcp.json` & `.mcp.json`. |
| **Registry** | `.agents/registry.json` | Provenance and source tracking registry. |

---

## 3. Operational Roles & Workflows

### A. Repository Discovery & Suggestion Engine
When a user provides a GitHub or Git repository, scan it to suggest the highest-value assets:
```bash
python3 .agents/scripts/agents-manager.py discover https://github.com/org/repo
```
The manager:
1. Performs a shallow clone (`--depth 1`) in a temporary sandbox.
2. Identifies all skills, agents, instructions, prompts, plugins, scripts, and MCP configs.
3. Computes estimated token consumption and tags recommendations:
   - `⭐ Highly Recommended`: Lightweight (< 4,000 tokens) with clear descriptions.
   - `📦 Standard`: Moderate size (4,000–15,000 tokens).
   - `⚠️ Heavy`: Large context footprint (> 15,000 tokens).
4. Presents an interactive menu to import chosen or recommended resources seamlessly.

### B. MCP Server Management & Cross-Assistant Sync
Manage Model Context Protocol servers from a central, canonical configuration:
```bash
# Explore available presets (filesystem, fetch, sqlite, github, memory, brave-search):
python3 .agents/scripts/agents-manager.py mcp templates

# Install a preset with one command:
python3 .agents/scripts/agents-manager.py mcp add-template filesystem

# Add custom MCP server:
python3 .agents/scripts/agents-manager.py mcp add my-api --cmd npx --args -y my-mcp-package --env API_KEY=xyz

# Synchronize across all assistants:
python3 .agents/scripts/agents-manager.py mcp sync
```
`mcp sync` mirrors `.agents/mcp.json` into:
- `.vscode/mcp.json` (for VS Code and GitHub Copilot)
- `.mcp.json` in root (for Cursor and Claude Code)

### C. Creator / Scaffolder Tool
Bootstrap a new resource with standardized boilerplate:
```bash
python3 .agents/scripts/agents-manager.py create skill my-workflow --description "Workflow runbook"
```

### D. Verifier / Linter Tool
Audit workspace health and canonical standards:
```bash
python3 .agents/scripts/agents-manager.py verify [--fix]
```

### E. Analyzer / Token Auditor Tool
Inspect context token consumption and assistant compatibility:
```bash
python3 .agents/scripts/agents-manager.py analyze [name]
```

### F. Exporter / Packager Tool
Package resources into portable archives:
```bash
python3 .agents/scripts/agents-manager.py export my-skill --format tar.gz
```
