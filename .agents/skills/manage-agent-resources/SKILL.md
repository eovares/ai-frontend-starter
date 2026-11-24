---
name: manage-agent-resources
description: >-
  Manage, scaffold, install, track, and update agent resources inside .agents/
  (skills, agents, instructions, plugins, prompts, scripts, hooks). Supports installing
  from GitHub repositories, recording upstream tracking in .agents/registry.json,
  and performing future updates.
---

# Manage Agent Resources Skill

Use this skill when you need to:
- Add a new skill, agent, prompt, instruction, hook, script, or plugin to `.agents/`.
- Import a skill or agent from a GitHub repository or Git URL.
- Track external sources in `.agents/registry.json` so they can be updated later.
- Update installed external resources to the latest commit/version from GitHub.
- List or audit existing workspace agent resources.

---

## 1. Quick Reference Commands

All management actions can be performed directly using the bundled Python script:

```bash
# Add a resource from GitHub / Git (auto-neutralizes model locks for cross-agent use)
python3 .agents/scripts/agents-manager.py add <type> <name> --url <github_url> [--subpath <path>] [--ref <branch>]

# Add raw without cross-agent neutralization
python3 .agents/scripts/agents-manager.py add <type> <name> --url <github_url> --raw

# Scaffold a user-created local resource (origin: user)
python3 .agents/scripts/agents-manager.py add <type> <name> [--author "<name>"] [--description "Description"]

# Synchronize untracked workspace files into registry.json
python3 .agents/scripts/agents-manager.py sync

# Neutralize model/vendor locks on an existing resource
python3 .agents/scripts/agents-manager.py neutralize <name>

# Update one or all tracked remote resources from remote GitHub
python3 .agents/scripts/agents-manager.py update [name]

# List all tracked resources categorized by origin (remote vs user)
python3 .agents/scripts/agents-manager.py list

# Remove a resource and deregister it
python3 .agents/scripts/agents-manager.py remove <name>
```

Supported `<type>` values: `skill`, `agent`, `instruction`, `plugin`, `prompt`, `script`, `hook`.

---

## 2. Resource Hierarchy & Canonical Paths

Every resource must strictly reside in `.agents/`:

| Resource Type | Path | Format & Invariants |
| :--- | :--- | :--- |
| **Skill** | `.agents/skills/<name>/SKILL.md` | Directory containing `SKILL.md` with YAML frontmatter (`name`, `description`). Optional `scripts/`, `references/`. |
| **Agent** | `.agents/agents/<name>.md` | Markdown document specifying persona, purpose, and operational rules. |
| **Instruction** | `.agents/instructions/<topic>.md` | Topic guideline referenced by `AGENTS.md`. |
| **Plugin** | `.agents/plugins/<name>/` | Directory containing `plugin.json` manifest. |
| **Prompt** | `.agents/prompts/<name>.md` | Markdown template with clear input parameters. |
| **Script** | `.agents/scripts/<name>` | Executable helper script (`chmod +x`). |
| **Hook** | `.agents/hooks/<name>` | Lifecycle trigger executable. |

---

## 3. GitHub Tracking & Registry Specification

When installing any resource from an external repository, the metadata is saved in `.agents/registry.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "version": "1.0.0",
  "description": "Registry tracking installed external agent resources and upstream repository sources.",
  "resources": {
    "my-external-skill": {
      "name": "my-external-skill",
      "type": "skill",
      "source_url": "https://github.com/example-user/skills-repo.git",
      "source_subpath": "skills/my-skill",
      "ref": "main",
      "commit": "4a1b2c3d...",
      "target_path": ".agents/skills/my-external-skill",
      "installed_at": "2026-11-23T23:25:00+00:00",
      "updated_at": "2026-11-23T23:25:00+00:00",
      "description": "Description of the skill"
    }
  }
}
```

---

## 4. Operational Procedures

### A. Installing a Skill from a GitHub Subfolder
If the user provides a URL like `https://github.com/owner/repo/tree/main/skills/my-skill`:
1. Run:
   ```bash
   python3 .agents/scripts/agents-manager.py add skill my-skill --url https://github.com/owner/repo/tree/main/skills/my-skill
   ```
2. Verify that `.agents/skills/my-skill/SKILL.md` exists and has valid YAML frontmatter.
3. Check `.agents/registry.json` to confirm the commit hash and repository URL are recorded.

### B. Updating Tracked Resources
1. Check what is installed:
   ```bash
   python3 .agents/scripts/agents-manager.py list
   ```
2. Pull updates from GitHub:
   ```bash
   python3 .agents/scripts/agents-manager.py update <name>
   ```
3. Inspect `git diff` to review upstream changes before committing.

### C. Cross-Agent Model & Vendor Neutralization (With Mandatory Approval)
When copying or updating skills from external repositories:
1. The manager scans for model locks (`model: ...`) and vendor-specific paths or directives.
2. If locks are detected, it **displays the exact changes and prompts the user for confirmation** before altering any file:
   ```text
   ⚠️  CROSS-AGENT NEUTRALIZATION PROMPT: '<name>'
   The following vendor or model-specific locks were detected:
     📄 File: .agents/skills/<name>/SKILL.md
        • Neutralize model lock 'model: claude-3-5-sonnet' -> model-agnostic
   Do you accept neutralizing '<name>' for cross-agent compatibility? [y/N]:
   ```
3. If confirmed (`y`), changes are applied. If declined (`n`), the resource is preserved in raw upstream format.
4. To automate without prompting (e.g. in CI scripts), pass `-y` or `--yes`.
5. To audit an existing resource at any time:
   ```bash
   python3 .agents/scripts/agents-manager.py neutralize <name>
   ```

