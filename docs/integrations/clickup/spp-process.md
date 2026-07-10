# DS & AI Squad — Strategic Planning Process (SPP)

> *"**Initiatives** define what we're building and why, **Tasks** decompose the how into estimable, assignable work, and **Sprints** govern the when and capture the feedback loop for improvement."*

This document describes how the DS & AI Squad structures work in ClickUp across three databases. Use it to understand **where** an item lives, **which view** to query, and **what action** is expected at each planning phase.

**Related docs:**
- IDs and list locations → [`config.md`](./config.md)
- Templates for artifacts → [`templates/`](./templates/)
- MCP usage → [`guide.md`](./guide.md)

---

## Initiatives Roadmap

The **Initiatives Roadmap** tracks all DS & AI initiatives from first definition through to active execution.

Each view reflects a stage in the planning cycle. Use them to understand where each initiative stands and what action is expected at each phase.

| View | What you'll find here |
| --- | --- |
| **Strategic Definition** | Initiatives (Level = Initiative) entering the planning cycle. These are high-level proposals pending epic breakdown. |
| **Scoping & Sizing** | Initiatives being decomposed into epics, with feasibility and sizing assessed by Product & Tech. |
| **Execution Planning** | Epics and initiatives with scope defined and User Stories under refinement, ready to be committed to a sprint. |
| **In-Execution** | Approved initiatives currently in active development, grouped by Quarter. |
| **Backlog** | Initiatives not committed to the current Q, either pending capacity or awaiting a future planning cycle. |

---

## Task Management

The **Tasks Management** database is where epics break down into actionable work. Each task is linked to an Epic (from the Initiatives Roadmap) and assigned to a Sprint, creating full traceability from strategic objective through to daily execution.

Each view maps to a moment in the planning cycle. Use them based on where you are in the SPP:

| View | SPP Phase | What you'll find here |
| --- | --- | --- |
| **Epic Sizing** | Phase 2 — Scoping & Sizing | Tasks grouped by Epic, filterable by assignee. Used to validate total effort per epic and calibrate T-shirt sizes during initiative breakdown. |
| **Dependencies** | Phase 2 — Scoping & Sizing | Tasks with Component = Dependency, grouped by Epic, with Team visible. Tracks cross-squad dependencies that need coordination — directly addresses the late-dependency risk identified in the SPP proposal. |
| **Quarter Planning** | Phase 2 → 3 transition | Tasks grouped by Sprint, filterable by assignee. A focused view for distributing tasks across sprints within the quarter commitment. |
| **Task Planning** | Phase 3 — Execution Planning | Tasks not yet started, grouped by Type (Product / Internal). Use during sprint planning to see what's ready to be committed, with points, priority, and epic context visible. Only tasks linked to an Epic appear. |
| **Team Capacity** | Phase 3 — Execution Planning | Tasks grouped by Sprint, showing individual point load and % Sprint Capacity. Used to balance workload and detect overcommitment before the sprint starts. |
| **Task Timeline** | In-Execution | All tasks on a timeline using Sprint Start/End dates, grouped by Epic. A birds-eye view of when work is expected to land across initiatives. |
| **Packages** | All phases | Internal tasks (Subtype = Packages), grouped by Component. Tracks shared library work (hero_*, templates). |
| **Baselines** | All phases | Internal tasks (Subtype = Baselines), grouped by Component. Tracks infrastructure baseline work (monorepo, CI/CD, tooling). |
| **Issues** | All phases | Internal tasks (Subtype = Issues), with Github Ref visible. Bug fixes and incidents for quick cross-referencing with the codebase. |
| **Documentation** | All phases | Internal tasks (Subtype = Documentation). Tracks documentation debt and knowledge deliverables. |

---

## Sprint Management & Retrospectives

The **Sprint Management & Retrospectives** database manages the full sprint lifecycle — from planning through execution to retrospective — and captures team health signals for continuous improvement.

Each sprint entry holds a **Sprint Goal**, **Dates**, and links to all committed **Tasks**. Rollup properties automatically compute delivery metrics: *say/do ratio*, *carry-over points*, *insertion points*, *average cycle time*, and *bugs found*. A composite **Health Score** formula weighs these together with team perception signals.

| View | What you'll find here |
| --- | --- |
| **Sprint Management** | A table of all sprints with their goals, status (Current / Next / Future / Last / Past), and dates. The primary administrative view for sprint creation and lifecycle management. |
| **Timeline** | Sprints displayed on a timeline by their Dates property. Gives a visual overview of sprint cadence, upcoming capacity windows, and how sprints align with Quarter boundaries. |
| **Current Sprint** | A Kanban board of the active sprint's tasks, grouped by Status (Not started → Development → Code review → Product/QA review → Done). Filterable by assignee for personal focus during the sprint. |
| **Retrospective** | The retrospective dashboard. For each sprint: goal achievement (Goal met?), delivery metrics (points committed vs completed, say/do ratio, carry-over, insertion, cycle time, bugs, quality index), and team health averages (happiness, pressure, quality, cognitive load, deep work, composite Health Score). |
| **Individual Sprint Scores** | Per-person feedback for each sprint across the five health dimensions. Filled out by each team member after sprint close; data feeds the Retrospective view's averages. |

---

## Agent guidelines

When working with DS & AI Squad product artifacts:

1. **Respect the hierarchy**: Initiative → Epic → Task → Sprint. Never create tasks without Epic context unless explicitly asked for internal/spike work.
2. **Match the SPP phase**: Use the view tables above to infer what kind of work the user is doing (sizing, planning, execution, retro).
3. **Task subtypes matter**: Packages, Baselines, Issues, and Documentation are internal work — route them to the correct subtype and component.
4. **Sprint health**: When asked about sprint status or retros, reference delivery metrics (say/do, carry-over, insertion) and health dimensions.
5. **Cross-reference IDs**: Always pair this process doc with [`config.md`](./config.md) for concrete list IDs when querying or creating via MCP.
