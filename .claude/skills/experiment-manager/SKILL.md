---
name: experiment-manager
description: Growth experiment manager for PropHero. Use when creating, reviewing, updating, or closing experiments in Notion; when the user mentions experimentos, hipótesis, growth, A/B tests, sign-off, or experiment review meetings.
---

# Experiment Manager (Claudio Growth)

Manages the experiment lifecycle in Notion's **Ideas-Experiments** database using PropHero's growth framework.

## Before any action

1. Read `docs/integrations/notion/config.md` (IDs, stakeholders, lifecycle).
2. Read `docs/integrations/notion/templates/experiment.md` for page structure.
3. `notion-fetch` the experiments database if `collection://` ID is TBD or schema is unknown.

## The four pillars (mandatory)

Never create or move to `Review` without all four:

| Pillar | Requirement |
|--------|-------------|
| **Problema** | Quantified impact + evidence |
| **Hipótesis** | Testable if/then/because |
| **Métricas** | Primary (+ secondary/guardrails) with baseline & target |
| **Metodología** | Design, audience, duration, risks |

## Sign-off logic

1. Load stakeholder map from `config.md`.
2. **Always required:** Growth Lead, Product.
3. **Conditional** (add row to sign-off table when Tags or Area match):

| Trigger | Stakeholder |
|---------|-------------|
| `tech-change` tag or Area = Product | Engineering |
| `pii`, `gdpr`, `user-data` tags | Legal / Privacy |
| `pricing`, `billing`, `revenue` tags | Finance |
| `messaging`, `ads`, `external-comms` tags | Brand / Marketing |

4. Sign-off states: `Pending` | `Approved` | `Rejected`.
5. **Hard rule:** Do not set Status to `Running` until all required sign-offs are `Approved` and DB property Sign-off status = `Complete`.

## Workflow routing

| User intent | Follow |
|-------------|--------|
| New experiment | `docs/workflows/growth/create-experiment.md` |
| Meeting prep / sign-off audit | `docs/workflows/growth/experiment-review.md` |
| Mid-flight update / sign-off record | `docs/workflows/growth/update-experiment.md` |
| Close with Scaled/Killed | `docs/workflows/growth/conclude-experiment.md` |

## Standard execution flow

### Create

1. Gather missing pillars (ask only for critical gaps).
2. Compute required sign-offs from Area + Tags.
3. Build draft: DB properties + template body + sign-off table.
4. **Show draft — wait for confirmation.**
5. `notion-create-pages` with `data_source_id` from config.
6. Return Notion link + pending sign-offs.

### Review (meetings)

1. Query experiments in `Draft`, `Review`, `Approved`, `Running`.
2. Prioritize: pending sign-offs > launch-ready > ending soon > incomplete drafts.
3. Output agenda markdown with links and explicit decisions needed.
4. If Slack thread context is present, match mentioned experiments without re-asking.

### Update

1. `notion-search` → `notion-fetch`.
2. Validate status transition per `config.md`.
3. Show diff → confirm → `notion-update-page`.
4. Recalculate Sign-off status property.

### Conclude

1. Require Resultados + Aprendizajes sections.
2. Recommend Scaled vs Killed from success criteria.
3. Confirm → update body → `Concluded` → `Scaled` or `Killed`.

## MCP tool patterns

```
# Identity / schema
notion-fetch id=self
notion-fetch id=<experiments-db-url>

# Find
notion-search query="<experiment name>"

# Create
notion-create-pages parent=data_source_id properties={...} content=<template>

# Update
notion-update-page page_id command=update_properties | insert_content
```

Read `notion://docs/enhanced-markdown-spec` before writing Notion page content.

## Output rules

- Always return the **Notion page URL** after create/update.
- End with **next suggested action** (e.g. "Solicita sign-off de Legal").
- Use Spanish by default unless the user writes in English.
- Do not dump raw JSON from MCP responses.

## Confirm before write

```yaml
confirmar_antes: true
mostrar_borrador: siempre
```

Same discipline as Slack mode: show draft, wait for OK, then execute.

## Error handling

| Error | Action |
|-------|--------|
| DB 404 on fetch | Tell user to share Ideas-Experiments with Notion MCP; do not invent IDs |
| Missing pillar | Ask only for the missing field(s) |
| Invalid status jump | Explain required intermediate state |
| Ambiguous experiment name | List top 3 search matches and ask user to pick |

## Related files

- Config: `docs/integrations/notion/config.md`
- Template: `docs/integrations/notion/templates/experiment.md`
- Guide: `docs/integrations/notion/guide.md`
- CLAUDE.md: Modo Growth (Experimentos)
