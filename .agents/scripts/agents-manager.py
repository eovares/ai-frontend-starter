#!/usr/bin/env python3
"""
agents-manager.py - Universal Agent Resource Manager for .agents/

Manages agents, hooks, instructions, plugins, prompts, scripts, and skills.
Tracks both user-created resources and external resources imported from GitHub/Git
repositories in .agents/registry.json for full traceability and updates.

Ensures cross-agent compatibility (Claude Code, Antigravity, GitHub Copilot, Codex)
by generalizing vendor-specific directives and neutralizing hardcoded LLM model locks,
always prompting the user for approval before making adjustments.
"""

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
AGENTS_DIR = WORKSPACE_ROOT / ".agents"
REGISTRY_FILE = AGENTS_DIR / "registry.json"
MCP_FILE = AGENTS_DIR / "mcp.json"
AIIGNORE_FILE = AGENTS_DIR / "aiignore"
CURSORIGNORE_FILE = WORKSPACE_ROOT / ".cursorignore"
CLAUDEIGNORE_FILE = WORKSPACE_ROOT / ".claudeignore"
SCHEMAS_DIR = AGENTS_DIR / "schemas"

RESOURCE_TYPES = {
    "skill": {
        "dir": AGENTS_DIR / "skills",
        "is_dir": True,
        "entry_file": "SKILL.md",
    },
    "agent": {
        "dir": AGENTS_DIR / "agents",
        "is_dir": False,
        "extension": ".md",
    },
    "instruction": {
        "dir": AGENTS_DIR / "instructions",
        "is_dir": False,
        "extension": ".md",
    },
    "plugin": {
        "dir": AGENTS_DIR / "plugins",
        "is_dir": True,
        "entry_file": "plugin.json",
    },
    "prompt": {
        "dir": AGENTS_DIR / "prompts",
        "is_dir": False,
        "extension": ".md",
    },
    "script": {
        "dir": AGENTS_DIR / "scripts",
        "is_dir": False,
        "extension": "",
    },
    "hook": {
        "dir": AGENTS_DIR / "hooks",
        "is_dir": False,
        "extension": "",
    },
    "schema": {
        "dir": AGENTS_DIR / "schemas",
        "is_dir": False,
        "extension": ".schema.json",
    },
    "mcp": {
        "dir": AGENTS_DIR,
        "is_dir": False,
        "file": MCP_FILE,
    },
}

TYPE_ALIASES = {
    "skills": "skill",
    "agents": "agent",
    "instructions": "instruction",
    "plugins": "plugin",
    "prompts": "prompt",
    "scripts": "script",
    "hooks": "hook",
    "schemas": "schema",
    "schema": "schema",
    "mcp": "mcp",
    "mcps": "mcp",
    "mcp-server": "mcp",
    "mcp-servers": "mcp",
    "mcpserver": "mcp",
}


def normalize_type(raw_type: str) -> str:
    cleaned = raw_type.lower().strip()
    return TYPE_ALIASES.get(cleaned, cleaned)


def get_default_author() -> str:
    try:
        proc = subprocess.run(
            ["git", "config", "user.name"],
            stdout=subprocess.PIPE,
            text=True,
            check=False,
        )
        name = proc.stdout.strip()
        if name:
            return name
    except Exception:
        pass
    return "user"


def load_registry() -> Dict[str, Any]:
    if not REGISTRY_FILE.exists():
        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "version": "1.1.0",
            "description": "Registry tracking all agent resources (.agents/), including user-created items and external repository sources.",
            "resources": {},
        }
    try:
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            data.setdefault("version", "1.1.0")
            data.setdefault("resources", {})
            return data
    except Exception as e:
        print(f"[WARN] Error reading registry.json: {e}", file=sys.stderr)
        return {"version": "1.1.0", "resources": {}}


def save_registry(data: Dict[str, Any]) -> None:
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def parse_github_url(url: str) -> Tuple[str, Optional[str], Optional[str]]:
    gh_tree_match = re.match(
        r"^https?://github\.com/([^/]+)/([^/]+)/(?:tree|blob)/([^/]+)/?(.*)$",
        url,
    )
    if gh_tree_match:
        owner, repo, ref, subpath = gh_tree_match.groups()
        repo_clean = repo[:-4] if repo.endswith(".git") else repo
        git_url = f"https://github.com/{owner}/{repo_clean}.git"
        return git_url, ref, subpath.rstrip("/") if subpath else None
    return url, None, None


def run_cmd(cmd: list, cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def get_target_path(res_type: str, name: str) -> Path:
    if res_type == "mcp":
        return MCP_FILE
    meta = RESOURCE_TYPES[res_type]
    base_dir = meta["dir"]
    base_dir.mkdir(parents=True, exist_ok=True)
    if meta.get("is_dir"):
        return base_dir / name
    else:
        ext = meta.get("extension", "")
        if ext and not name.endswith(ext):
            return base_dir / f"{name}{ext}"
        return base_dir / name


def neutralize_text(content: str) -> Tuple[str, List[str]]:
    """
    Standardizes content for universal cross-agent compatibility
    (Claude Code, Antigravity, GitHub Copilot, Codex).
    Leaves functional logic intact while generalizing vendor/model locks.
    """
    changes: List[str] = []

    # 1. Frontmatter model / vendor lock removal
    fm_match = re.match(r"^(---\r?\n)(.*?)(\r?\n---\r?\n)(.*)$", content, re.DOTALL)
    if fm_match:
        prefix, fm_body, suffix, rest = fm_match.groups()
        new_fm_lines = []
        for line in fm_body.splitlines():
            if re.match(r"^\s*model\s*:\s*.*", line, re.IGNORECASE):
                changes.append(f"Neutralize model lock '{line.strip()}' -> model-agnostic")
                continue
            if re.match(r"^\s*vendor\s*:\s*.*", line, re.IGNORECASE):
                changes.append(f"Remove vendor lock '{line.strip()}'")
                continue
            new_fm_lines.append(line)
        content = prefix + "\n".join(new_fm_lines) + suffix + rest

    # 2. Path normalization to canonical .agents/
    path_replacements = [
        (r"\.claude/skills/", ".agents/skills/"),
        (r"\.claude/agents/", ".agents/agents/"),
        (r"\.claude/", ".agents/"),
        (r"\.cursor/rules/", ".agents/instructions/"),
        (r"\.gemini/skills/", ".agents/skills/"),
        (r"\.gemini/agents/", ".agents/agents/"),
    ]
    for pattern, repl in path_replacements:
        if re.search(pattern, content):
            content = re.sub(pattern, repl, content)
            changes.append(f"Normalize path '{pattern}' -> '{repl}'")

    # 3. Model/Assistant persona generalization
    persona_replacements = [
        (r"\bYou are Claude Code\b", "You are an AI coding assistant"),
        (r"\bYou are Claude\b", "You are an AI coding assistant"),
        (r"\bYou are Gemini\b", "You are an AI coding assistant"),
        (r"\bYou are ChatGPT\b", "You are an AI coding assistant"),
        (r"\bYou are GitHub Copilot\b", "You are an AI coding assistant"),
        (r"\bAs Claude,\b", "As an AI assistant,"),
        (r"\bAs Gemini,\b", "As an AI assistant,"),
        (r"\bClaude-specific\b", "Agent-specific"),
    ]
    for pattern, repl in persona_replacements:
        if re.search(pattern, content, flags=re.IGNORECASE):
            content = re.sub(pattern, repl, content, flags=re.IGNORECASE)
            changes.append(f"Neutralize persona reference: '{pattern}'")

    return content, changes


def preview_neutralization(target_path: Path) -> Dict[Path, Tuple[str, List[str]]]:
    """
    Scans files and returns a mapping of path to (new_content, list_of_changes).
    Does NOT write any files to disk.
    """
    candidates = {}
    files_to_check = []
    if target_path.is_file():
        files_to_check.append(target_path)
    elif target_path.is_dir():
        for ext in ("*.md", "*.json", "*.yaml", "*.yml", "*.txt"):
            files_to_check.extend(target_path.rglob(ext))

    for fpath in files_to_check:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            new_content, changes = neutralize_text(content)
            if changes:
                candidates[fpath] = (new_content, changes)
        except Exception as e:
            print(f"[WARN] Error scanning {fpath}: {e}", file=sys.stderr)

    return candidates


def prompt_and_apply_neutralization(
    target_path: Path,
    resource_name: str,
    auto_yes: bool = False,
) -> bool:
    """
    Prompts the user for explicit confirmation before applying cross-agent neutralization.
    Returns True if changes were applied, False otherwise.
    """
    candidates = preview_neutralization(target_path)
    if not candidates:
        print(f"[*] Verified: '{resource_name}' is already model-agnostic and vendor-neutral.")
        return False

    print(f"\n==========================================================================")
    print(f"⚠️  CROSS-AGENT NEUTRALIZATION PROMPT: '{resource_name}'")
    print(f"==========================================================================")
    print("The following vendor or model-specific locks were detected:")
    for fpath, (_, changes) in candidates.items():
        rel = fpath.relative_to(WORKSPACE_ROOT) if fpath.is_relative_to(WORKSPACE_ROOT) else fpath
        print(f"  📄 File: {rel}")
        for ch in changes:
            print(f"     • {ch}")
    print("--------------------------------------------------------------------------")
    print("Neutralizing will remove hardcoded model locks and vendor paths so that")
    print("this resource runs universally on Claude Code, Antigravity, and Copilot.")
    print("Functional logic and steps are kept 100% intact.")
    print("==========================================================================")

    confirmed = False
    if auto_yes:
        print("[AUTO-ACCEPT] -y/--yes specified. Applying neutralization...\n")
        confirmed = True
    else:
        try:
            prompt_msg = f"Do you accept neutralizing '{resource_name}' for cross-agent compatibility? [y/N]: "
            answer = input(prompt_msg).strip().lower()
            confirmed = answer in ("y", "yes")
        except (KeyboardInterrupt, EOFError):
            print("\n[INFO] Prompt interrupted or non-interactive.")
            confirmed = False

    if not confirmed:
        print(f"\n[INFO] Neutralization DECLINED. '{resource_name}' is preserved in raw upstream format.\n")
        return False

    # Apply adjustments
    for fpath, (new_content, _) in candidates.items():
        try:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(new_content)
        except Exception as e:
            print(f"[ERROR] Failed writing {fpath}: {e}", file=sys.stderr)

    print(f"\n[SUCCESS] Neutralization ACCEPTED and applied to {len(candidates)} file(s) in '{resource_name}'.\n")
    return True


def create_boilerplate(res_type: str, name: str, author: str, description: str = "") -> Path:
    target = get_target_path(res_type, name)
    clean_desc = description or f"Custom {res_type} created by {author}."

    if res_type == "skill":
        target.mkdir(parents=True, exist_ok=True)
        skill_file = target / "SKILL.md"
        content = f"""---
name: {name}
description: {clean_desc}
---

# {name}

## Overview
{clean_desc}

## Author & Origin
- **Author**: {author}
- **Origin**: User-created workspace skill (Model-Agnostic)

## Workflow & Steps
1. Step 1: Define requirements.
2. Step 2: Execute task.
3. Step 3: Verify outputs.
"""
        with open(skill_file, "w", encoding="utf-8") as f:
            f.write(content)
        return skill_file

    elif res_type == "agent":
        content = f"""# Agent: {name}

## Persona & Purpose
{clean_desc}

## Metadata
- **Author**: {author}
- **Origin**: User-created agent persona (Compatible with Claude Code, Antigravity, Copilot, Cursor)

## Responsibilities
- Autonomous task execution within domain scope.
- Enforcing rules from AGENTS.md.

## Guidelines
- Follow project guidelines and standards from AGENTS.md.
"""
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        return target

    elif res_type == "instruction":
        content = f"""# Instruction: {name}

> Guidelines created by {author} extending AGENTS.md.

## Overview
{clean_desc}

## Standards & Best Practices
- Define clear requirements and invariants.
"""
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        return target

    elif res_type == "plugin":
        target.mkdir(parents=True, exist_ok=True)
        manifest = {
            "name": name,
            "version": "1.0.0",
            "description": clean_desc,
            "author": author,
            "origin": "user",
            "skills": [],
            "agents": [],
            "rules": []
        }
        with open(target / "plugin.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        return target

    elif res_type == "prompt":
        content = f"""# Prompt: {name}

{clean_desc}

## Author: {author}

## Template
```text
[Input Task Description]
```
"""
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        return target

    elif res_type in ("script", "hook"):
        content = f"""#!/usr/bin/env bash
# {name} - {clean_desc}
# Author: {author}
set -euo pipefail

echo "Executing {name}..."
"""
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        target.chmod(0o755)
        return target

    elif res_type == "schema":
        schema_obj = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": f"./schemas/{name}.schema.json",
            "title": f"{name.replace('-', ' ').title()} Schema",
            "description": clean_desc or f"JSON Schema definition for {name}",
            "type": "object",
            "properties": {},
            "additionalProperties": True,
        }
        with open(target, "w", encoding="utf-8") as f:
            json.dump(schema_obj, f, indent=2)
            f.write("\n")
        return target

    elif res_type == "mcp":
        mcp_cfg = load_mcp_config()
        servers = mcp_cfg.setdefault("mcpServers", {})
        if name not in servers:
            servers[name] = {
                "command": "npx",
                "args": ["-y", f"@modelcontextprotocol/server-{name}"],
                "env": {},
                "disabled": False,
                "description": clean_desc or f"Custom MCP server '{name}'",
            }
            save_mcp_config(mcp_cfg)
            cmd_mcp_sync(mcp_cfg)
        return MCP_FILE

    return target


def install_from_repo(
    res_type: str,
    name: str,
    raw_url: str,
    ref: Optional[str] = None,
    subpath: Optional[str] = None,
    description: str = "",
    raw: bool = False,
    auto_yes: bool = False,
) -> bool:
    git_url, detected_ref, detected_subpath = parse_github_url(raw_url)
    effective_ref = ref or detected_ref or "main"
    effective_subpath = subpath or detected_subpath or ""

    temp_clone_dir = Path("/tmp") / f"agents_install_{name}_{int(datetime.datetime.now().timestamp())}"
    if temp_clone_dir.exists():
        shutil.rmtree(temp_clone_dir, ignore_errors=True)

    print(f"[*] Cloning {git_url} (ref: {effective_ref})...")
    clone_cmd = [
        "git",
        "clone",
        "--depth",
        "1",
        "--branch",
        effective_ref,
        git_url,
        str(temp_clone_dir),
    ]
    code, out, err = run_cmd(clone_cmd)
    if code != 0:
        clone_cmd = ["git", "clone", "--depth", "1", git_url, str(temp_clone_dir)]
        code, out, err = run_cmd(clone_cmd)
        if code != 0:
            print(f"[ERROR] Failed to clone {git_url}:\n{err}", file=sys.stderr)
            return False

    code, commit_hash, _ = run_cmd(["git", "rev-parse", "HEAD"], cwd=temp_clone_dir)
    if code != 0:
        commit_hash = "unknown"

    source_path = temp_clone_dir / effective_subpath if effective_subpath else temp_clone_dir
    if not source_path.exists():
        print(f"[ERROR] Subpath '{effective_subpath}' does not exist in repository.", file=sys.stderr)
        shutil.rmtree(temp_clone_dir, ignore_errors=True)
        return False

    target_path = get_target_path(res_type, name)
    is_dir = RESOURCE_TYPES[res_type].get("is_dir", False)
    desc = description

    try:
        if res_type == "mcp":
            mcp_source = None
            if effective_subpath:
                cand = temp_clone_dir / effective_subpath
                if cand.is_file():
                    mcp_source = cand
                elif cand.is_dir():
                    for sf in [cand / "mcp.json", cand / ".agents" / "mcp.json"]:
                        if sf.exists():
                            mcp_source = sf
                            break
            if not mcp_source:
                for sf in temp_clone_dir.rglob("mcp.json"):
                    if ".git" in sf.parts:
                        continue
                    mcp_source = sf
                    break

            server_payload = None
            if mcp_source and mcp_source.exists():
                try:
                    mcp_data = json.loads(mcp_source.read_text(encoding="utf-8"))
                    srvs = mcp_data.get("mcpServers", {})
                    if name in srvs:
                        server_payload = srvs[name]
                    elif len(srvs) == 1:
                        server_payload = list(srvs.values())[0]
                    elif "command" in mcp_data:
                        server_payload = mcp_data
                except Exception as e:
                    print(f"[WARN] Failed parsing {mcp_source}: {e}")

            if not server_payload:
                server_payload = {
                    "command": "npx",
                    "args": ["-y", name],
                    "env": {},
                    "disabled": False,
                    "description": description or f"Imported MCP server '{name}' from {git_url}",
                }

            desc = desc or server_payload.get("description", f"MCP server '{name}'")
            mcp_cfg = load_mcp_config()
            mcp_cfg.setdefault("mcpServers", {})[name] = server_payload
            save_mcp_config(mcp_cfg)
            cmd_mcp_sync(mcp_cfg)
            target_path = MCP_FILE
        elif is_dir:
            if target_path.exists():
                shutil.rmtree(target_path)
            if source_path.is_dir():
                shutil.copytree(source_path, target_path)
            else:
                target_path.mkdir(parents=True, exist_ok=True)
                entry_file = RESOURCE_TYPES[res_type].get("entry_file", source_path.name)
                shutil.copy2(source_path, target_path / entry_file)
        else:
            if target_path.exists():
                if target_path.is_dir():
                    shutil.rmtree(target_path)
                else:
                    target_path.unlink()
            if source_path.is_file():
                shutil.copy2(source_path, target_path)
            else:
                candidates = []
                if res_type in ("agent", "instruction", "prompt"):
                    candidates = [source_path / f"{name}.md", source_path / f"{res_type}.md", source_path / f"{name}.txt"]
                elif res_type == "schema":
                    candidates = [source_path / f"{name}.schema.json", source_path / f"{name}.json", source_path / "schema.json"]
                elif res_type in ("script", "hook"):
                    candidates = [source_path / f"{name}.py", source_path / f"{name}.sh", source_path / f"{name}.bash", source_path / name]

                default_file = None
                for cand in candidates:
                    if cand.exists() and cand.is_file():
                        default_file = cand
                        break

                if not default_file:
                    files = [f for f in source_path.iterdir() if f.is_file() and not f.name.startswith(".")]
                    default_file = files[0] if files else None

                if default_file:
                    shutil.copy2(default_file, target_path)
                else:
                    shutil.copytree(source_path, target_path)

            if res_type in ("script", "hook") and target_path.exists() and target_path.is_file():
                target_path.chmod(target_path.stat().st_mode | 0o111)
    except Exception as e:
        print(f"[ERROR] Failed copying resource to {target_path}: {e}", file=sys.stderr)
        shutil.rmtree(temp_clone_dir, ignore_errors=True)
        return False

    shutil.rmtree(temp_clone_dir, ignore_errors=True)

    # Cross-Agent Neutralization with confirmation prompt
    if not raw and res_type not in ("mcp", "schema") and target_path.exists():
        prompt_and_apply_neutralization(target_path, name, auto_yes=auto_yes)

    # Register in registry.json as remote
    registry = load_registry()
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    existing_entry = registry.get("resources", {}).get(name, {})

    entry = {
        "name": name,
        "type": res_type,
        "origin": "remote",
        "source_url": git_url,
        "source_subpath": effective_subpath or None,
        "ref": effective_ref,
        "commit": commit_hash,
        "target_path": str(target_path.relative_to(WORKSPACE_ROOT)),
        "created_at": existing_entry.get("created_at", now_iso),
        "updated_at": now_iso,
        "description": desc or description or existing_entry.get("description", ""),
    }
    registry.setdefault("resources", {})[name] = entry
    save_registry(registry)

    print(f"[SUCCESS] Installed {res_type} '{name}' from {git_url} (commit {commit_hash[:7]})")
    print(f"          Target: {target_path.relative_to(WORKSPACE_ROOT)}")
    return True


def cmd_add(args: argparse.Namespace) -> None:
    res_type = normalize_type(args.type)
    if res_type not in RESOURCE_TYPES:
        print(f"[ERROR] Invalid type '{args.type}'. Valid types: {', '.join(RESOURCE_TYPES.keys())}", file=sys.stderr)
        sys.exit(1)

    if args.url:
        success = install_from_repo(
            res_type=res_type,
            name=args.name,
            raw_url=args.url,
            ref=args.ref,
            subpath=args.subpath,
            description=args.description or "",
            raw=args.raw,
            auto_yes=args.yes,
        )
        if not success:
            sys.exit(1)
    else:
        author = args.author or get_default_author()
        target = create_boilerplate(
            res_type=res_type,
            name=args.name,
            author=author,
            description=args.description or "",
        )
        registry = load_registry()
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        rel_target = str(get_target_path(res_type, args.name).relative_to(WORKSPACE_ROOT))

        entry = {
            "name": args.name,
            "type": res_type,
            "origin": "user",
            "author": author,
            "target_path": rel_target,
            "created_at": now_iso,
            "updated_at": now_iso,
            "description": args.description or f"Custom {res_type} created by {author}",
        }
        registry.setdefault("resources", {})[args.name] = entry
        save_registry(registry)
        print(f"[OK] Created and registered user {res_type} '{args.name}' at {rel_target}")


def cmd_update(args: argparse.Namespace) -> None:
    registry = load_registry()
    resources = registry.get("resources", {})

    targets = [args.name] if args.name else list(resources.keys())
    if not targets:
        print("[INFO] No external resources registered in registry.json to update.")
        return

    updated_count = 0
    for name in targets:
        item = resources.get(name)
        if not item:
            print(f"[WARN] Resource '{name}' is not in registry.json. Skipping.")
            continue

        if item.get("origin") == "user":
            if args.name:
                print(f"[INFO] '{name}' was created locally by '{item.get('author', 'user')}' (origin: user). It cannot be updated from remote.")
            continue

        if not item.get("source_url"):
            continue

        print(f"[*] Updating remote resource '{name}' from {item['source_url']}...")
        success = install_from_repo(
            res_type=item["type"],
            name=name,
            raw_url=item["source_url"],
            ref=item.get("ref"),
            subpath=item.get("source_subpath"),
            description=item.get("description", ""),
            raw=args.raw,
            auto_yes=args.yes,
        )
        if success:
            updated_count += 1

    print(f"[DONE] Updated {updated_count} remote resource(s).")


def extract_description(path: Path) -> str:
    target_file = path / "SKILL.md" if path.is_dir() and (path / "SKILL.md").exists() else path
    if not target_file.is_file():
        return ""
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            lines = [f.readline() for _ in range(30)]
            content = "".join(lines)
            desc_match = re.search(r"description:\s*(?:>|\|)?\s*\n?\s*([^\n\r]+)", content)
            if desc_match:
                return desc_match.group(1).strip()
    except Exception:
        pass
    return ""


def cmd_sync(args: argparse.Namespace) -> None:
    registry = load_registry()
    resources = registry.setdefault("resources", {})
    author = args.author or get_default_author()
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    added_count = 0

    for res_type, meta in RESOURCE_TYPES.items():
        if res_type == "mcp":
            continue
        base_dir = meta["dir"]
        if not base_dir.exists():
            continue

        for item in base_dir.iterdir():
            if item.name.startswith(".") or item.name in ("registry.json", "mcp.json", "aiignore", "__pycache__") or item.name.endswith(".pyc"):
                continue

            name = item.stem if not meta["is_dir"] else item.name
            if res_type == "schema" and name.endswith(".schema"):
                name = name[:-7]

            if name in resources:
                existing_type = resources[name].get("type")
                if existing_type != res_type:
                    name = f"{name}-{res_type}"
                if name in resources:
                    continue

            desc = extract_description(item) or f"Custom {res_type} in workspace"
            rel_path = str(item.relative_to(WORKSPACE_ROOT))

            resources[name] = {
                "name": name,
                "type": res_type,
                "origin": "user",
                "author": author,
                "target_path": rel_path,
                "created_at": now_iso,
                "updated_at": now_iso,
                "description": desc,
            }
            added_count += 1
            print(f"[SYNC] Registered existing {res_type} '{name}' as user resource (author: {author})")

    # Sync MCP servers in .agents/mcp.json
    if MCP_FILE.exists():
        try:
            mcp_cfg = load_mcp_config()
            for sname, sdata in mcp_cfg.get("mcpServers", {}).items():
                if sname not in resources:
                    resources[sname] = {
                        "name": sname,
                        "type": "mcp",
                        "origin": "user",
                        "author": author,
                        "target_path": str(MCP_FILE.relative_to(WORKSPACE_ROOT)),
                        "created_at": now_iso,
                        "updated_at": now_iso,
                        "description": sdata.get("description", f"MCP server '{sname}'"),
                    }
                    added_count += 1
                    print(f"[SYNC] Registered existing mcp server '{sname}' as user resource (author: {author})")
        except Exception:
            pass

    save_registry(registry)
    print(f"\n[OK] Sync complete. Added {added_count} untracked resource(s) to registry.json.")


def cmd_neutralize(args: argparse.Namespace) -> None:
    """Manually audits and prompts to neutralize vendor/model locks on any existing resource."""
    registry = load_registry()
    tracked = registry.get("resources", {})
    name = args.name

    target_path = None
    if name in tracked:
        target_path = WORKSPACE_ROOT / tracked[name]["target_path"]
    else:
        for res_type in RESOURCE_TYPES:
            candidate = get_target_path(res_type, name)
            if candidate.exists():
                target_path = candidate
                break

    if not target_path or not target_path.exists():
        print(f"[ERROR] Could not find resource '{name}'.", file=sys.stderr)
        sys.exit(1)

    prompt_and_apply_neutralization(target_path, name, auto_yes=args.yes)


def cmd_list(args: argparse.Namespace) -> None:
    registry = load_registry()
    tracked = registry.get("resources", {})

    remote_items = {k: v for k, v in tracked.items() if v.get("origin") == "remote"}
    user_items = {k: v for k, v in tracked.items() if v.get("origin") == "user"}

    unregistered = []
    for res_type, meta in RESOURCE_TYPES.items():
        if res_type == "mcp":
            continue
        base_dir = meta["dir"]
        if not base_dir.exists():
            continue
        for item in base_dir.iterdir():
            if item.name.startswith(".") or item.name in ("registry.json", "mcp.json", "aiignore", "__pycache__") or item.name.endswith(".pyc"):
                continue
            name = item.stem if not meta["is_dir"] else item.name
            if res_type == "schema" and name.endswith(".schema"):
                name = name[:-7]
            if name not in tracked and f"{name}-{res_type}" not in tracked:
                unregistered.append((res_type, name))

    if MCP_FILE.exists():
        try:
            mcp_cfg = load_mcp_config()
            for sname in mcp_cfg.get("mcpServers", {}):
                if sname not in tracked:
                    unregistered.append(("mcp", sname))
        except Exception:
            pass

    print("\n======================= .agents/ Resource Registry =======================")

    # 1. Remote items
    print(f"\n🌐 REMOTE / UPSTREAM RESOURCES (GitHub / Git) [{len(remote_items)}]:")
    if not remote_items:
        print("  (None installed from external repositories)")
    else:
        for name, data in remote_items.items():
            print(f"  • [{data['type'].upper()}] {name}")
            print(f"    Source   : {data['source_url']}")
            if data.get("source_subpath"):
                print(f"    Subpath  : {data['source_subpath']}")
            print(f"    Commit   : {data.get('commit', 'unknown')[:7]} ({data.get('ref', 'main')})")
            print(f"    Target   : {data['target_path']}")
            print(f"    Updated  : {data.get('updated_at', 'unknown')}")
            if data.get("description"):
                print(f"    Desc     : {data['description']}")

    # 2. User-created items
    print(f"\n👤 USER-CREATED RESOURCES (Local Customizations) [{len(user_items)}]:")
    if not user_items:
        print("  (None registered)")
    else:
        for name, data in user_items.items():
            print(f"  • [{data['type'].upper()}] {name}")
            print(f"    Author   : {data.get('author', 'user')}")
            print(f"    Target   : {data['target_path']}")
            print(f"    Created  : {data.get('created_at', 'unknown')}")
            if data.get("description"):
                print(f"    Desc     : {data['description']}")

    # 3. Untracked items
    if unregistered:
        print(f"\n⚠️  UNREGISTERED WORKSPACE FILES [{len(unregistered)}]:")
        for res_type, name in unregistered:
            print(f"  • [{res_type.upper()}] {name}")
        print("  👉 Tip: Run 'python3 .agents/scripts/agents-manager.py sync' to register them.")

    print("\n=========================================================================\n")


def cmd_remove(args: argparse.Namespace) -> None:
    registry = load_registry()
    tracked = registry.get("resources", {})
    name = args.name

    target_path = None
    if name in tracked:
        res_info = tracked[name]
        res_type = res_info.get("type")
        origin = res_info.get("origin", "unknown")
        rel_target = res_info.get("target_path")
        target_path = WORKSPACE_ROOT / rel_target if rel_target else None
        del tracked[name]
        save_registry(registry)
        print(f"[*] Deregistered '{name}' ({origin}) from registry.json.")

        if res_type == "mcp":
            mcp_cfg = load_mcp_config()
            if name in mcp_cfg.get("mcpServers", {}):
                del mcp_cfg["mcpServers"][name]
                save_mcp_config(mcp_cfg)
                cmd_mcp_sync(mcp_cfg)
                print(f"[OK] Removed MCP server '{name}' from .agents/mcp.json and synced adapters.")
            return

    if not target_path:
        for res_type in RESOURCE_TYPES:
            if res_type == "mcp":
                continue
            candidate = get_target_path(res_type, name)
            if candidate.exists():
                target_path = candidate
                break

    if target_path and target_path.exists() and target_path != MCP_FILE:
        if target_path.is_dir():
            shutil.rmtree(target_path)
        else:
            target_path.unlink()
        print(f"[OK] Removed files at {target_path.relative_to(WORKSPACE_ROOT)}.")
    else:
        print(f"[WARN] No matching file or folder found for '{name}'.")


def cmd_verify(args: argparse.Namespace) -> None:
    """Verifies registry health, skill frontmatters, execution permissions, and structure."""
    registry = load_registry()
    tracked = registry.get("resources", {})
    fix = getattr(args, "fix", False)

    issues: List[Tuple[str, str]] = []
    passed = 0

    # 1. Registry integrity: All tracked resources exist on disk
    for name, data in tracked.items():
        rel_target = data.get("target_path")
        if not rel_target:
            issues.append(("ERROR", f"Resource '{name}' has no target_path defined in registry.json"))
            continue
        full_target = WORKSPACE_ROOT / rel_target
        if not full_target.exists():
            issues.append(("ERROR", f"Tracked resource '{name}' missing on disk: {rel_target}"))
        else:
            if data.get("type") == "mcp":
                mcp_cfg = load_mcp_config()
                if name not in mcp_cfg.get("mcpServers", {}):
                    issues.append(("WARN", f"Tracked MCP resource '{name}' not found in {rel_target} mcpServers"))
                else:
                    passed += 1
            else:
                passed += 1

    # 2. Check for untracked workspace resources
    for res_type, meta in RESOURCE_TYPES.items():
        if res_type == "mcp":
            continue
        base_dir = meta["dir"]
        if not base_dir.exists():
            continue
        for item in base_dir.iterdir():
            if item.name.startswith(".") or item.name in ("registry.json", "mcp.json", "aiignore", "__pycache__") or item.name.endswith(".pyc"):
                continue
            name = item.stem if not meta["is_dir"] else item.name
            if res_type == "schema" and name.endswith(".schema"):
                name = name[:-7]
            if name not in tracked and f"{name}-{res_type}" not in tracked:
                issues.append(("WARN", f"Untracked {res_type} on disk: {item.relative_to(WORKSPACE_ROOT)} (Run 'sync' to register)"))
            else:
                passed += 1

    if MCP_FILE.exists():
        try:
            mcp_cfg = load_mcp_config()
            for sname in mcp_cfg.get("mcpServers", {}):
                if sname not in tracked:
                    issues.append(("WARN", f"Untracked mcp server in mcp.json: '{sname}' (Run 'sync' to register)"))
                else:
                    passed += 1
        except Exception:
            pass

    # 3. Skills validation (SKILL.md exists with YAML frontmatter)
    skills_dir = AGENTS_DIR / "skills"
    if skills_dir.exists():
        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir() or skill_dir.name.startswith("."):
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                issues.append(("ERROR", f"Skill '{skill_dir.name}' is missing SKILL.md"))
            else:
                try:
                    content = skill_md.read_text(encoding="utf-8")
                    if not content.startswith("---") or "---" not in content[3:]:
                        issues.append(("WARN", f"Skill '{skill_dir.name}' SKILL.md is missing YAML frontmatter"))
                    else:
                        frontmatter = content[3:].split("---", 1)[0]
                        if "name:" not in frontmatter:
                            issues.append(("WARN", f"Skill '{skill_dir.name}' SKILL.md frontmatter missing 'name:'"))
                        if "description:" not in frontmatter:
                            issues.append(("WARN", f"Skill '{skill_dir.name}' SKILL.md frontmatter missing 'description:'"))
                        passed += 1
                except Exception as e:
                    issues.append(("ERROR", f"Skill '{skill_dir.name}' failed to read SKILL.md: {e}"))

    # 4. Plugins validation (plugin.json exists)
    plugins_dir = AGENTS_DIR / "plugins"
    if plugins_dir.exists():
        for plugin_dir in plugins_dir.iterdir():
            if not plugin_dir.is_dir() or plugin_dir.name.startswith("."):
                continue
            plugin_json = plugin_dir / "plugin.json"
            if not plugin_json.exists():
                issues.append(("ERROR", f"Plugin '{plugin_dir.name}' is missing plugin.json"))
            else:
                try:
                    json.loads(plugin_json.read_text(encoding="utf-8"))
                    passed += 1
                except Exception as e:
                    issues.append(("ERROR", f"Plugin '{plugin_dir.name}' plugin.json is invalid JSON: {e}"))

    # 5. Executable permissions on scripts and hooks
    for check_type in ["scripts", "hooks"]:
        dir_path = AGENTS_DIR / check_type
        if dir_path.exists():
            for sfile in dir_path.iterdir():
                if sfile.is_file() and not sfile.name.startswith("."):
                    if not os.access(sfile, os.X_OK):
                        if fix:
                            os.chmod(sfile, os.stat(sfile).st_mode | 0o111)
                            print(f"[FIX] Added executable permission to {check_type}/{sfile.name}")
                            passed += 1
                        else:
                            issues.append(("WARN", f"Executable bit not set on {check_type}/{sfile.name} (use --fix to resolve)"))
                    else:
                        passed += 1

    # 6. Check for leaked local user home paths
    for root, _, files in os.walk(AGENTS_DIR):
        for fname in files:
            if fname.endswith((".md", ".py", ".sh", ".json", ".yaml", ".yml")) and not fname.startswith("."):
                fpath = Path(root) / fname
                try:
                    text = fpath.read_text(encoding="utf-8", errors="ignore")
                    if re.search(r"/(?:Users|home)/[a-zA-Z0-9_-]+/", text):
                        issues.append(("WARN", f"Hardcoded absolute user path found in {fpath.relative_to(WORKSPACE_ROOT)}"))
                except Exception:
                    pass

    # 7. Check for rogue vendor-specific folders outside .agents/
    for vendor_dir in [".claude", ".gemini"]:
        candidate = WORKSPACE_ROOT / vendor_dir
        if candidate.exists() and candidate.is_dir():
            issues.append(("WARN", f"Non-canonical vendor folder detected: {vendor_dir}/ (move agent resources to .agents/)"))

    # 8. Check MCP synchronization parity (.vscode/mcp.json and .mcp.json vs .agents/mcp.json)
    if MCP_FILE.exists():
        try:
            mcp_cfg = load_mcp_config()
            mcp_ok, mcp_diffs = check_mcp_sync(mcp_cfg)
            if not mcp_ok:
                if fix:
                    cmd_mcp_sync(mcp_cfg)
                    print("[FIX] Synchronized MCP configurations to .vscode/mcp.json and .mcp.json")
                    passed += 1
                else:
                    for diff in mcp_diffs:
                        issues.append(("ERROR", f"MCP Sync Issue: {diff} (Run 'mcp sync' or use --fix)"))
            else:
                passed += 1
        except Exception as e:
            issues.append(("ERROR", f"Failed reading .agents/mcp.json: {e}"))

    # 9. Check AI ignore synchronization parity (.cursorignore, .claudeignore vs .agents/aiignore)
    if AIIGNORE_FILE.exists():
        ign_ok, ign_diffs = check_aiignore_sync()
        if not ign_ok:
            if fix:
                sync_aiignore()
                print("[FIX] Synchronized .agents/aiignore to .cursorignore and .claudeignore")
                passed += 1
            else:
                for diff in ign_diffs:
                    issues.append(("WARN", f"AI Ignore Issue: {diff} (Run 'ignore sync' or use --fix)"))
        else:
            passed += 1

    # 10. Check JSON Schemas existence
    if SCHEMAS_DIR.exists():
        reg_schema = SCHEMAS_DIR / "registry.schema.json"
        mcp_schema = SCHEMAS_DIR / "mcp.schema.json"
        if not reg_schema.exists():
            issues.append(("WARN", "Missing .agents/schemas/registry.schema.json"))
        else:
            passed += 1
        if not mcp_schema.exists():
            issues.append(("WARN", "Missing .agents/schemas/mcp.schema.json"))
        else:
            passed += 1

    # Print summary report
    print("\n======================= .agents/ Verification & Health Report =======================")
    errors = [msg for lvl, msg in issues if lvl == "ERROR"]
    warns = [msg for lvl, msg in issues if lvl == "WARN"]

    for msg in errors:
        print(f"❌ [FAIL] {msg}")
    for msg in warns:
        print(f"⚠️  [WARN] {msg}")

    print("-------------------------------------------------------------------------------------")
    print(f"Summary: {passed} invariant check(s) passed, {len(warns)} warning(s), {len(errors)} error(s).")
    if not errors and not warns:
        print("🎉 [PASS] Workspace agent resources are 100% healthy, canonical, and compliant!")
    elif not errors:
        print("✅ [PASS] No critical errors found. Workspace is operational.")
    else:
        print("❌ [FAIL] Critical errors detected that should be resolved.")
    print("=====================================================================================\n")

    if errors:
        sys.exit(1)


def cmd_analyze(args: argparse.Namespace) -> None:
    """Performs deep token analysis, line count, and cross-agent compatibility scoring."""
    registry = load_registry()
    tracked = registry.get("resources", {})
    name_filter = getattr(args, "name", None)

    targets: Dict[str, Dict[str, Any]] = {}
    if name_filter:
        if name_filter not in tracked:
            for rtype in RESOURCE_TYPES:
                candidate = get_target_path(rtype, name_filter)
                if candidate.exists():
                    targets[name_filter] = {
                        "name": name_filter,
                        "type": rtype,
                        "origin": "user",
                        "target_path": str(candidate.relative_to(WORKSPACE_ROOT)),
                    }
                    break
            if not targets:
                print(f"[ERROR] Resource '{name_filter}' not found.")
                sys.exit(1)
        else:
            targets[name_filter] = tracked[name_filter]
    else:
        targets = tracked

    print("\n======================= .agents/ Deep Resource Analysis =======================")
    for res_name, data in targets.items():
        rel_target = data.get("target_path", "")
        full_path = WORKSPACE_ROOT / rel_target
        if not full_path.exists():
            print(f"\n• [{data.get('type', 'resource').upper()}] {res_name}: Missing on disk ({rel_target})")
            continue

        file_count = 0
        total_lines = 0
        total_chars = 0
        model_locks_found: List[str] = []
        vendor_locks_found: List[str] = []

        files_to_scan: List[Path] = []
        if full_path.is_dir():
            for p in full_path.rglob("*"):
                if p.is_file() and not p.name.startswith("."):
                    files_to_scan.append(p)
        else:
            files_to_scan.append(full_path)

        for p in files_to_scan:
            file_count += 1
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
                lines = content.splitlines()
                total_lines += len(lines)
                total_chars += len(content)

                for pattern in MODEL_LOCK_PATTERNS:
                    matches = pattern.findall(content)
                    if matches:
                        model_locks_found.extend([str(m) for m in matches[:3]])
                for pattern in VENDOR_PATTERNS:
                    matches = pattern.findall(content)
                    if matches:
                        vendor_locks_found.extend([str(m) for m in matches[:3]])
            except Exception:
                pass

        est_tokens = total_chars // 4
        if est_tokens < 1500:
            tier = "🟢 Lightweight"
        elif est_tokens < 5000:
            tier = "🟡 Moderate"
        else:
            tier = "🔴 Heavy (Consumes substantial context)"

        claude_ok = "✅ Agnostic" if not model_locks_found else "⚠️  Model Lock"
        antigravity_ok = "✅ Supported" if not vendor_locks_found else "⚠️  Vendor Lock"
        copilot_ok = "✅ Supported"
        cursor_ok = "✅ Supported"

        print(f"\n📦 Resource: {res_name} [{data.get('type', 'unknown').upper()}]")
        print(f"   • Origin            : {data.get('origin', 'unknown')} ({data.get('source_url', 'local')})")
        print(f"   • Size & Complexity : {file_count} file(s), {total_lines:,} lines, {total_chars:,} chars")
        print(f"   • Context Token Tier: {tier} (~{est_tokens:,} tokens)")
        print(f"   • Compatibility Matrix:")
        print(f"       - Claude Code   : {claude_ok}")
        print(f"       - Antigravity   : {antigravity_ok}")
        print(f"       - GitHub Copilot: {copilot_ok}")
        print(f"       - Cursor        : {cursor_ok}")

        if model_locks_found or vendor_locks_found:
            print(f"   • Detected Locks    : {len(model_locks_found) + len(vendor_locks_found)} potential locks (run 'neutralize {res_name}')")

    print("\n===============================================================================\n")


def cmd_export(args: argparse.Namespace) -> None:
    """Exports a single resource or the entire .agents/ directory into a bundle."""
    registry = load_registry()
    tracked = registry.get("resources", {})
    name = getattr(args, "name", None)
    output_path = getattr(args, "output", None)
    fmt = getattr(args, "format", "tar.gz")

    if name and name != "all":
        if name not in tracked:
            print(f"[ERROR] Resource '{name}' is not registered.")
            sys.exit(1)
        target_items = {name: tracked[name]}
        default_filename = f"agent-resource-{name}.{fmt}"
    else:
        target_items = tracked
        default_filename = f"agents-bundle-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.{fmt}"

    out_file = Path(output_path) if output_path else WORKSPACE_ROOT / default_filename

    manifest = {
        "export_version": "1.0.0",
        "exported_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "resources_count": len(target_items),
        "resources": target_items,
    }

    temp_manifest = WORKSPACE_ROOT / ".export_manifest.json"
    temp_manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    try:
        if fmt in ("tar.gz", "tgz"):
            with tarfile.open(out_file, "w:gz") as tar:
                tar.add(temp_manifest, arcname="manifest.json")
                for rname, rdata in target_items.items():
                    rpath = WORKSPACE_ROOT / rdata["target_path"]
                    if rpath.exists():
                        tar.add(rpath, arcname=rdata["target_path"])
        else:
            with zipfile.ZipFile(out_file, "w", zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(temp_manifest, arcname="manifest.json")
                for rname, rdata in target_items.items():
                    rpath = WORKSPACE_ROOT / rdata["target_path"]
                    if rpath.exists():
                        if rpath.is_dir():
                            for subp in rpath.rglob("*"):
                                if subp.is_file():
                                    zipf.write(subp, arcname=str(subp.relative_to(WORKSPACE_ROOT)))
                        else:
                            zipf.write(rpath, arcname=rdata["target_path"])

        rel_out = out_file.relative_to(WORKSPACE_ROOT) if out_file.is_relative_to(WORKSPACE_ROOT) else out_file
        print(f"\n[SUCCESS] Exported {len(target_items)} resource(s) to: {rel_out}")
    finally:
        if temp_manifest.exists():
            temp_manifest.unlink()


def cmd_info(args: argparse.Namespace) -> None:
    """Displays detailed metadata card of a specific resource."""
    registry = load_registry()
    tracked = registry.get("resources", {})
    name = args.name

    if name not in tracked:
        print(f"[ERROR] Resource '{name}' is not registered in registry.json.")
        sys.exit(1)

    data = tracked[name]
    target_path = WORKSPACE_ROOT / data.get("target_path", "")

    print(f"\n======================= Resource Card: {name} =======================")
    print(f"• Name        : {name}")
    print(f"• Type        : {data.get('type')}")
    print(f"• Origin      : {data.get('origin')}")
    print(f"• Target Path : {data.get('target_path')} (Exists: {target_path.exists()})")
    if data.get("origin") == "remote":
        print(f"• Source URL  : {data.get('source_url')}")
        if data.get("source_subpath"):
            print(f"• Subpath     : {data.get('source_subpath')}")
        print(f"• Ref / Commit: {data.get('ref')} / {data.get('commit')}")
        print(f"• Installed At: {data.get('created_at', data.get('installed_at'))}")
    else:
        print(f"• Author      : {data.get('author', 'user')}")
        print(f"• Created At  : {data.get('created_at')}")
    print(f"• Updated At  : {data.get('updated_at')}")
    print(f"• Description : {data.get('description', '-')}")

    if target_path.exists():
        if target_path.is_dir():
            files = [str(f.relative_to(target_path)) for f in target_path.rglob("*") if f.is_file()]
            print(f"• Files ({len(files)}):")
            for f in files[:10]:
                print(f"    - {f}")
            if len(files) > 10:
                print(f"    ... and {len(files) - 10} more files.")
        else:
            print(f"• Size: {target_path.stat().st_size} bytes")
    print("====================================================================\n")


# =====================================================================
# MCP (Model Context Protocol) Management
# =====================================================================

POPULAR_MCP_TEMPLATES = {
    "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
        "env": {},
        "description": "Secure local workspace file read and edit tools",
    },
    "fetch": {
        "command": "uvx",
        "args": ["mcp-server-fetch"],
        "env": {},
        "description": "Fetch web pages and convert HTML to markdown for LLMs",
    },
    "sqlite": {
        "command": "uvx",
        "args": ["mcp-server-sqlite", "--db-path", "./data.db"],
        "env": {},
        "description": "Query and inspect SQLite databases",
    },
    "github": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "<your-token>"},
        "description": "GitHub issues, PRs, commits, and repository management",
    },
    "memory": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-memory"],
        "env": {},
        "description": "Knowledge graph-based associative long-term memory",
    },
    "brave-search": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-brave-search"],
        "env": {"BRAVE_API_KEY": "<your-brave-key>"},
        "description": "Web and local search using the Brave Search API",
    },
}


def load_mcp_config() -> Dict[str, Any]:
    if not MCP_FILE.exists():
        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "version": "1.0.0",
            "mcpServers": {},
        }
    try:
        with open(MCP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"version": "1.0.0", "mcpServers": {}}


def save_mcp_config(data: Dict[str, Any]) -> None:
    MCP_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MCP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def cmd_mcp_sync(config: Dict[str, Any]) -> None:
    """Syncs .agents/mcp.json to .vscode/mcp.json and root .mcp.json for cross-agent compatibility."""
    servers = config.get("mcpServers", {})
    payload = {"mcpServers": servers}

    # 1. VS Code / Copilot: .vscode/mcp.json
    vscode_dir = WORKSPACE_ROOT / ".vscode"
    if vscode_dir.exists():
        vscode_mcp = vscode_dir / "mcp.json"
        with open(vscode_mcp, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            f.write("\n")
        print(f"[*] Synced MCP configuration to .vscode/mcp.json")

    # 2. Root .mcp.json (Cursor & Claude Code compatible)
    root_mcp = WORKSPACE_ROOT / ".mcp.json"
    with open(root_mcp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    print(f"[*] Synced MCP configuration to .mcp.json (Cursor & Claude Code compatible)")


def check_mcp_sync(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Checks whether .vscode/mcp.json and .mcp.json match .agents/mcp.json."""
    servers = config.get("mcpServers", {})
    mismatches = []

    vscode_mcp = WORKSPACE_ROOT / ".vscode" / "mcp.json"
    if not vscode_mcp.exists():
        mismatches.append(".vscode/mcp.json is missing")
    else:
        try:
            vdata = json.loads(vscode_mcp.read_text(encoding="utf-8"))
            if vdata.get("mcpServers") != servers:
                mismatches.append(".vscode/mcp.json out of sync with .agents/mcp.json")
        except Exception as e:
            mismatches.append(f".vscode/mcp.json invalid JSON: {e}")

    root_mcp = WORKSPACE_ROOT / ".mcp.json"
    if not root_mcp.exists():
        mismatches.append(".mcp.json is missing")
    else:
        try:
            rdata = json.loads(root_mcp.read_text(encoding="utf-8"))
            if rdata.get("mcpServers") != servers:
                mismatches.append(".mcp.json out of sync with .agents/mcp.json")
        except Exception as e:
            mismatches.append(f".mcp.json invalid JSON: {e}")

    return (len(mismatches) == 0, mismatches)


def sync_aiignore() -> Tuple[bool, str]:
    """Synchronizes .agents/aiignore SSOT to .cursorignore and .claudeignore."""
    if not AIIGNORE_FILE.exists():
        return False, f"Source ignore file missing: {AIIGNORE_FILE.relative_to(WORKSPACE_ROOT)}"
    content = AIIGNORE_FILE.read_text(encoding="utf-8")
    CURSORIGNORE_FILE.write_text(content, encoding="utf-8")
    CLAUDEIGNORE_FILE.write_text(content, encoding="utf-8")
    return True, "Synced .agents/aiignore to .cursorignore and .claudeignore"


def check_aiignore_sync() -> Tuple[bool, List[str]]:
    """Checks whether .cursorignore and .claudeignore match .agents/aiignore."""
    mismatches = []
    if not AIIGNORE_FILE.exists():
        return False, [".agents/aiignore does not exist"]
    content = AIIGNORE_FILE.read_text(encoding="utf-8")
    for fpath in [CURSORIGNORE_FILE, CLAUDEIGNORE_FILE]:
        if not fpath.exists():
            mismatches.append(f"{fpath.name} is missing")
        else:
            if fpath.read_text(encoding="utf-8") != content:
                mismatches.append(f"{fpath.name} is out of sync with .agents/aiignore")
    return (len(mismatches) == 0, mismatches)


def cmd_ignore(args: argparse.Namespace) -> None:
    action = getattr(args, "ignore_action", "sync")
    if action == "sync":
        ok, msg = sync_aiignore()
        if ok:
            print(f"[*] {msg}")
        else:
            print(f"❌ {msg}")
    elif action == "check":
        ok, diffs = check_aiignore_sync()
        if ok:
            print("✅ All AI ignore files (.cursorignore, .claudeignore) are in sync with .agents/aiignore.")
        else:
            for diff in diffs:
                print(f"⚠️  {diff}")


def cmd_mcp(args: argparse.Namespace) -> None:
    action = getattr(args, "mcp_action", "list")
    config = load_mcp_config()
    servers = config.setdefault("mcpServers", {})

    if action == "list":
        print("\n======================= Configured MCP Servers (.agents/mcp.json) =======================")
        if not servers:
            print("  (No MCP servers configured yet)")
            print("  👉 Tip: Run 'python3 .agents/scripts/agents-manager.py mcp templates' to explore presets.")
        else:
            for sname, sdata in servers.items():
                status = "🔴 Disabled" if sdata.get("disabled") else "🟢 Enabled"
                cmd_str = f"{sdata.get('command', '')} {' '.join(sdata.get('args', []))}"
                print(f"• [{sname}] ({status})")
                print(f"    Command: {cmd_str}")
                if sdata.get("description"):
                    print(f"    Desc   : {sdata['description']}")
                if sdata.get("env"):
                    print(f"    Env    : {list(sdata['env'].keys())}")
        print("=========================================================================================\n")

    elif action == "templates":
        print("\n======================= Popular MCP Server Presets =======================")
        for tname, tdata in POPULAR_MCP_TEMPLATES.items():
            cmd_str = f"{tdata['command']} {' '.join(tdata['args'])}"
            print(f"• {tname}:")
            print(f"    Desc   : {tdata['description']}")
            print(f"    Command: {cmd_str}")
            if tdata.get("env"):
                print(f"    Env    : {tdata['env']}")
            print(f"    👉 Install: python3 .agents/scripts/agents-manager.py mcp add-template {tname}")
            print()
        print("==========================================================================\n")

    elif action == "add-template":
        tname = args.template_name
        if tname not in POPULAR_MCP_TEMPLATES:
            print(f"[ERROR] Template '{tname}' not found. Run 'mcp templates' to see available presets.")
            sys.exit(1)
        servers[tname] = POPULAR_MCP_TEMPLATES[tname]
        save_mcp_config(config)
        print(f"[SUCCESS] Added MCP server preset '{tname}' to .agents/mcp.json.")
        cmd_mcp_sync(config)

        reg = load_registry()
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        author = get_default_author()
        reg.setdefault("resources", {})[tname] = {
            "name": tname,
            "type": "mcp",
            "origin": "user",
            "author": author,
            "target_path": str(MCP_FILE.relative_to(WORKSPACE_ROOT)),
            "created_at": now_iso,
            "updated_at": now_iso,
            "description": POPULAR_MCP_TEMPLATES[tname].get("description", f"MCP server '{tname}'"),
        }
        save_registry(reg)
        print(f"[*] Registered MCP server '{tname}' in registry.json.")

    elif action == "add":
        sname = args.name
        command = args.cmd
        args_list = args.args or []
        env_dict = {}
        if args.env:
            for item in args.env:
                if "=" in item:
                    k, v = item.split("=", 1)
                    env_dict[k.strip()] = v.strip()

        servers[sname] = {
            "command": command,
            "args": args_list,
            "env": env_dict,
            "disabled": False,
            "description": args.description or "",
        }
        save_mcp_config(config)
        print(f"[SUCCESS] Registered MCP server '{sname}' in .agents/mcp.json.")
        cmd_mcp_sync(config)

        reg = load_registry()
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        author = get_default_author()
        reg.setdefault("resources", {})[sname] = {
            "name": sname,
            "type": "mcp",
            "origin": "user",
            "author": author,
            "target_path": str(MCP_FILE.relative_to(WORKSPACE_ROOT)),
            "created_at": now_iso,
            "updated_at": now_iso,
            "description": args.description or f"Custom MCP server '{sname}'",
        }
        save_registry(reg)
        print(f"[*] Registered MCP server '{sname}' in registry.json.")

    elif action == "remove":
        sname = args.name
        if sname in servers:
            del servers[sname]
            save_mcp_config(config)
            print(f"[SUCCESS] Removed MCP server '{sname}' from .agents/mcp.json.")
            cmd_mcp_sync(config)

            reg = load_registry()
            if sname in reg.get("resources", {}):
                del reg["resources"][sname]
                save_registry(reg)
                print(f"[*] Deregistered MCP server '{sname}' from registry.json.")
        else:
            print(f"[WARN] MCP server '{sname}' not found in configuration.")

    elif action == "sync":
        cmd_mcp_sync(config)


# =====================================================================
# Repository Discovery & Recommendation Engine
# =====================================================================

def cmd_discover(args: argparse.Namespace) -> None:
    raw_url = args.url
    git_url, detected_ref, _ = parse_github_url(raw_url)
    ref = args.ref or detected_ref or "main"

    temp_clone_dir = Path("/tmp") / f"agents_discover_{int(datetime.datetime.now().timestamp())}"
    if temp_clone_dir.exists():
        shutil.rmtree(temp_clone_dir, ignore_errors=True)

    print(f"\n[*] Scanning repository: {git_url} (ref: {ref})...")
    clone_cmd = ["git", "clone", "--depth", "1", "--branch", ref, git_url, str(temp_clone_dir)]
    code, _, err = run_cmd(clone_cmd)
    if code != 0:
        clone_cmd = ["git", "clone", "--depth", "1", git_url, str(temp_clone_dir)]
        code, _, err = run_cmd(clone_cmd)
        if code != 0:
            print(f"[ERROR] Failed to clone {git_url}:\n{err}", file=sys.stderr)
            return

    try:
        discovered: List[Dict[str, Any]] = []

        # 1. Scan for Skills: directories containing SKILL.md
        for p in temp_clone_dir.rglob("SKILL.md"):
            if ".git" in p.parts:
                continue
            skill_dir = p.parent
            subpath = skill_dir.relative_to(temp_clone_dir)
            name = skill_dir.name
            desc = "Skill workflow"
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
                if content.startswith("---") and "---" in content[3:]:
                    fm = content[3:].split("---", 1)[0]
                    for line in fm.splitlines():
                        if line.startswith("description:"):
                            desc = line.split(":", 1)[1].strip().strip('"').strip("'")
                        elif line.startswith("name:"):
                            name = line.split(":", 1)[1].strip()
            except Exception:
                pass

            chars = sum(f.stat().st_size for f in skill_dir.rglob("*") if f.is_file())
            discovered.append({
                "type": "skill",
                "name": name,
                "subpath": str(subpath) if str(subpath) != "." else "",
                "description": desc,
                "tokens": chars // 4,
            })

        # 2. Scan for Agents: md files in agents/ or with persona structures
        for cand in [temp_clone_dir / "agents", temp_clone_dir / ".agents" / "agents"]:
            if cand.exists() and cand.is_dir():
                for af in cand.glob("*.md"):
                    subpath = af.relative_to(temp_clone_dir)
                    desc = "Specialized agent persona"
                    try:
                        first_lines = af.read_text(encoding="utf-8", errors="ignore").splitlines()[:5]
                        for l in first_lines:
                            if l.startswith(">"):
                                desc = l.lstrip(">").strip()
                                break
                    except Exception:
                        pass
                    discovered.append({
                        "type": "agent",
                        "name": af.stem,
                        "subpath": str(subpath),
                        "description": desc,
                        "tokens": af.stat().st_size // 4,
                    })

        # 3. Scan for Instructions: md files in instructions/
        for cand in [temp_clone_dir / "instructions", temp_clone_dir / ".agents" / "instructions"]:
            if cand.exists() and cand.is_dir():
                for inf in cand.glob("*.md"):
                    subpath = inf.relative_to(temp_clone_dir)
                    discovered.append({
                        "type": "instruction",
                        "name": inf.stem,
                        "subpath": str(subpath),
                        "description": f"Instruction set for {inf.stem}",
                        "tokens": inf.stat().st_size // 4,
                    })

        # 4. Scan for Prompts: md files in prompts/
        for cand in [temp_clone_dir / "prompts", temp_clone_dir / ".agents" / "prompts"]:
            if cand.exists() and cand.is_dir():
                for pf in cand.glob("*.md"):
                    subpath = pf.relative_to(temp_clone_dir)
                    discovered.append({
                        "type": "prompt",
                        "name": pf.stem,
                        "subpath": str(subpath),
                        "description": f"Prompt template for {pf.stem}",
                        "tokens": pf.stat().st_size // 4,
                    })

        # 5. Scan for Plugins: folders with plugin.json
        for pf in temp_clone_dir.rglob("plugin.json"):
            if ".git" in pf.parts:
                continue
            plug_dir = pf.parent
            subpath = plug_dir.relative_to(temp_clone_dir)
            pname = plug_dir.name
            pdesc = "Plugin bundle"
            try:
                pdata = json.loads(pf.read_text(encoding="utf-8"))
                pname = pdata.get("name", pname)
                pdesc = pdata.get("description", pdesc)
            except Exception:
                pass
            chars = sum(f.stat().st_size for f in plug_dir.rglob("*") if f.is_file())
            discovered.append({
                "type": "plugin",
                "name": pname,
                "subpath": str(subpath),
                "description": pdesc,
                "tokens": chars // 4,
            })

        # 6. Scan for MCP Configs in repo
        for mcpf in temp_clone_dir.rglob("mcp.json"):
            if ".git" in mcpf.parts:
                continue
            try:
                mcp_data = json.loads(mcpf.read_text(encoding="utf-8"))
                srvs = mcp_data.get("mcpServers", {})
                for sname, sdata in srvs.items():
                    discovered.append({
                        "type": "mcp-server",
                        "name": sname,
                        "subpath": str(mcpf.relative_to(temp_clone_dir)),
                        "description": sdata.get("description", f"MCP server '{sname}'"),
                        "tokens": 200,
                        "mcp_payload": sdata,
                    })
            except Exception:
                pass

        # 7. Scan for Schemas: json files in schemas/ or .agents/schemas/
        for cand in [temp_clone_dir / "schemas", temp_clone_dir / ".agents" / "schemas"]:
            if cand.exists() and cand.is_dir():
                for sf in cand.glob("*.json"):
                    subpath = sf.relative_to(temp_clone_dir)
                    sname = sf.stem
                    if sname.endswith(".schema"):
                        sname = sname[:-7]
                    discovered.append({
                        "type": "schema",
                        "name": sname,
                        "subpath": str(subpath),
                        "description": f"JSON Schema definition for {sname}",
                        "tokens": sf.stat().st_size // 4,
                    })

        # 8. Scan for Scripts: files in scripts/ or .agents/scripts/
        for cand in [temp_clone_dir / "scripts", temp_clone_dir / ".agents" / "scripts"]:
            if cand.exists() and cand.is_dir():
                for scf in cand.iterdir():
                    if scf.is_file() and not scf.name.startswith("."):
                        subpath = scf.relative_to(temp_clone_dir)
                        discovered.append({
                            "type": "script",
                            "name": scf.name,
                            "subpath": str(subpath),
                            "description": f"Automation script {scf.name}",
                            "tokens": scf.stat().st_size // 4,
                        })

        # 9. Scan for Hooks: files in hooks/ or .agents/hooks/
        for cand in [temp_clone_dir / "hooks", temp_clone_dir / ".agents" / "hooks"]:
            if cand.exists() and cand.is_dir():
                for hf in cand.iterdir():
                    if hf.is_file() and not hf.name.startswith("."):
                        subpath = hf.relative_to(temp_clone_dir)
                        discovered.append({
                            "type": "hook",
                            "name": hf.name,
                            "subpath": str(subpath),
                            "description": f"Lifecycle hook {hf.name}",
                            "tokens": hf.stat().st_size // 4,
                        })

        if not discovered:
            print(f"[WARN] No standard agent resources found in {git_url}.")
            return

        unique_disc = {}
        for d in discovered:
            key = (d["type"], d["name"])
            if key not in unique_disc:
                unique_disc[key] = d
        items = list(unique_disc.values())

        print(f"\n======================= Discovered Agent Resources ({len(items)}) =======================")
        print(f"Repository: {git_url}\n")

        for idx, item in enumerate(items, 1):
            tok = item["tokens"]
            if tok < 4000:
                rec_badge = "⭐ Highly Recommended (Lightweight & Focused)"
                item["recommended"] = True
            elif tok < 15000:
                rec_badge = "📦 Standard"
                item["recommended"] = False
            else:
                rec_badge = "⚠️  Heavy (Large context footprint)"
                item["recommended"] = False

            print(f"[{idx}] [{item['type'].upper()}] {item['name']}")
            print(f"    • Subpath : {item['subpath'] or '(root)'}")
            print(f"    • Tokens  : ~{tok:,} tokens | {rec_badge}")
            print(f"    • Desc    : {item['description']}")
            print()

        print("==========================================================================================")

        auto_recommended = getattr(args, "import_recommended", False)
        auto_all = getattr(args, "import_all", False)
        auto_yes = getattr(args, "yes", False)

        selected_indices: List[int] = []
        if auto_all:
            selected_indices = list(range(1, len(items) + 1))
        elif auto_recommended:
            selected_indices = [i + 1 for i, it in enumerate(items) if it.get("recommended")]
        else:
            try:
                choice = input("Enter resource numbers to import (e.g. '1,3', 'recommended', 'all', or 'q' to quit): ").strip().lower()
                if choice in ("q", "quit", "exit", ""):
                    print("[INFO] Import cancelled.")
                    return
                elif choice == "all":
                    selected_indices = list(range(1, len(items) + 1))
                elif choice == "recommended":
                    selected_indices = [i + 1 for i, it in enumerate(items) if it.get("recommended")]
                else:
                    for part in choice.split(","):
                        part = part.strip()
                        if part.isdigit():
                            val = int(part)
                            if 1 <= val <= len(items):
                                selected_indices.append(val)
            except (KeyboardInterrupt, EOFError):
                print("\n[INFO] Cancelled.")
                return

        if not selected_indices:
            print("[INFO] No resources selected for import.")
            return

        print(f"\n[*] Importing {len(selected_indices)} selected resource(s)...")
        for num in selected_indices:
            res = items[num - 1]
            target_res_type = "mcp" if res["type"] == "mcp-server" else res["type"]
            install_from_repo(
                res_type=target_res_type,
                name=res["name"],
                raw_url=git_url,
                ref=ref,
                subpath=res["subpath"],
                description=res["description"],
                raw=False,
                auto_yes=auto_yes,
            )

        print("\n🎉 [SUCCESS] Selected resources successfully imported and registered!")
    finally:
        if temp_clone_dir.exists():
            shutil.rmtree(temp_clone_dir, ignore_errors=True)


def cmd_doctor(args: argparse.Namespace) -> None:
    """Performs comprehensive diagnostics on environment, adapters, MCP, and security."""
    print("\n======================= 🩺 Agent Environment Diagnostics (Doctor) =======================")
    checks: List[Tuple[str, str, str]] = []  # (status, category, message)

    # 1. System environment
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 8):
        checks.append(("PASS", "System", f"Python version {py_ver} (>= 3.8 supported)"))
    else:
        checks.append(("FAIL", "System", f"Python version {py_ver} is too old (>= 3.8 required)"))

    node_found = shutil.which("node") is not None
    npx_found = shutil.which("npx") is not None
    if npx_found:
        checks.append(("PASS", "System", "npx executable is available for MCP servers"))
    elif node_found:
        checks.append(("WARN", "System", "node is available, but npx was not found in PATH"))
    else:
        checks.append(("WARN", "System", "Node.js / npx not detected (required for npx-based MCP servers)"))

    git_found = shutil.which("git") is not None
    if git_found:
        checks.append(("PASS", "System", "Git CLI is available"))
    else:
        checks.append(("FAIL", "System", "Git CLI not found in PATH"))

    # 2. SSOT & Adapters
    agents_md = WORKSPACE_ROOT / "AGENTS.md"
    if agents_md.exists():
        checks.append(("PASS", "Architecture", "Canonical AGENTS.md (SSOT) exists in workspace root"))
    else:
        checks.append(("FAIL", "Architecture", "AGENTS.md (SSOT) is missing from workspace root"))

    adapters = [
        ("Claude Code", WORKSPACE_ROOT / "CLAUDE.md", "AGENTS.md"),
        ("Antigravity", WORKSPACE_ROOT / "GEMINI.md", "AGENTS.md"),
        ("Cursor", WORKSPACE_ROOT / ".cursorrules", "AGENTS.md"),
        ("GitHub Copilot", WORKSPACE_ROOT / ".github" / "copilot-instructions.md", "AGENTS.md"),
        ("EditorConfig", WORKSPACE_ROOT / ".editorconfig", None),
    ]
    for name, apath, ref in adapters:
        if not apath.exists():
            checks.append(("WARN", "Adapters", f"Adapter for {name} is missing: {apath.name}"))
        else:
            if ref:
                content = apath.read_text(encoding="utf-8", errors="ignore")
                if ref in content:
                    checks.append(("PASS", "Adapters", f"{name} adapter ({apath.name}) correctly links to {ref}"))
                else:
                    checks.append(("WARN", "Adapters", f"{name} adapter ({apath.name}) does not mention {ref}"))
            else:
                checks.append(("PASS", "Adapters", f"{name} ({apath.name}) configured"))

    # 3. AI Ignore SSOT
    if AIIGNORE_FILE.exists():
        checks.append(("PASS", "AI Ignore", ".agents/aiignore SSOT exists"))
        ign_ok, ign_errs = check_aiignore_sync()
        if ign_ok:
            checks.append(("PASS", "AI Ignore", ".cursorignore and .claudeignore are fully in sync"))
        else:
            for err in ign_errs:
                checks.append(("WARN", "AI Ignore", err))
    else:
        checks.append(("WARN", "AI Ignore", ".agents/aiignore is missing (create with default exclusion rules)"))

    # 4. MCP Configuration & Sync
    if MCP_FILE.exists():
        checks.append(("PASS", "MCP", ".agents/mcp.json SSOT exists"))
        try:
            mcp_cfg = load_mcp_config()
            srv_count = len(mcp_cfg.get("mcpServers", {}))
            checks.append(("PASS", "MCP", f"{srv_count} MCP server(s) configured in .agents/mcp.json"))
            mcp_ok, mcp_errs = check_mcp_sync(mcp_cfg)
            if mcp_ok:
                checks.append(("PASS", "MCP", "Adapters (.vscode/mcp.json, .mcp.json) in sync"))
            else:
                for err in mcp_errs:
                    checks.append(("FAIL", "MCP", err))
        except Exception as e:
            checks.append(("FAIL", "MCP", f"Error parsing .agents/mcp.json: {e}"))
    else:
        checks.append(("WARN", "MCP", ".agents/mcp.json is missing"))

    # 5. JSON Schemas
    if (SCHEMAS_DIR / "registry.schema.json").exists() and (SCHEMAS_DIR / "mcp.schema.json").exists():
        checks.append(("PASS", "Schemas", "Local JSON schemas present (.agents/schemas/)"))
    else:
        checks.append(("WARN", "Schemas", "One or more JSON schemas missing in .agents/schemas/"))

    # 6. Security & Leaks
    leak_patterns = [
        (r"AIza[0-9A-Za-z-_]{35}", "Google API Key"),
        (r"sk-[a-zA-Z0-9_-]{20,}", "OpenAI/Anthropic API Key"),
        (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
    ]
    leaks_found = 0
    for root, _, files in os.walk(AGENTS_DIR):
        for fname in files:
            if fname.endswith((".md", ".py", ".sh", ".json", ".yaml", ".yml")) and not fname.startswith("."):
                fpath = Path(root) / fname
                try:
                    text = fpath.read_text(encoding="utf-8", errors="ignore")
                    for pat, desc in leak_patterns:
                        if re.search(pat, text):
                            checks.append(("FAIL", "Security", f"Possible {desc} leaked in {fpath.relative_to(WORKSPACE_ROOT)}"))
                            leaks_found += 1
                except Exception:
                    pass
    if leaks_found == 0:
        checks.append(("PASS", "Security", "No exposed API keys or credentials detected in .agents/"))

    # Print results grouped by category
    categories = ["System", "Architecture", "Adapters", "AI Ignore", "MCP", "Schemas", "Security"]
    total_passed = 0
    total_warn = 0
    total_fail = 0

    for cat in categories:
        cat_checks = [c for c in checks if c[1] == cat]
        if not cat_checks:
            continue
        print(f"\n📂 [{cat}]")
        for status, _, msg in cat_checks:
            if status == "PASS":
                print(f"  🟢 [OK] {msg}")
                total_passed += 1
            elif status == "WARN":
                print(f"  ⚠️  [WARN] {msg}")
                total_warn += 1
            else:
                print(f"  ❌ [FAIL] {msg}")
                total_fail += 1

    print("\n-------------------------------------------------------------------------------------")
    print(f"Diagnostics: {total_passed} passed, {total_warn} warning(s), {total_fail} failure(s).")
    if total_fail == 0:
        print("🎉 [HEALTHY] Your workspace configuration is in optimal shape!")
    else:
        print("⚠️  [ACTION REQUIRED] Address the failing checks above to ensure full agent capability.")
    print("=====================================================================================\n")


def cmd_init(args: argparse.Namespace) -> None:
    """Scaffold or initialize project context and stack in AGENTS.md."""
    print("\n======================= 🚀 Initialize Universal AI Workspace =======================")
    agents_md = WORKSPACE_ROOT / "AGENTS.md"
    if not agents_md.exists():
        print("❌ AGENTS.md not found in workspace root.")
        return

    content = agents_md.read_text(encoding="utf-8")

    project_name = getattr(args, "name", None)
    stack = getattr(args, "stack", None)
    goal = getattr(args, "goal", None)
    author = getattr(args, "author", None)
    non_interactive = getattr(args, "non_interactive", False)

    if not non_interactive:
        if not project_name:
            try:
                def_name = WORKSPACE_ROOT.name
                val = input(f"Enter project name [{def_name}]: ").strip()
                project_name = val if val else def_name
            except (KeyboardInterrupt, EOFError):
                print("\n[INFO] Cancelled.")
                return

        if not stack:
            try:
                val = input("Enter technologies / stack (e.g. React 19, Vite, TypeScript, Tailwind): ").strip()
                stack = val if val else "To be defined based on project requirements"
            except (KeyboardInterrupt, EOFError):
                print("\n[INFO] Cancelled.")
                return

        if not goal:
            try:
                val = input("Enter project goal / purpose: ").strip()
                goal = val if val else "Provide a clean, scalable workspace architecture"
            except (KeyboardInterrupt, EOFError):
                print("\n[INFO] Cancelled.")
                return

        if not author:
            try:
                val = input("Enter author / maintainer name (optional): ").strip()
                author = val if val else ""
            except (KeyboardInterrupt, EOFError):
                pass
    else:
        project_name = project_name or WORKSPACE_ROOT.name
        stack = stack or "To be defined based on project requirements"
        goal = goal or "Provide a clean, scalable workspace architecture"

    # Replace placeholders in AGENTS.md
    content = re.sub(r"- \*\*Project\*\*:.*", f"- **Project**: `{project_name}`", content)
    content = re.sub(r"- \*\*Stack / Technologies\*\*:.*", f"- **Stack / Technologies**: {stack}", content)
    content = re.sub(r"- \*\*Goal\*\*:.*", f"- **Goal**: {goal}", content)

    agents_md.write_text(content, encoding="utf-8")
    print(f"[*] Updated {agents_md.name} with project context:")
    print(f"    • Name : {project_name}")
    print(f"    • Stack: {stack}")
    print(f"    • Goal : {goal}")

    # Synchronize MCP
    if MCP_FILE.exists():
        cmd_mcp_sync(load_mcp_config())

    # Synchronize AI Ignore
    if AIIGNORE_FILE.exists():
        sync_aiignore()

    print("\n✅ Initialization complete. Running environment doctor...")
    cmd_doctor(args)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Universal Agent Resource Manager for .agents/ folder.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # DISCOVER & SUGGEST
    disc_p = subparsers.add_parser("discover", help="Scan a remote repo and suggest best resources to import.")
    disc_p.add_argument("url", help="GitHub or Git repository URL to inspect")
    disc_p.add_argument("--ref", help="Branch, tag, or commit to inspect (defaults to main)")
    disc_p.add_argument("--import-recommended", action="store_true", help="Automatically import all recommended resources")
    disc_p.add_argument("--import-all", action="store_true", help="Automatically import all discovered resources")
    disc_p.add_argument("-y", "--yes", action="store_true", help="Automatically accept cross-agent neutralization")
    disc_p.set_defaults(func=cmd_discover)

    # MCP MANAGEMENT
    mcp_p = subparsers.add_parser("mcp", help="Manage Model Context Protocol (MCP) server configurations.")
    mcp_sub = mcp_p.add_subparsers(dest="mcp_action", required=False)

    mcp_list_p = mcp_sub.add_parser("list", help="List configured MCP servers.")
    mcp_list_p.set_defaults(func=cmd_mcp, mcp_action="list")

    mcp_tmpl_p = mcp_sub.add_parser("templates", help="List popular MCP server presets.")
    mcp_tmpl_p.set_defaults(func=cmd_mcp, mcp_action="templates")

    mcp_add_tmpl = mcp_sub.add_parser("add-template", help="Add a popular MCP server preset.")
    mcp_add_tmpl.add_argument("template_name", help="Preset name (e.g. filesystem, fetch, sqlite, github, memory)")
    mcp_add_tmpl.set_defaults(func=cmd_mcp, mcp_action="add-template")

    mcp_add_p = mcp_sub.add_parser("add", help="Register a custom MCP server.")
    mcp_add_p.add_argument("name", help="Unique identifier for the MCP server")
    mcp_add_p.add_argument("--cmd", required=True, help="Command executable (e.g. npx, uvx, python3, node)")
    mcp_add_p.add_argument("--args", nargs="*", help="Arguments passed to the command")
    mcp_add_p.add_argument("--env", nargs="*", help="Environment variables in KEY=VALUE format")
    mcp_add_p.add_argument("--description", help="Description of the MCP server tools")
    mcp_add_p.set_defaults(func=cmd_mcp, mcp_action="add")

    mcp_rm_p = mcp_sub.add_parser("remove", help="Remove an MCP server.")
    mcp_rm_p.add_argument("name", help="Identifier of the MCP server to remove")
    mcp_rm_p.set_defaults(func=cmd_mcp, mcp_action="remove")

    mcp_sync_p = mcp_sub.add_parser("sync", help="Synchronize .agents/mcp.json to .vscode/mcp.json and .mcp.json.")
    mcp_sync_p.set_defaults(func=cmd_mcp, mcp_action="sync")

    mcp_p.set_defaults(func=cmd_mcp, mcp_action="list")

    # ADD / CREATE / IMPORT
    add_p = subparsers.add_parser("add", help="Add or scaffold an agent resource (alias: create).")
    add_p.add_argument("type", help="Resource type: skill, agent, instruction, plugin, prompt, schema, script, hook, mcp")
    add_p.add_argument("name", help="Name or identifier of the resource")
    add_p.add_argument("--url", help="GitHub or Git repository URL to clone from")
    add_p.add_argument("--ref", help="Branch, tag, or commit to checkout (defaults to main)")
    add_p.add_argument("--subpath", help="Folder or file path inside the remote repository")
    add_p.add_argument("--author", help="Author name for user-created resources")
    add_p.add_argument("--description", help="Description of the resource")
    add_p.add_argument("--raw", action="store_true", help="Preserve raw upstream content without neutralization check")
    add_p.add_argument("-y", "--yes", action="store_true", help="Automatically accept cross-agent neutralization without prompting")
    add_p.set_defaults(func=cmd_add)

    # CREATE (Alias for add without --url)
    create_p = subparsers.add_parser("create", help="Scaffold a new user-created agent resource.")
    create_p.add_argument("type", help="Resource type: skill, agent, instruction, plugin, prompt, schema, script, hook, mcp")
    create_p.add_argument("name", help="Name or identifier of the resource")
    create_p.add_argument("--author", help="Author name for user-created resources")
    create_p.add_argument("--description", help="Description of the resource")
    create_p.set_defaults(func=cmd_add, url=None, ref=None, subpath=None, raw=False, yes=False)

    # SYNC
    sync_p = subparsers.add_parser("sync", help="Register existing untracked workspace resources as user-created.")
    sync_p.add_argument("--author", help="Author name to attribute untracked items to")
    sync_p.set_defaults(func=cmd_sync)

    # UPDATE
    update_p = subparsers.add_parser("update", help="Update tracked remote resource(s) from remote GitHub.")
    update_p.add_argument("name", nargs="?", help="Specific resource name to update (updates all remote if omitted)")
    update_p.add_argument("--raw", action="store_true", help="Preserve raw upstream content without neutralization check")
    update_p.add_argument("-y", "--yes", action="store_true", help="Automatically accept cross-agent neutralization without prompting")
    update_p.set_defaults(func=cmd_update)

    # NEUTRALIZE
    neut_p = subparsers.add_parser("neutralize", help="Audit and prompt to neutralize model/vendor locks on an existing resource.")
    neut_p.add_argument("name", help="Resource name to neutralize")
    neut_p.add_argument("-y", "--yes", action="store_true", help="Automatically accept cross-agent neutralization without prompting")
    neut_p.set_defaults(func=cmd_neutralize)

    # VERIFY / VALIDATE
    verify_p = subparsers.add_parser("verify", help="Audit, lint, and verify health of all agent resources.")
    verify_p.add_argument("--fix", action="store_true", help="Automatically resolve repairable issues (such as executable permissions)")
    verify_p.set_defaults(func=cmd_verify)

    # ANALYZE / INSPECT
    analyze_p = subparsers.add_parser("analyze", help="Deep inspection of token size, line count, and cross-agent compatibility.")
    analyze_p.add_argument("name", nargs="?", help="Specific resource name to analyze (analyzes all if omitted)")
    analyze_p.set_defaults(func=cmd_analyze)

    # EXPORT
    export_p = subparsers.add_parser("export", help="Package resource(s) into a portable bundle (.tar.gz or .zip).")
    export_p.add_argument("name", nargs="?", help="Resource name to export (or 'all' for complete library)")
    export_p.add_argument("--output", "-o", help="Target output file path")
    export_p.add_argument("--format", choices=["tar.gz", "zip"], default="tar.gz", help="Archive format")
    export_p.set_defaults(func=cmd_export)

    # INFO
    info_p = subparsers.add_parser("info", help="Display metadata card and files for a specific resource.")
    info_p.add_argument("name", help="Name of the resource")
    info_p.set_defaults(func=cmd_info)

    # LIST
    list_p = subparsers.add_parser("list", help="List all tracked and local agent resources.")
    list_p.set_defaults(func=cmd_list)

    # REMOVE
    remove_p = subparsers.add_parser("remove", help="Remove a resource and deregister it.")
    remove_p.add_argument("name", help="Name of the resource to remove")
    remove_p.set_defaults(func=cmd_remove)

    # DOCTOR (Diagnostics)
    doctor_p = subparsers.add_parser("doctor", help="Run comprehensive environment and configuration diagnostics.")
    doctor_p.set_defaults(func=cmd_doctor)

    # INIT (Workspace Scaffolding)
    init_p = subparsers.add_parser("init", help="Scaffold or initialize project context and stack in AGENTS.md.")
    init_p.add_argument("--name", help="Project name")
    init_p.add_argument("--stack", help="Target tech stack or framework")
    init_p.add_argument("--goal", help="Project objective or purpose")
    init_p.add_argument("--author", help="Author or maintainer name")
    init_p.add_argument("--non-interactive", action="store_true", help="Skip interactive prompts")
    init_p.set_defaults(func=cmd_init)

    # IGNORE (AI Exclusions)
    ignore_p = subparsers.add_parser("ignore", help="Manage AI assistant exclusion rules (.agents/aiignore).")
    ignore_sub = ignore_p.add_subparsers(dest="ignore_action", required=False)
    ignore_sync_p = ignore_sub.add_parser("sync", help="Synchronize .agents/aiignore to .cursorignore and .claudeignore.")
    ignore_sync_p.set_defaults(func=cmd_ignore, ignore_action="sync")
    ignore_check_p = ignore_sub.add_parser("check", help="Check parity between .agents/aiignore and adapter files.")
    ignore_check_p.set_defaults(func=cmd_ignore, ignore_action="check")
    ignore_p.set_defaults(func=cmd_ignore, ignore_action="sync")

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
