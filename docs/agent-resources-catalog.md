# Agent Resources Catalog & Taxonomy Directory

> **Canonical Categorized Inventory of all Workspace AI Resources** (Agents, Skills, Instructions, MCP Servers, Schemas, Scripts, Hooks, Plugins, Prompts, and Governance assets).

---

## 1. Overview & Architecture

This directory serves as the centralized, human-readable catalog and domain taxonomy for all agent capabilities within `.agents/` and workspace configurations.

```
                                  .agents/ ARTIFACT REGISTRY
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │                                                                                        │
 │  🎨 Design Systems & Figma Integration  │  💻 Front End Development                    │
 │  24 Skills, 1 MCP                       │  3 Skills                                    │
 │                                                                                        │
 │  📝 Documentation & Technical Writing   │  ⚙️ AgentOps & Architecture                  │
 │  5 Skills, 1 Agent, 2 Instructions      │  1 Agent, 1 Script, 2 Schemas, 1 MCP         │
 │                                                                                        │
 │  🔌 Extensibility Points: Hooks (.gitkeep), Plugins (.gitkeep), Prompts (.gitkeep)     │
 └────────────────────────────────────────────────────────────────────────────────────────┘
```

Every resource is tracked in the provenance registry [`.agents/registry.json`](../.agents/registry.json) and classified by domain specialization below.

---

## 2. Categorized Catalog

### 1. 🎨 Design Systems & Figma Integration (Design ↔ Code)
*Complete ecosystem for design tokens, component contracts, canvas manipulation, design-to-code translation, SwiftUI mirroring, 3D transforms, shaders, and UI motion.*

| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Skill** | `cc-figma-tokens` | `.agents/skills/cc-figma-tokens/SKILL.md` | Builds and updates Figma native variable collections (Primitives & Semantic) from component-contract token definitions. |
| **Skill** | `sync-figma-token` | `.agents/skills/sync-figma-token/SKILL.md` | Token synchronization workflow between codebases, design tokens, and Figma files. |
| **Skill** | `cc-figma-component` | `.agents/skills/cc-figma-component/SKILL.md` | Generates Figma component sets with full variant properties from component contract files. |
| **Skill** | `apply-design-system` | `.agents/skills/apply-design-system/SKILL.md` | Reviews existing canvas designs and maps loose elements to design system components. |
| **Skill** | `audit-design-system` | `.agents/skills/audit-design-system/SKILL.md` | Audits Figma screens or components for drift, missing shared components, and unbound tokens. |
| **Skill** | `fix-design-system-finding` | `.agents/skills/fix-design-system-finding/SKILL.md` | Resolves specific audit findings (unbound tokens, raw colors, component detachments). |
| **Skill** | `rad-spacing` | `.agents/skills/rad-spacing/SKILL.md` | Hierarchical spacing using Gestalt proximity in 8px/4px library variable increments. |
| **Skill** | `figma-generate-library` | `.agents/skills/figma-generate-library/SKILL.md` | Generates comprehensive Figma component libraries, token bindings, and Light/Dark themes. |
| **Skill** | `figma-code-connect` | `.agents/skills/figma-code-connect/SKILL.md` | Creates and maintains Figma Code Connect templates (`.figma.ts` / `.figma.js`). |
| **Skill** | `figma-design-to-code` | `.agents/skills/figma-design-to-code/SKILL.md` | Mandatory prerequisite protocol for translating Figma designs into clean production code. |
| **Skill** | `figma-generate-design` | `.agents/skills/figma-generate-design/SKILL.md` | Assembles full pages, views, dialogs, and layouts in Figma from specs or code. |
| **Skill** | `figma-code-workflows` | `.agents/skills/figma-code-workflows/SKILL.md` | Imports HTML/code to Figma and supports standalone Code Layers and Make environments. |
| **Skill** | `figma-use` | `.agents/skills/figma-use/SKILL.md` | Low-level script executor for Figma Plugin API (nodes, auto-layout, fills, bindings). |
| **Skill** | `figma-create-new-file` | `.agents/skills/figma-create-new-file/SKILL.md` | Guided workflow for initializing new Figma Design, FigJam, or Slides files. |
| **Skill** | `figma-generate-diagram` | `.agents/skills/figma-generate-diagram/SKILL.md` | Generates technical diagrams (flowchart, sequence, ERD, state machines) in FigJam/Mermaid. |
| **Skill** | `figma-use-figjam` | `.agents/skills/figma-use-figjam/SKILL.md` | FigJam canvas automation, sticky notes, connectors, and whiteboard actions. |
| **Skill** | `figma-use-slides` | `.agents/skills/figma-use-slides/SKILL.md` | Figma Slides automation, slide generation, and presentation layouts. |
| **Skill** | `figma-spec` | `.agents/skills/figma-spec/SKILL.md` | Creates and edits PRDs, RFCs, and engineering specifications inside Figma. |
| **Skill** | `figma-generative-plugins` | `.agents/skills/figma-generative-plugins/SKILL.md` | Authors, modifies, and debugs reusable generative Figma plugins. |
| **Skill** | `figma-swiftui` | `.agents/skills/figma-swiftui/SKILL.md` | Bi-directional Figma ↔ SwiftUI translation for native iOS and macOS application development. |
| **Skill** | `figma-3d-transforms` | `.agents/skills/figma-3d-transforms/SKILL.md` | Adds depth, perspective, z-axis rotation, tilt, isometric views, and parallax effects. |
| **Skill** | `figma-shaders` | `.agents/skills/figma-shaders/SKILL.md` | Authors custom shader fills, procedural shader effects, and GPU visuals in Figma. |
| **Skill** | `figma-use-motion` | `.agents/skills/figma-use-motion/SKILL.md` | Canvas animation authoring via manual keyframes, easing curves, and timeline durations. |
| **Skill** | `figma-implement-motion` | `.agents/skills/figma-implement-motion/SKILL.md` | Translates Figma motion and micro-interactions into production code (CSS/Web Animations). |
| **MCP** | `figma` | `.agents/mcp.json` (`https://mcp.figma.com/mcp`) | Official Figma remote MCP server providing design context, canvas inspection, and Code Connect. |

---

### 2. 💻 Front End Development
*Modern web platform standards, distinctive user interface aesthetics, and browser runtime capabilities.*

| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Skill** | `modern-web-guidance` | `.agents/skills/modern-web-guidance/SKILL.md` | Search tool and guidelines for modern HTML/CSS/JS APIs (dialogs, popovers, container queries, view transitions, a11y). |
| **Skill** | `frontend-design` | `.agents/skills/frontend-design/SKILL.md` | Guidance for intentional, distinctive visual design, typography, and anti-generic UI aesthetics. |
| **Skill** | `chrome-extensions` | `.agents/skills/chrome-extensions/SKILL.md` | End-to-end authoring, architecture, debugging, and store publication for Chrome Extensions (Manifest V3). |

---

### 3. 📝 Documentation, Technical Writing & LLM Context
*Technical documentation architecture, Markdown accessibility standards, and LLM context files.*

| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Skill** | `documentation-writer` | `.agents/skills/documentation-writer/SKILL.md` | Diátaxis documentation authoring framework (Tutorials, How-Tos, Technical References, Concept Explanations). |
| **Skill** | `docs-sync-audit` | `.agents/skills/docs-sync-audit/SKILL.md` | Read-only documentation drift auditor checking code implementation vs. documentation claims. |
| **Skill** | `create-readme` | `.agents/skills/create-readme/SKILL.md` | Scaffolds comprehensive, standardized project `README.md` documents. |
| **Skill** | `create-llms` | `.agents/skills/create-llms/SKILL.md` | Generates standardized `llms.txt` and `llms-full.txt` files compliant with the llmstxt.org specification. |
| **Skill** | `update-llms` | `.agents/skills/update-llms/SKILL.md` | Keeps `llms.txt` synchronized with ongoing repository, specification, and documentation changes. |
| **Instruction** | `markdown-gfm.md` | `.agents/instructions/markdown-gfm.md` | GitHub-Flavored Markdown syntax rules, callout alerts, tables, and Mermaid diagram constraints. |
| **Instruction** | `markdown-accessibility.md` | `.agents/instructions/markdown-accessibility.md` | Markdown accessibility standards adhering to WCAG and GitHub's 5 best practices. |
| **Agent** | `markdown-accessibility-assistant.md` | `.agents/agents/markdown-accessibility-assistant.md` | Specialized persona for auditing and improving accessibility across Markdown documentation. |

---

### 4. ⚙️ AgentOps, Governance & Workspace Architecture
*Core infrastructure, automation utilities, JSON schemas, registry provenance, and cross-assistant governance.*

| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Agent** | `agents-manager.md` | `.agents/agents/agents-manager.md` | Custodian agent for resource lifecycle: discovery, import, neutralization, verification, and MCP management. |
| **Skill** | `manage-agent-resources` | `.agents/skills/manage-agent-resources/SKILL.md` | Universal toolkit for discovering, scaffolding, verifying, updating, and exporting `.agents/` assets. |
| **Script** | `agents-manager.py` | `.agents/scripts/agents-manager.py` | Universal CLI automation harness for registry provenance, MCP sync, and health audits. |
| **Schema** | `registry.schema.json` | `.agents/schemas/registry.schema.json` | JSON Schema validating the structure, metadata, and provenance of `.agents/registry.json`. |
| **Schema** | `mcp.schema.json` | `.agents/schemas/mcp.schema.json` | JSON Schema validating MCP configuration formats and tool definitions. |
| **MCP** | `filesystem` | `.agents/mcp.json` | Local filesystem MCP server enabling safe file reading and editing in workspace paths. |
| **Registry** | `registry.json` | `.agents/registry.json` | Single source of provenance tracking all 42 local and imported resources. |
| **Governance** | `AGENTS.md` | `AGENTS.md` | Universal Single Source of Truth (SSOT) defining conventions for all AI coding assistants. |
| **Governance** | `GEMINI.md` | `GEMINI.md` | Antigravity-specific entry point routing instructions to `AGENTS.md`. |
| **Exclusions** | `aiignore` | `.agents/aiignore` | Universal context exclusion rules kept synchronized with `.cursorignore` and `.claudeignore`. |

---

### 5. 🔌 Extensibility Points (Hooks, Plugins & Prompts)
*Reserved canonical directories for expanding workspace functionality:*

| Type | Location | Purpose & Extension Protocol |
| :--- | :--- | :--- |
| **Hooks** | `.agents/hooks/` | Lifecycle triggers (e.g. pre-tool linting, post-tool formatting, git commit verification). |
| **Plugins** | `.agents/plugins/` | Reusable, namespaced packages combining skills, agents, rules, and MCP servers into single units. |
| **Prompts** | `.agents/prompts/` | Reusable prompt templates, query structures, and domain-specific evaluation prompts. |

---

## 3. Category Management & Future Expansion Protocol

As the workspace grows, new categories may be introduced whenever a cluster of capabilities emerges. Recommended upcoming categories include:

- **Backend & APIs**: REST, GraphQL, gRPC, database ORMs, serverless workers.
- **Testing, QA & Verification**: E2E testing (Playwright, Cypress), unit test harnesses, visual regression.
- **Security & Compliance**: SAST linters, secret scanning, dependency vulnerability management.
- **Data & AI/ML Pipelines**: Dataset processing, model evaluation, vector store integration.

### Rules for Adding or Modifying Categories:
1. **Cohesion**: A category should group at least 2-3 related resources sharing a clear technical domain.
2. **Standard Headers**: Use a descriptive name accompanied by an icon and domain scope summary.
3. **Cross-Agent Neutrality**: Ensure all resources referenced under any category remain vendor-neutral.

---

## 4. Maintenance & Synchronization Rule

Per **Rule 6 in [AGENTS.md](../AGENTS.md)**:
> **Mandatory Catalog Update**: Whenever an agent resource (`agent`, `hook`, `instruction`, `plugin`, `prompt`, `schema`, `script`, `skill`, `mcp`, or other AI asset) is created, imported, recategorized, or deleted, this document MUST be updated in lockstep.

Furthermore, per **Rule 1 in [AGENTS.md](../AGENTS.md)**:
> **Absolute SSOT & Immutable Assistant Adapters**: All architectural guidelines, conventions, rules, and workflows must reside exclusively within `AGENTS.md`. Assistant-specific entry points (`GEMINI.md`, `.cursorrules`, `.github/copilot-instructions.md`) are strictly immutable, read-only forwarders and must NEVER be modified directly by AI assistants.
