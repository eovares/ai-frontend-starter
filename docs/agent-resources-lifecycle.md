# Agent Resources Lifecycle & Provenance Guide

A comprehensive guide to managing, tracking, and updating the 9 universal agent resource types in the `.agents/` ecosystem across multiple AI assistants (**Claude Code**, **Antigravity**, **GitHub Copilot**, and **Cursor**).

---

## 1. Overview & Architectural Philosophy

When scaling AI agent capabilities in software repositories, teams face two major challenges:
1. **Provenance Drift:** Losing track of whether a tool, prompt, or skill was authored locally by a team member or imported from an external repository (e.g. Anthropic, Google Chrome, Figma, or community repos).
2. **Upstream Invalidation:** Inability to safely update imported capabilities from upstream Git repositories without accidentally overwriting local customizations.

To solve this, this repository implements a canonical **Provenance & Registry System** centered around **`.agents/registry.json`** and driven by the CLI utility **`.agents/scripts/agents-manager.py`**.

```text
                              ┌───────────────────────────────────┐
                              │     .agents/registry.json         │
                              │  (Central Provenance Registry)    │
                              └─────────────────┬─────────────────┘
                                                │
         ┌──────────────────────────────────────┴──────────────────────────────────────┐
         ▼                                                                             ▼
┌─────────────────────────────────┐                                   ┌─────────────────────────────────┐
│     User-Created Resources      │                                   │    Remote / External Resources  │
│        (origin: "user")         │                                   │       (origin: "remote")        │
├─────────────────────────────────┤                                   ├─────────────────────────────────┤
│ • Scaffolds standardized code   │                                   │ • Cloned from Git / GitHub      │
│ • Attributed to author          │                                   │ • Pinned to Git commit SHA      │
│ • Protected from remote updates │                                   │ • Updatable via `update [name]` │
│ • Tracked in workspace Git      │                                   │ • Model-lock neutralized        │
└─────────────────────────────────┘                                   └─────────────────────────────────┘
```

---

## 2. The 9 Resource Types

Every agent resource resides in the canonical `.agents/` folder under its designated type directory:

| Type | Canonical Path | Description | Format / Entrypoint |
| :--- | :--- | :--- | :--- |
| **`skill`** | `.agents/skills/<name>/` | Procedural workflows, domain runbooks, and multi-step tasks. | `SKILL.md` with YAML frontmatter |
| **`agent`** | `.agents/agents/<name>.md` | Specialized persona, system prompt, and subagent role definitions. | Markdown with persona guidelines |
| **`instruction`** | `.agents/instructions/<topic>.md` | Extended guidelines and modular standards that complement `AGENTS.md`. | Markdown |
| **`plugin`** | `.agents/plugins/<name>/` | Namespaced bundles grouping skills, rules, and hooks. | `plugin.json` manifest |
| **`prompt`** | `.agents/prompts/<name>.md` | Reusable prompt templates, query structures, and review tasks. | Markdown template |
| **`schema`** | `.agents/schemas/<name>.schema.json` | Local JSON Schemas providing validation and editor autocomplete. | JSON Schema Draft 2020-12 |
| **`script`** | `.agents/scripts/<name>` | Automation scripts and operational CLI tools executed by agents. | Executable (`chmod 755`) |
| **`hook`** | `.agents/hooks/<name>` | Lifecycle triggers (e.g. pre-tool / post-tool execution scripts). | Executable (`chmod 755`) |
| **`mcp`** | `.agents/mcp.json` | Model Context Protocol servers synced to all AI tools. | JSON server definitions |

---

## 3. Provenance Schema (`.agents/registry.json`)

All resources are tracked in `.agents/registry.json`, validated by the local schema [`.agents/schemas/registry.schema.json`](file:///Users/eovares/code/ai-frontend-starter/.agents/schemas/registry.schema.json).

### Schema Structure Example

```json
{
  "$schema": "./schemas/registry.schema.json",
  "version": "1.0.0",
  "description": "Registry tracking installed external agent resources and upstream repository sources.",
  "resources": {
    "modern-web-guidance": {
      "name": "modern-web-guidance",
      "type": "skill",
      "origin": "remote",
      "source_url": "https://github.com/GoogleChrome/modern-web-guidance.git",
      "source_subpath": "skills/modern-web-guidance",
      "ref": "main",
      "commit": "2b4aa13a72dd47cd135b06ce5abfccd92e19b24f",
      "target_path": ".agents/skills/modern-web-guidance",
      "created_at": "2026-11-24T05:33:46.627881+00:00",
      "updated_at": "2026-11-24T05:43:51.324097+00:00",
      "description": "Search tool for modern web development best practices"
    },
    "filesystem": {
      "name": "filesystem",
      "type": "mcp",
      "origin": "user",
      "author": "Edward Ovares",
      "target_path": ".agents/mcp.json",
      "created_at": "2026-11-24T14:54:07.858971+00:00",
      "updated_at": "2026-11-24T14:54:07.858971+00:00",
      "description": "Secure local workspace file read and edit tools"
    }
  }
}
```

### Core Metadata Fields

* **`name`** *(string)*: Unique resource identifier.
* **`type`** *(string)*: One of `skill`, `agent`, `instruction`, `plugin`, `prompt`, `schema`, `script`, `hook`, `mcp`.
* **`origin`** *(string)*:
  * `"user"`: Created locally in this workspace.
  * `"remote"`: Imported from an external Git repository.
* **`target_path`** *(string)*: Relative workspace path to the installed file or directory.
* **`created_at` / `updated_at`** *(ISO 8601)*: Creation and latest update timestamps.
* **`source_url`** *(string, remote only)*: Upstream Git repository URL.
* **`source_subpath`** *(string, remote only)*: Subpath inside the upstream repository.
* **`ref`** *(string, remote only)*: Pinned branch, tag, or Git reference (defaults to `main`).
* **`commit`** *(string, remote only)*: Pinned SHA-1 commit hash for deterministic reproduction.
* **`author`** *(string, user only)*: Creator attribution.

---

## 4. Lifecycle Operations & CLI Commands

All lifecycle operations are managed via `python3 .agents/scripts/agents-manager.py`:

### A. Creating User Resources (`origin: "user"`)

Scaffold a standardized resource for any of the 9 types:

```bash
# General syntax:
python3 .agents/scripts/agents-manager.py create <type> <name> [--author <author>] [--description <desc>]

# Examples:
python3 .agents/scripts/agents-manager.py create agent code-reviewer --description "Domain code review agent"
python3 .agents/scripts/agents-manager.py create prompt pr-review-template
python3 .agents/scripts/agents-manager.py create instruction security-rules
python3 .agents/scripts/agents-manager.py create hook pre-tool-guard
python3 .agents/scripts/agents-manager.py create script deploy-helper
python3 .agents/scripts/agents-manager.py create schema api-contract
python3 .agents/scripts/agents-manager.py create mcp sqlite-db
```

**Behavior:**
1. Generates the canonical directory/file with appropriate boilerplate (e.g. YAML frontmatter for skills, JSON Schema definitions for schemas, shebang and `chmod 755` for scripts/hooks, or server entry in `mcp.json`).
2. Registers the item in `registry.json` with `origin: "user"`.
3. Protects the item against accidental remote overwrites.

---

### B. Importing Remote Resources (`origin: "remote"`)

Import capabilities from external GitHub or Git repositories:

```bash
# General syntax:
python3 .agents/scripts/agents-manager.py add <type> <name> --url <github-url> [--subpath <path>] [--ref <branch>]

# Examples:
# 1. Import a remote skill from a subpath:
python3 .agents/scripts/agents-manager.py add skill chrome-extensions \
  --url https://github.com/GoogleChrome/modern-web-guidance.git \
  --subpath skills/chrome-extensions

# 2. Import an external agent persona:
python3 .agents/scripts/agents-manager.py add agent qa-specialist \
  --url https://github.com/example-org/agent-personas.git \
  --subpath agents/qa-specialist.md

# 3. Import a remote MCP server definition:
python3 .agents/scripts/agents-manager.py add mcp fetch-server \
  --url https://github.com/modelcontextprotocol/servers.git \
  --subpath src/fetch
```

**Behavior:**
1. Clones the remote repository at the specified reference.
2. Extracts the requested subpath or file.
3. Automatically sets executable permissions on imported scripts/hooks.
4. Audits and applies **Cross-Agent Neutralization** (removes hardcoded model locks like `model: claude-3-5...`).
5. Pins the exact SHA-1 commit hash into `registry.json` with `origin: "remote"`.

---

### C. Discovering Resources in Remote Repositories

Inspect any remote repository to discover all available agent resources:

```bash
python3 .agents/scripts/agents-manager.py discover <github-url> [--import-recommended]
```

Scans for skills, agents, instructions, prompts, plugins, MCP servers, schemas, scripts, and hooks, displaying token sizes and recommendations, with one-click batch import.

---

### D. Updating Tracked Remote Resources (`update`)

Update external resources whenever upstream repositories release improvements:

```bash
# Update a specific remote resource:
python3 .agents/scripts/agents-manager.py update modern-web-guidance

# Update ALL remote resources in the workspace:
python3 .agents/scripts/agents-manager.py update
```

**Behavior:**
* Re-fetches the latest commit from the upstream Git repository.
* Updates local files and refreshes the pinned `commit` SHA and `updated_at` in `registry.json`.
* Re-applies cross-agent neutralization.
* **Safe Guard:** Local user-created resources (`origin: "user"`) are automatically skipped:
  ```text
  [INFO] 'filesystem' was created locally by 'Edward Ovares' (origin: user). It cannot be updated from remote.
  ```

---

### E. Indexing Untracked Files (`sync`)

If you manually create or paste files into `.agents/` without using the CLI:

```bash
python3 .agents/scripts/agents-manager.py sync
```

Scans all subdirectories (`agents/`, `skills/`, `schemas/`, `scripts/`, `hooks/`, `prompts/`, `instructions/`, `plugins/`, and servers in `mcp.json`), detects unregistered items, and indexes them in `registry.json` as `origin: "user"`.

---

### F. Inspecting & Listing Resources

```bash
# List all resources grouped by Remote, User-Created, and Untracked:
python3 .agents/scripts/agents-manager.py list

# Display detailed metadata card of a specific resource:
python3 .agents/scripts/agents-manager.py info <name>
```

---

### G. Deregistering & Removing Resources

```bash
python3 .agents/scripts/agents-manager.py remove <name>
```

* Removes the entry from `.agents/registry.json`.
* Deletes the corresponding file or folder.
* For `mcp` resources: safely deletes the server entry from `.agents/mcp.json` and resynchronizes adapters without deleting the configuration file.

---

## 5. Health Checks, Invariants & Diagnostics

Ensure the integrity of all agent resources with automated audits:

```bash
# Verify integrity, permissions, frontmatter, and registry health:
python3 .agents/scripts/agents-manager.py verify [--fix]

# Comprehensive environment, adapter parity, and security diagnostics:
python3 .agents/scripts/agents-manager.py doctor
```

### Verification Invariants Checked:
1. **Target Existence:** Every tracked resource in `registry.json` exists on disk.
2. **MCP Parity:** Tracked MCP resources exist in `.agents/mcp.json`.
3. **Registration Parity:** No unregistered files exist in `.agents/` subdirectories.
4. **Skill Frontmatter:** All `SKILL.md` files possess valid YAML frontmatter with `name` and `description`.
5. **Plugin Manifests:** All `plugin.json` files are valid JSON.
6. **Execution Permissions:** All scripts in `scripts/` and `hooks/` have executable bits set (`chmod +x`).
7. **No Leaked Home Paths:** No hardcoded `/Users/<username>/` or `/home/<username>/` paths.
8. **No Rogue Vendor Folders:** No `.claude/` or `.gemini/` directories outside canonical `.agents/`.
9. **MCP Sync Parity:** `.vscode/mcp.json` and `.mcp.json` match `.agents/mcp.json`.
10. **AI Ignore Parity:** `.cursorignore` and `.claudeignore` match `.agents/aiignore`.
11. **JSON Schemas:** Canonical schemas exist in `.agents/schemas/`.

---

## 6. Integration in CI/CD & Developer Tooling

To ensure that no broken or out-of-sync agent resources are committed:

1. **Pre-commit Hook ([`.husky/pre-commit`](file:///Users/eovares/code/ai-frontend-starter/.husky/pre-commit)):**
   Automatically runs `python3 .agents/scripts/agents-manager.py verify` before every `git commit`.
2. **GitHub Actions ([`.github/workflows/validate-agents.yml`](file:///Users/eovares/code/ai-frontend-starter/.github/workflows/validate-agents.yml)):**
   Runs `verify` and `doctor` on every push and pull request.
3. **VS Code Tasks ([`.vscode/tasks.json`](file:///Users/eovares/code/ai-frontend-starter/.vscode/tasks.json)):**
   Run `verify`, `doctor`, `analyze`, `sync`, and `mcp sync` directly from `Cmd+Shift+P` → *Tasks: Run Task*.
