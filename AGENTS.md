# AGENTS.md

> **Single Source of Truth (SSOT)** for all AI coding assistants (**Claude Code**, **Antigravity**, **GitHub Copilot**, **Cursor**).

## 1. Project Context

- **Project**: `<project-name>` (Generic AI-Assisted Workspace)
- **Stack / Technologies**: *[To be defined based on project requirements]*
- **Goal**: Provide a clean, scalable workspace architecture configured with universal AI agent tooling, ready to integrate any technology stack.

---

## 2. Standards and Coding Conventions

> *Note: Customize and expand this section once the project stack and architecture are chosen.*

### General Architecture Principles

- **Single Responsibility**: Keep modules, functions, and components focused on a single concern.
- **Modularity & Scalability**: Organize code by domain, features, or logical boundaries.
- **Simplicity (DRY & YAGNI)**: Avoid premature abstractions; prioritize clean, readable, and self-documenting code.

### Code Quality & Best Practices

- **Reliability & Error Handling**: Implement explicit error handling, input validation, and clear contracts.
- **Maintainability**: Write descriptive names that clearly communicate intent without redundant comments.
- **Naming Conventions**: Follow idiomatic naming conventions consistent with the chosen language and ecosystem.

---

## 3. Development Workflow and Tooling

> *Note: Populate with specific build, test, lint, and formatting tools as dependencies are added.*

- **Dev / Build Command**: *[To be defined]*
- **Linter**: *[To be defined]*
- **Formatter**: *[To be defined]*
- **Testing**: *[To be defined]*

---

## 4. Universal Workspace Customization Directory (`.agents/`)

When creating, reading, or maintaining agent resources, assistants must strictly locate them within the canonical `.agents/` directory tree:

| Resource Type    | Canonical Path                         | Description                                                    |
| :--------------- | :------------------------------------- | :------------------------------------------------------------- |
| **Skills**       | `.agents/skills/<skill-name>/SKILL.md` | Multi-step procedures, runbooks, and domain workflows.         |
| **Agents**       | `.agents/agents/<agent-name>.md`       | Specialized persona and subagent role definitions.             |
| **Instructions** | `.agents/instructions/<topic>.md`      | Deep or modular guidelines that extend `AGENTS.md`.            |
| **Plugins**      | `.agents/plugins/<plugin-name>/`       | Namespaced bundles grouping skills, rules, and hooks.          |
| **Prompts**      | `.agents/prompts/<prompt-name>.md`     | Reusable prompt templates, query structures, and tasks.        |
| **Scripts**      | `.agents/scripts/<script-name>`        | Project automation and helper scripts executed by agents.      |
| **Hooks**        | `.agents/hooks/`                       | Lifecycle triggers (e.g., pre-tool/post-tool execution hooks). |
| **MCP Servers**  | `.agents/mcp.json`                     | Model Context Protocol (MCP) server definitions synced to all AI tools. |
| **Registry**     | `.agents/registry.json`                | Source registry tracking user-created items & upstream GitHub repositories. |
| **AI Exclusions**| `.agents/aiignore`                     | Universal AI assistant exclusion rules synced to `.cursorignore` & `.claudeignore`. |
| **Schemas**      | `.agents/schemas/`                     | Local JSON Schemas providing validation & autocomplete for registry & MCP. |

Assistants must never create vendor-specific folders (e.g., `.claude/skills/`, `.gemini/agents/`) in this workspace. All AI resources reside under `.agents/`.

### Resource Tracking & Provenance Registry

All agent resources must be recorded in `.agents/registry.json`:
1. **User-Created Resources (`origin: "user"`)**: Records author, creation date, target path, and description.
2. **External / GitHub Resources (`origin: "remote"`)**: Records upstream Git URL, subpath, branch/ref, commit hash, installation path, and timestamps for seamless future updates.
3. **Cross-Agent Neutrality & Mandatory User Confirmation**: Imported skills and resources must retain functionality while neutralizing hardcoded LLM model locks (`model: ...`) or vendor-specific directories (`.claude/`, `.gemini/`) to run agnostically on **Claude Code**, **Antigravity**, **GitHub Copilot**, and **Cursor**. Assistants and scripts must always prompt the user with a preview of changes to accept or decline before applying neutralization.
4. **English for All AI Artifacts**: Write all AI configurations, instructions, rules, prompts, and skills strictly in English. English produces optimal tokenization, clearer instruction following, and lower token consumption across modern LLMs.
5. **Agentic Mode MCP Synchronization**: When configuring or updating MCP tools in agentic mode, assistants must strictly treat `.agents/mcp.json` as the canonical SSOT (via `python3 .agents/scripts/agents-manager.py mcp ...`) and ensure adapters (`.vscode/mcp.json` and `.mcp.json`) are automatically kept synchronized in lockstep, preserving all cross-agent neutrality and English language standards.
6. Use the specialized agent (`.agents/agents/agents-manager.md`) and automation tool (`python3 .agents/scripts/agents-manager.py`) to discover external repository resources, manage MCP servers, create, verify, update, analyze, import, export, and maintain workspace resources.
7. **AI Exclusions & Security SSOT**: Assistants must respect `.agents/aiignore` to prevent indexing secrets, credentials, or massive lockfiles, and keep adapter ignore files (`.cursorignore`, `.claudeignore`) in sync.
