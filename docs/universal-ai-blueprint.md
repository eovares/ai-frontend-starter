# Universal AI Assistants Project Blueprint

A comprehensive, reusable guide for setting up multi-assistant AI workflows (**Claude Code**, **Antigravity**, **GitHub Copilot**, **Cursor**, etc.) in any new or existing software repository.

---

## 1. Core Architecture: The SSOT Pattern

When multiple AI coding assistants collaborate on the same repository, avoid defining rules in multiple vendor-specific locations. Instead, use the **Single Source of Truth (SSOT)** pattern:

```text
                              ┌───────────────────────────────────┐
                              │     Universal SSOT: AGENTS.md     │
                              │        (.agents/ Architecture)    │
                              └─────────────────┬─────────────────┘
                                                │
         ┌───────────────────────┬──────────────┴──────────────┬────────────────────────┐
         ▼                       ▼                             ▼                        ▼
┌──────────────────┐    ┌──────────────────┐         ┌──────────────────┐     ┌──────────────────┐
│   Antigravity    │    │   Claude Code    │         │      Cursor      │     │  GitHub Copilot  │
│ (GEMINI.md / AGY)│    │   (CLAUDE.md)    │         │  (.cursorrules)  │     │ (.github/copilot)│
└──────────────────┘    └──────────────────┘         └──────────────────┘     └──────────────────┘
```

### The Three Golden Rules

1. **Single Source of Truth (`AGENTS.md`):** All rules, conventions, architectural decisions, and lifecycle requirements must live in `AGENTS.md`.
2. **Lightweight Tool Adapters:** Tool-specific files (`CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, `.cursorrules`) must be minimal shims (< 15 lines) pointing back to `./AGENTS.md`.
3. **English for All AI Artifacts:** Write all AI configurations, instructions, rules, prompts, and skills in English. English produces optimal tokenization, clearer instruction following, and lower token consumption across modern LLMs.

---

## 2. Universal Directory Hierarchy: `.agents/`

To prevent creating fragmented proprietary folders (`.claude/`, `.gemini/`, `.cursor/`), all AI workspace assets must reside in the standard **`.agents/`** directory tree:

```text
.agents/
├── agents/        # Specialized agent personas and subagent definitions
├── hooks/         # Lifecycle hooks (pre-tool/post-tool execution scripts)
├── instructions/  # Extended, modular instruction files that complement AGENTS.md
├── plugins/       # Bundled capabilities (skills + rules + hooks)
├── prompts/       # Reusable prompt templates and query patterns
├── scripts/       # Automation helper scripts executed by agents
└── skills/        # Reusable procedural skills (<skill-name>/SKILL.md)
```

### Preserving Empty Folders in Git with `.gitkeep`

#### 1. Why Git Ignores Empty Directories

By design, Git tracks **file content (blobs)** and directory trees containing files. It does **not** track directory nodes themselves. As a result:

- An empty directory will never appear in `git status`.
- An empty directory cannot be staged with `git add`.
- When pushing to a remote (e.g., GitHub, GitLab) or cloning the repository on another machine, empty folders will be completely missing.

#### 2. The `.gitkeep` Convention

To solve this without cluttering the repository with dummy content, the industry convention is to place a hidden zero-byte file named **`.gitkeep`** inside each directory you want to preserve:

```bash
# Add .gitkeep to all empty .agents subdirectories:
touch .agents/{agents,hooks,instructions,plugins,prompts,scripts,skills}/.gitkeep
```

You can also automate this recursively for any empty directory in your workspace:

```bash
find .agents -type d -empty -exec touch {}/.gitkeep \;
```

#### 3. Lifecycle & Best Practices for `.gitkeep`

- **Zero Overhead:** A `.gitkeep` file is 0 bytes and consumes negligible repository space.
- **Retain vs. Delete:**
  - _Option A (Recommended):_ Leave `.gitkeep` in the directory permanently. Even if you add or remove actual files later, the folder will never disappear if all other files are temporarily deleted or moved during a refactor.
  - _Option B:_ Delete `.gitkeep` once actual files (e.g., a `.sh` script or `SKILL.md`) are added to that directory.
- **Ensure `.gitignore` Compatibility:** If your project uses aggressive `.gitignore` rules (e.g., ignoring hidden files), ensure `.gitkeep` is explicitly permitted:

  ```gitignore
  # Allow .gitkeep files to be tracked
  !.gitkeep
  ```

---

## 3. Template Specifications for Any New Project

### A. Root: `AGENTS.md` (SSOT Template)

```markdown
# AGENTS.md

> **Single Source of Truth (SSOT)** for all AI coding assistants.

## 1. Project Context

- **Project**: <project-name>
- **Stack**: <technologies-used>
- **Goal**: <main-objective>

## 2. Standards and Coding Conventions

- **Naming**: <conventions>
- **Architecture**: <patterns>
- **Lifecycle & Resource Management**: <cleanup-rules>

## 3. Development Workflow & Tooling

- **Dev Server**: <command>
- **Formatting**: <formatter>
- **Linting**: <linter>

## 4. Universal Workspace Customization Directory (`.agents/`)

All agent resources must reside under `.agents/` (never vendor-specific folders).
```

### B. Root: `CLAUDE.md` (Claude Code Adapter)

```markdown
# CLAUDE.md

Guidelines for Claude Code.

All architectural, code style, lifecycle, and component standards are defined in:
👉 **[AGENTS.md](./AGENTS.md)**

## Claude Code Specific Notes

- Follow all standards in `AGENTS.md` strictly.
- Run commands using non-blocking approaches when launching development servers.
```

### C. Root: `GEMINI.md` (Antigravity Adapter)

```markdown
# GEMINI.md

Instructions for Antigravity in this workspace.

All architectural guidelines, lifecycle rules, and standards are centralized in:
👉 **[AGENTS.md](./AGENTS.md)**

## Antigravity-Specific Notes

- Prioritize standards defined in `AGENTS.md`.
```

### D. Subdirectory: `.github/copilot-instructions.md` (GitHub Copilot Adapter)

```markdown
# GitHub Copilot Instructions

All project standards, architectural rules, and code conventions are centralized in:
👉 **[AGENTS.md](../AGENTS.md)**

## Core Rules for Copilot

- Adhere to the core standards defined in `AGENTS.md`.
```

In `.vscode/settings.json`, register the instruction file:

```json
{
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "file": ".github/copilot-instructions.md"
    }
  ]
}
```

### E. Root: `.cursorrules` (Cursor Adapter)

```markdown
# .cursorrules

Instructions for Cursor.

All architectural guidelines, project rules, and conventions are centralized in:
👉 [AGENTS.md](./AGENTS.md)

## Cursor-Specific Notes

- Always follow project architecture, guidelines, and standards in accordance with `AGENTS.md`.
- Store any agent resources (skills, agents, instructions, prompts) inside `.agents/`.
```

### F. Generic VS Code Configuration (`.vscode/`)

Keep VS Code workspace configurations generic, stack-agnostic, and focused on clean editor hygiene and AI assistant linking:

#### 1. `.vscode/settings.json`

```json
{
  "editor.formatOnSave": true,
  "editor.tabSize": 2,
  "editor.insertSpaces": true,
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,
  "files.exclude": {
    "**/.git": true,
    "**/.DS_Store": true
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/.git": true,
    "**/dist": true,
    "**/build": true
  },
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "file": ".github/copilot-instructions.md"
    }
  ]
}
```

#### 2. `.vscode/extensions.json`

```json
{
  "recommendations": [
    "github.copilot",
    "github.copilot-chat",
    "anthropic.claude-code",
    "editorconfig.editorconfig"
  ]
}
```

### G. Root: `.editorconfig` (Editor-Agnostic Formatting SSOT)

`.editorconfig` acts as the universal formatting Single Source of Truth across editors (VS Code, Cursor, JetBrains, Neovim, and Zed), complementing `.vscode/settings.json` without coupling formatting rules to a single IDE:

```ini
# EditorConfig is awesome: https://EditorConfig.org
# Single Source of Truth (SSOT) for cross-editor formatting standards.

root = true

# Default settings for all files
[*]
charset = utf-8
end_of_line = lf
indent_style = space
indent_size = 2
insert_final_newline = true
trim_trailing_whitespace = true

# Markdown: preserve trailing whitespace for hard line breaks
[*.md]
trim_trailing_whitespace = false

# Python (PEP 8)
[*.{py,pyi}]
indent_size = 4

# Makefiles require literal tabs
[{Makefile,makefile,GNUmakefile,*.mk}]
indent_style = tab

# Go (gofmt standard)
[*.go]
indent_style = tab

# Shell scripts must always use LF
[*.{sh,bash,zsh}]
end_of_line = lf

# Windows batch scripts require CRLF
[*.{bat,cmd}]
end_of_line = crlf
```

### H. Universal AI Exclusions: `.agents/aiignore` (SSOT)

To prevent AI assistants from burning context tokens on massive dependencies, build directories, or accidentally indexing credentials (`.env`, private keys), define exclusions centrally in `.agents/aiignore` and synchronize to `.cursorignore` and `.claudeignore`:

```gitignore
# .agents/aiignore - SSOT for AI Assistant Exclusions
.env
.env.*
!.env.example
*.pem
*.key
*.cert
credentials.json
node_modules/
package-lock.json
yarn.lock
pnpm-lock.yaml
dist/
build/
out/
.cache/
__pycache__/
*.log
.DS_Store
.cursorindexing/
.claude/
```

Synchronize automatically with:
```bash
python3 .agents/scripts/agents-manager.py ignore sync
```

### I. Automated Quality & CI (Husky Pre-Commit & GitHub Actions)

To guarantee that agent resources remain healthy and all shims stay synchronized, enforce automated validation:

1. **Husky Pre-Commit Hook (`.husky/pre-commit`):**
   ```sh
   #!/bin/sh
   python3 .agents/scripts/agents-manager.py verify
   ```

2. **GitHub Actions Workflow (`.github/workflows/validate-agents.yml`):**
   Runs `agents-manager.py verify` and `doctor` on every push and pull request.

---

## 4. Quick Bootstrap Script (Bash)

To scaffold this entire architecture into any new repository, run this one-liner script from the repository root:

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1. Create directory structure
mkdir -p .agents/{agents,hooks,instructions,plugins,prompts,scripts,skills}
mkdir -p .github .vscode docs

# 2. Add .gitkeep to ensure empty folders are committed
touch .agents/{agents,hooks,instructions,plugins,prompts,scripts,skills}/.gitkeep

# 3. Create tool adapters with portable relative paths
cat << 'EOF' > CLAUDE.md
# CLAUDE.md
Guidelines for Claude Code.
All standards and conventions are defined in:
👉 **[AGENTS.md](./AGENTS.md)**
EOF

cat << 'EOF' > GEMINI.md
# GEMINI.md
Instructions for Antigravity.
All standards and conventions are defined in:
👉 **[AGENTS.md](./AGENTS.md)**
EOF

cat << 'EOF' > .github/copilot-instructions.md
# GitHub Copilot Instructions
All standards and conventions are defined in:
👉 **[AGENTS.md](../AGENTS.md)**
EOF

cat << 'EOF' > .cursorrules
# .cursorrules
Instructions for Cursor.
All standards and conventions are defined in:
👉 **[AGENTS.md](./AGENTS.md)**
EOF

# 4. Create generic VS Code configuration
cat << 'EOF' > .vscode/settings.json
{
  "editor.formatOnSave": true,
  "editor.tabSize": 2,
  "editor.insertSpaces": true,
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,
  "files.exclude": {
    "**/.git": true,
    "**/.DS_Store": true
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/.git": true,
    "**/dist": true,
    "**/build": true
  },
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "file": ".github/copilot-instructions.md"
    }
  ]
}
EOF

cat << 'EOF' > .vscode/extensions.json
{
  "recommendations": [
    "github.copilot",
    "github.copilot-chat",
    "anthropic.claude-code",
    "editorconfig.editorconfig"
  ]
}
EOF

# 5. Create universal .editorconfig
cat << 'EOF' > .editorconfig
# EditorConfig is awesome: https://EditorConfig.org
# Single Source of Truth (SSOT) for cross-editor formatting standards.

root = true

# Default settings for all files
[*]
charset = utf-8
end_of_line = lf
indent_style = space
indent_size = 2
insert_final_newline = true
trim_trailing_whitespace = true

# Markdown: preserve trailing whitespace for hard line breaks
[*.md]
trim_trailing_whitespace = false

# Python (PEP 8)
[*.{py,pyi}]
indent_size = 4

# Makefiles require literal tabs
[{Makefile,makefile,GNUmakefile,*.mk}]
indent_style = tab

# Go (gofmt standard)
[*.go]
indent_style = tab

# Shell scripts must always use LF
[*.{sh,bash,zsh}]
end_of_line = lf

# Windows batch scripts require CRLF
[*.{bat,cmd}]
end_of_line = crlf
EOF

echo "✅ AI architecture scaffolded successfully."
```

---

## 5. Summary of Best Practices

1. **Portable Relative Paths:** Always use relative links (`./AGENTS.md`, `../AGENTS.md`). Never hardcode absolute paths (`file:///Users/...`).
2. **Rule Modification:** When updating rules, edit **only `AGENTS.md`**. The adapters will automatically propagate the updates to all assistants.
3. **English Default:** Standardize all configuration files in English for optimal LLM token efficiency and comprehension.
4. **Skills Location:** Store reusable capabilities in `.agents/skills/<skill-name>/SKILL.md`.
