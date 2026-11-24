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
 │  24 Skills, 1 MCP                       │  3 Skills, 1 Instruction                     │
 │                                                                                        │
 │  🧪 Web App Testing & Playwright        │  📝 Documentation & Technical Writing        │
 │  3 Skills, 2 Agents, 1 Inst, 1 MCP       │  5 Skills, 1 Agent, 2 Instructions           │
 │                                                                                        │
 │  ⚙️ AgentOps & Architecture             │  🔌 Extensibility Points                     │
 │  1 Agent, 1 Script, 2 Schemas, 1 MCP    │  Hooks (.gitkeep), Plugins, Prompts          │
 │                                                                                        │
 └────────────────────────────────────────────────────────────────────────────────────────┘
```

Every resource is tracked in the provenance registry [`.agents/registry.json`](../.agents/registry.json) and classified by domain specialization and functional subcategory below.

---

## 2. Categorized Catalog

### 1. 🎨 Design Systems & Figma Integration (Design ↔ Code)
*Complete ecosystem for design tokens, component contracts, canvas manipulation, design-to-code translation, SwiftUI mirroring, 3D transforms, shaders, and UI motion.*

#### 1.1. Design Tokens & Hierarchical Spacing (Skills)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Skill** | `cc-figma-tokens` | `.agents/skills/cc-figma-tokens/SKILL.md` | Builds and updates Figma native variable collections (Primitives & Semantic) from component-contract token definitions. |
| **Skill** | `sync-figma-token` | `.agents/skills/sync-figma-token/SKILL.md` | Token synchronization workflow between codebases, design tokens, and Figma files. |
| **Skill** | `rad-spacing` | `.agents/skills/rad-spacing/SKILL.md` | Hierarchical spacing using Gestalt proximity in 8px/4px library variable increments. |

#### 1.2. Component Architecture & Code Connect (Skills)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Skill** | `cc-figma-component` | `.agents/skills/cc-figma-component/SKILL.md` | Generates Figma component sets with full variant properties from component contract files. |
| **Skill** | `figma-generate-library` | `.agents/skills/figma-generate-library/SKILL.md` | Generates comprehensive Figma component libraries, token bindings, and Light/Dark themes. |
| **Skill** | `figma-code-connect` | `.agents/skills/figma-code-connect/SKILL.md` | Creates and maintains Figma Code Connect templates (`.figma.ts` / `.figma.js`). |
| **Skill** | `figma-design-to-code` | `.agents/skills/figma-design-to-code/SKILL.md` | Mandatory prerequisite protocol for translating Figma designs into clean production code. |
| **Skill** | `figma-code-workflows` | `.agents/skills/figma-code-workflows/SKILL.md` | Imports HTML/code to Figma and supports standalone Code Layers and Make environments. |

#### 1.3. Screen Layouts, Specs & Diagramming (Skills)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Skill** | `figma-generate-design` | `.agents/skills/figma-generate-design/SKILL.md` | Assembles full pages, views, dialogs, and layouts in Figma from specs or code. |
| **Skill** | `apply-design-system` | `.agents/skills/apply-design-system/SKILL.md` | Reviews existing canvas designs and maps loose elements to design system components. |
| **Skill** | `figma-create-new-file` | `.agents/skills/figma-create-new-file/SKILL.md` | Guided workflow for initializing new Figma Design, FigJam, or Slides files. |
| **Skill** | `figma-generate-diagram` | `.agents/skills/figma-generate-diagram/SKILL.md` | Generates technical diagrams (flowchart, sequence, ERD, state machines) in FigJam/Mermaid. |
| **Skill** | `figma-spec` | `.agents/skills/figma-spec/SKILL.md` | Creates and edits PRDs, RFCs, and engineering specifications inside Figma. |

#### 1.4. Multi-Canvas Workspaces: FigJam & Slides (Skills)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Skill** | `figma-use-figjam` | `.agents/skills/figma-use-figjam/SKILL.md` | FigJam canvas automation, sticky notes, connectors, and whiteboard actions. |
| **Skill** | `figma-use-slides` | `.agents/skills/figma-use-slides/SKILL.md` | Figma Slides automation, slide generation, and presentation layouts. |

#### 1.5. Advanced Graphics: 3D, Shaders, Motion & SwiftUI (Skills)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Skill** | `figma-3d-transforms` | `.agents/skills/figma-3d-transforms/SKILL.md` | Adds depth, perspective, z-axis rotation, tilt, isometric views, and parallax effects. |
| **Skill** | `figma-shaders` | `.agents/skills/figma-shaders/SKILL.md` | Authors custom shader fills, procedural shader effects, and GPU visuals in Figma. |
| **Skill** | `figma-use-motion` | `.agents/skills/figma-use-motion/SKILL.md` | Canvas animation authoring via manual keyframes, easing curves, and timeline durations. |
| **Skill** | `figma-implement-motion` | `.agents/skills/figma-implement-motion/SKILL.md` | Translates Figma motion and micro-interactions into production code (CSS/Web Animations). |
| **Skill** | `figma-swiftui` | `.agents/skills/figma-swiftui/SKILL.md` | Bi-directional Figma ↔ SwiftUI translation for native iOS and macOS application development. |

#### 1.6. Canvas Automation & Generative Plugins (Skills)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Skill** | `figma-use` | `.agents/skills/figma-use/SKILL.md` | Low-level script executor for Figma Plugin API (nodes, auto-layout, fills, bindings). |
| **Skill** | `figma-generative-plugins` | `.agents/skills/figma-generative-plugins/SKILL.md` | Authors, modifies, and debugs reusable generative Figma plugins. |

#### 1.7. Design System Auditing & Drift Resolution (Skills)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Skill** | `audit-design-system` | `.agents/skills/audit-design-system/SKILL.md` | Audits Figma screens or components for drift, missing shared components, and unbound tokens. |
| **Skill** | `fix-design-system-finding` | `.agents/skills/fix-design-system-finding/SKILL.md` | Resolves specific audit findings (unbound tokens, raw colors, component detachments). |

#### 1.8. Model Context Protocol Tools (MCP)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **MCP** | `figma` | `.agents/mcp.json` (`https://mcp.figma.com/mcp`) | Official Figma remote MCP server providing design context, canvas inspection, and Code Connect. |

---

### 2. 💻 Front End Development
*Modern web platform standards, distinctive user interface aesthetics, and browser runtime capabilities.*

#### 2.1. Web Standards, Modern APIs & Accessibility (Skills)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Skill** | `modern-web-guidance` | `.agents/skills/modern-web-guidance/SKILL.md` | Search tool and guidelines for modern HTML/CSS/JS APIs (dialogs, popovers, container queries, view transitions, a11y). |

#### 2.2. Aesthetic Direction & Visual UI Design (Skills)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Skill** | `frontend-design` | `.agents/skills/frontend-design/SKILL.md` | Guidance for intentional, distinctive visual design, typography, and anti-generic UI aesthetics. |

#### 2.3. Browser Extensions & Manifest V3 Engineering (Skills)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Skill** | `chrome-extensions` | `.agents/skills/chrome-extensions/SKILL.md` | End-to-end authoring, architecture, debugging, and store publication for Chrome Extensions (Manifest V3). |

#### 2.4. Web Accessibility & WCAG 2.2 Standards (Instructions)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Instruction** | `a11y` | `.agents/instructions/a11y.md` | Comprehensive WCAG 2.2 AA accessibility standards, 38+ anti-patterns, legal compliance (EAA, ADA), and framework-specific patterns. |

---

### 3. 🧪 Web App Testing, Playwright & Browser QA
*Comprehensive browser automation, Playwright end-to-end test generation, website exploration, and runtime regression diagnostics.*

#### 3.1. E2E Automation, Exploration & Test Generation (Skills)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Skill** | `playwright-cli` | `.agents/skills/playwright-cli/SKILL.md` | Token-efficient browser automation CLI workflows, web testing, snapshots, and session management. |
| **Skill** | `playwright-generate-test` | `.agents/skills/playwright-generate-test/SKILL.md` | Generates Playwright end-to-end tests based on user scenarios via Playwright MCP. |
| **Skill** | `playwright-explore-website` | `.agents/skills/playwright-explore-website/SKILL.md` | Explores live websites and interactive workflows to discover edge cases using Playwright MCP. |

#### 3.2. Model Context Protocol Browser Engine (MCP)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **MCP** | `playwright` | `.agents/mcp.json` (`@playwright/mcp@latest`) | Official Playwright MCP server for browser automation, web testing, and accessibility snapshot workflows. |

#### 3.3. Test Engineering Standards & Specifications (Instructions)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Instruction** | `playwright-typescript.md` | `.agents/instructions/playwright-typescript.md` | Playwright TypeScript test generation rules, robust locators, and assertions (`applyTo: '**/tests/**/*.ts'`). |

#### 3.4. Runtime Regression & Diagnostic Specialists (Agents)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Agent** | `devtools-regression-investigator.md` | `.agents/agents/devtools-regression-investigator.md` | Browser regression specialist diagnosing broken flows, failed submissions, and root causes via Chrome DevTools. |

#### 3.5. Runtime Accessibility Testing (Agents)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Agent** | `accessibility-runtime-tester.md` | `.agents/agents/accessibility-runtime-tester.md` | Runtime accessibility specialist for keyboard flows, focus management, dialog behavior, and evidence-backed WCAG validation. |

---

### 4. 📝 Documentation, Technical Writing & LLM Context
*Technical documentation architecture, Markdown accessibility standards, and LLM context files.*

#### 4.1. Technical Documentation Frameworks & Drift Audits (Skills)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Skill** | `documentation-writer` | `.agents/skills/documentation-writer/SKILL.md` | Diátaxis documentation authoring framework (Tutorials, How-Tos, Technical References, Concept Explanations). |
| **Skill** | `docs-sync-audit` | `.agents/skills/docs-sync-audit/SKILL.md` | Read-only documentation drift auditor checking code implementation vs. documentation claims. |
| **Skill** | `create-readme` | `.agents/skills/create-readme/SKILL.md` | Scaffolds comprehensive, standardized project `README.md` documents. |

#### 4.2. LLM Context Standards: llms.txt (Skills)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Skill** | `create-llms` | `.agents/skills/create-llms/SKILL.md` | Generates standardized `llms.txt` and `llms-full.txt` files compliant with the llmstxt.org specification. |
| **Skill** | `update-llms` | `.agents/skills/update-llms/SKILL.md` | Keeps `llms.txt` synchronized with ongoing repository, specification, and documentation changes. |

#### 4.3. Markdown Syntax & Accessibility Standards (Instructions)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Instruction** | `markdown-gfm.md` | `.agents/instructions/markdown-gfm.md` | GitHub-Flavored Markdown syntax rules, callout alerts, tables, and Mermaid diagram constraints. |
| **Instruction** | `markdown-accessibility.md` | `.agents/instructions/markdown-accessibility.md` | Markdown accessibility standards adhering to WCAG and GitHub's 5 best practices. |

#### 4.4. Documentation Quality & Accessibility Specialists (Agents)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Agent** | `markdown-accessibility-assistant.md` | `.agents/agents/markdown-accessibility-assistant.md` | Specialized persona for auditing and improving accessibility across Markdown documentation. |

---

### 5. ⚙️ AgentOps, Governance & Workspace Architecture
*Core infrastructure, automation utilities, JSON schemas, registry provenance, and cross-assistant governance.*

#### 5.1. Resource Architecture & Lifecycle Custodians (Agents & Skills)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Agent** | `agents-manager.md` | `.agents/agents/agents-manager.md` | Custodian agent for resource lifecycle: discovery, import, neutralization, verification, and MCP management. |
| **Skill** | `manage-agent-resources` | `.agents/skills/manage-agent-resources/SKILL.md` | Universal toolkit for discovering, scaffolding, verifying, updating, and exporting `.agents/` assets. |

#### 5.2. Workspace Automation & Operational Tooling (Scripts)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Script** | `agents-manager.py` | `.agents/scripts/agents-manager.py` | Universal CLI automation harness for registry provenance, MCP sync, and health audits. |

#### 5.3. Provenance Schemas & Resource Registry (Schemas & Registry)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Schema** | `registry.schema.json` | `.agents/schemas/registry.schema.json` | JSON Schema validating the structure, metadata, and provenance of `.agents/registry.json`. |
| **Schema** | `mcp.schema.json` | `.agents/schemas/mcp.schema.json` | JSON Schema validating MCP configuration formats and tool definitions. |
| **Registry** | `registry.json` | `.agents/registry.json` | Single source of provenance tracking all 48 local and imported resources. |

#### 5.4. Workspace Execution Environment Tools (MCP)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **MCP** | `filesystem` | `.agents/mcp.json` | Local filesystem MCP server enabling safe file reading and editing in workspace paths. |

#### 5.5. Core Governance & Security Exclusions (Governance & Policies)
| Type | Resource / File | Location | Specialization & Functional Description |
| :--- | :--- | :--- | :--- |
| **Governance** | `AGENTS.md` | `AGENTS.md` | Universal Single Source of Truth (SSOT) defining conventions for all AI coding assistants. |
| **Governance** | `GEMINI.md` | `GEMINI.md` | Antigravity-specific entry point routing instructions to `AGENTS.md`. |
| **Exclusions** | `aiignore` | `.agents/aiignore` | Universal context exclusion rules kept synchronized with `.cursorignore` and `.claudeignore`. |

---

### 6. 🔌 Extensibility Points (Hooks, Plugins & Prompts)
*Reserved canonical directories for expanding workspace functionality:*

#### 6.1. Tool Execution & Lifecycle Interceptors (Hooks)
| Type | Location | Purpose & Extension Protocol |
| :--- | :--- | :--- |
| **Hooks** | `.agents/hooks/` | Lifecycle triggers (e.g. pre-tool linting, post-tool formatting, git commit verification). |

#### 6.2. Namespaced Multi-Resource Bundles (Plugins)
| Type | Location | Purpose & Extension Protocol |
| :--- | :--- | :--- |
| **Plugins** | `.agents/plugins/` | Reusable, namespaced packages combining skills, agents, rules, and MCP servers into single units. |

#### 6.3. Prompt Engineering & Reusable Templates (Prompts)
| Type | Location | Purpose & Extension Protocol |
| :--- | :--- | :--- |
| **Prompts** | `.agents/prompts/` | Reusable prompt templates, query structures, and domain-specific evaluation prompts. |

---

## 3. Category Management & Future Expansion Protocol

The workspace uses a **two-tier hierarchical taxonomy** to organize agent capabilities cleanly without context bloat:
1. **Tier 1 — Primary Domain Categories**: Broad technical domains numbered with emoji identifiers (e.g., `1. 🎨 Design Systems`, `2. 💻 Front End`, `3. 🧪 Web App Testing`).
2. **Tier 2 — Functional Subcategories**: Specific operational groupings numbered hierarchically (`X.Y`), classifying resources by technical role (e.g., `3.1. E2E Automation Skills`, `3.2. MCP Engines`, `3.3. Test Instructions`, `3.4. Diagnostic Agents`).

### Active Workspace Categories
1. **🎨 1. Design Systems & Figma Integration (Design ↔ Code)** — 8 Subcategories (24 Skills, 1 MCP)
2. **💻 2. Front End Development** — 4 Subcategories (3 Skills, 1 Instruction)
3. **🧪 3. Web App Testing, Playwright & Browser QA** — 5 Subcategories (3 Skills, 1 MCP, 1 Instruction, 2 Agents)
4. **📝 4. Documentation, Technical Writing & LLM Context** — 4 Subcategories (5 Skills, 1 Agent, 2 Instructions)
5. **⚙️ 5. AgentOps, Governance & Workspace Architecture** — 5 Subcategories (1 Agent, 1 Script, 2 Schemas, 1 MCP, Registry & Policies)
6. **🔌 6. Extensibility Points** — 3 Subcategories (Hooks, Plugins, Prompts)

---

### Expansion Criteria: When to Create a New Category vs. Subcategory

| Action | Criterion | Threshold & Examples |
| :--- | :--- | :--- |
| **Add a Subcategory (`X.Y`)** | A new functional cluster belongs to an existing domain. | ≥ 1 new resource enhancing an existing domain (e.g., adding `3.5. Visual Regression Testing` under Testing). |
| **Create a New Category (`N.`)** | A distinctly new technical ecosystem or engineering discipline is introduced. | ≥ 2-3 dedicated resources spanning multiple types (e.g., Backend APIs, Cloud DevOps, AI/ML). |

---

### Planned & Recommended Future Categories

As new tools and domain needs are introduced to the workspace, future categories should follow this standardized roadmap:

- **🌐 Backend Engineering & APIs**: REST endpoints, GraphQL schemas, gRPC services, database ORMs (Prisma, Drizzle), serverless edge functions.
- **☁️ DevOps, Infrastructure & CI/CD**: Docker containers, Kubernetes manifests, Terraform IaC, GitHub Actions workflows, cloud deployment pipelines.
- **🛡️ Security, Privacy & Compliance**: SAST static analyzers, secret scanning, dependency vulnerability auditing (CVEs), OWASP compliance checkers.
- **📊 Data Engineering & AI/ML Pipelines**: Dataset cleaning, model evaluation suites, vector database connectors, embedding pipelines.
- **📱 Mobile & Cross-Platform Development**: React Native, Flutter, native Android/iOS tooling beyond SwiftUI.

---

### Step-by-Step Protocol for Adding a New Category

When adding or expanding categories, AI assistants and contributors must strictly execute the following steps:

1. **Verify Canonical Storage**: Ensure all associated files live strictly under `.agents/<type>/` (never in vendor folders).
2. **Track in Provenance Registry**: Record every new asset in [`.agents/registry.json`](../.agents/registry.json) with `python3 .agents/scripts/agents-manager.py sync` or `add`.
3. **Assign Tier 1 Category & Numbered Subcategories**: Select an icon, descriptive title, and scope summary. Break it down into numbered subcategories (`X.1`, `X.2`, etc.) by resource type.
4. **Populate Standard Markdown Table**: Use the four canonical columns:
   ```markdown
   | Type | Resource / File | Location | Specialization & Functional Description |
   | :--- | :--- | :--- | :--- |
   ```
5. **Update Top ASCII Diagram & Resource Counts**: Reflect the new category and increment the resource counters in Section 1.
6. **Audit Health & Invariants**: Run `python3 .agents/scripts/agents-manager.py verify` to ensure zero errors and complete invariant compliance.

---

## 4. Maintenance & Synchronization Rule

Per **Rule 6 in [AGENTS.md](../AGENTS.md)**:
> **Mandatory Catalog Update**: Whenever an agent resource (`agent`, `hook`, `instruction`, `plugin`, `prompt`, `schema`, `script`, `skill`, `mcp`, or other AI asset) is created, imported, recategorized, or deleted, this document MUST be updated in lockstep.

Furthermore, per **Rule 1 in [AGENTS.md](../AGENTS.md)**:
> **Absolute SSOT & Immutable Assistant Adapters**: All architectural guidelines, conventions, rules, and workflows must reside exclusively within `AGENTS.md`. Assistant-specific entry points (`GEMINI.md`, `.cursorrules`, `.github/copilot-instructions.md`) are strictly immutable, read-only forwarders and must NEVER be modified directly by AI assistants.

### Full Governance Hierarchy Reference

| # | Rule | Scope / Domain | Key Invariant |
| :-: | :--- | :--- | :--- |
| **1** | **Absolute SSOT & Immutable Assistant Adapters** | 🏛️ Governance | All guidelines live in `AGENTS.md`; assistant adapters are read-only. |
| **2** | **Cross-Agent Neutrality & Mandatory User Confirmation** | 🌐 Neutrality | Zero model locks; user approval required before neutralizing. |
| **3** | **English for All AI Artifacts** | 🔤 Standard | All configurations, prompts, and skills written in English. |
| **4** | **AI Exclusions & Security SSOT** | 🔒 Security | `.agents/aiignore` is SSOT synced to `.cursorignore` and `.claudeignore`. |
| **5** | **Agentic Mode MCP Synchronization** | 🔌 Tooling | `.agents/mcp.json` canonical SSOT synced to adapters. |
| **6** | **Mandatory Documentation & Taxonomy Synchronization** | 📚 Living Docs | Immediate lockstep updates to `docs/agent-resources-catalog.md`. |
| **7** | **Provenance Tracking: User Resources (`origin: "user"`)** | 🏷️ Provenance | Author, timestamp, and target path recorded in `registry.json`. |
| **8** | **Provenance Tracking: Remote Resources (`origin: "remote"`)** | 🔗 Provenance | Upstream Git URL, commit SHA, and subpath recorded in `registry.json`. |
| **9** | **Canonical Automation Tooling & Specialized Agent** | ⚙️ Tooling | Lifecycle operations executed via `agents-manager.py` / `agents-manager.md`. |
