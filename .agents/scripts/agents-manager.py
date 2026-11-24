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
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
AGENTS_DIR = WORKSPACE_ROOT / ".agents"
REGISTRY_FILE = AGENTS_DIR / "registry.json"

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
}

TYPE_ALIASES = {
    "skills": "skill",
    "agents": "agent",
    "instructions": "instruction",
    "plugins": "plugin",
    "prompts": "prompt",
    "scripts": "script",
    "hooks": "hook",
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
    meta = RESOURCE_TYPES[res_type]
    base_dir = meta["dir"]
    base_dir.mkdir(parents=True, exist_ok=True)
    if meta["is_dir"]:
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
    is_dir = RESOURCE_TYPES[res_type]["is_dir"]

    try:
        if is_dir:
            if target_path.exists():
                shutil.rmtree(target_path)
            if source_path.is_dir():
                shutil.copytree(source_path, target_path)
            else:
                target_path.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, target_path / source_path.name)
        else:
            if target_path.exists():
                if target_path.is_dir():
                    shutil.rmtree(target_path)
                else:
                    target_path.unlink()
            if source_path.is_file():
                shutil.copy2(source_path, target_path)
            else:
                default_file = source_path / f"{name}.md"
                if not default_file.exists():
                    files = [f for f in source_path.iterdir() if f.is_file()]
                    default_file = files[0] if files else None
                if default_file:
                    shutil.copy2(default_file, target_path)
                else:
                    shutil.copytree(source_path, target_path)
    except Exception as e:
        print(f"[ERROR] Failed copying resource to {target_path}: {e}", file=sys.stderr)
        shutil.rmtree(temp_clone_dir, ignore_errors=True)
        return False

    shutil.rmtree(temp_clone_dir, ignore_errors=True)

    # Cross-Agent Neutralization with confirmation prompt
    if not raw:
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
        "description": description or existing_entry.get("description", ""),
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
        base_dir = meta["dir"]
        if not base_dir.exists():
            continue

        for item in base_dir.iterdir():
            if item.name.startswith(".") or item.name == "registry.json":
                continue

            name = item.stem if not meta["is_dir"] else item.name
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
        base_dir = meta["dir"]
        if not base_dir.exists():
            continue
        for item in base_dir.iterdir():
            if item.name.startswith(".") or item.name == "registry.json":
                continue
            name = item.stem if not meta["is_dir"] else item.name
            if name not in tracked:
                unregistered.append((res_type, name))

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
        target_path = WORKSPACE_ROOT / tracked[name]["target_path"]
        origin = tracked[name].get("origin", "unknown")
        del tracked[name]
        save_registry(registry)
        print(f"[*] Deregistered '{name}' ({origin}) from registry.json.")

    if not target_path:
        for res_type in RESOURCE_TYPES:
            candidate = get_target_path(res_type, name)
            if candidate.exists():
                target_path = candidate
                break

    if target_path and target_path.exists():
        if target_path.is_dir():
            shutil.rmtree(target_path)
        else:
            target_path.unlink()
        print(f"[OK] Removed files at {target_path.relative_to(WORKSPACE_ROOT)}.")
    else:
        print(f"[WARN] No matching file or folder found for '{name}'.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Universal Agent Resource Manager for .agents/ folder.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ADD
    add_p = subparsers.add_parser("add", help="Add or import an agent resource.")
    add_p.add_argument("type", help="Resource type: skill, agent, instruction, plugin, prompt, script, hook")
    add_p.add_argument("name", help="Name or identifier of the resource")
    add_p.add_argument("--url", help="GitHub or Git repository URL to clone from")
    add_p.add_argument("--ref", help="Branch, tag, or commit to checkout (defaults to main)")
    add_p.add_argument("--subpath", help="Folder or file path inside the remote repository")
    add_p.add_argument("--author", help="Author name for user-created resources")
    add_p.add_argument("--description", help="Description of the resource")
    add_p.add_argument("--raw", action="store_true", help="Preserve raw upstream content without neutralization check")
    add_p.add_argument("-y", "--yes", action="store_true", help="Automatically accept cross-agent neutralization without prompting")
    add_p.set_defaults(func=cmd_add)

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

    # LIST
    list_p = subparsers.add_parser("list", help="List all tracked and local agent resources.")
    list_p.set_defaults(func=cmd_list)

    # REMOVE
    remove_p = subparsers.add_parser("remove", help="Remove a resource and deregister it.")
    remove_p.add_argument("name", help="Name of the resource to remove")
    remove_p.set_defaults(func=cmd_remove)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
