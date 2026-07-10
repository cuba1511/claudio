# Notion Configuration — Growth Experiments

## Purpose

Canonical IDs, stakeholder mapping, and lifecycle rules for Claudio's **Growth / Experiment Manager** mode.

> **Important:** The Ideas-Experiments database must be accessible to the Notion MCP integration. If `notion-fetch` returns 404, invite the integration to the page/database or reconnect OAuth to the correct workspace, then run `notion-fetch` on the DB URL to populate `data_source_id` below.

---

## Workspace

| Field | Value |
|-------|-------|
| **Workspace name** | Notion de Ignacio De La Cuba |
| **Workspace ID** | `3bb559e8-6d16-46cc-8610-4ffd1b011529` |
| **Default owner** | Ignacio De La Cuba (`b943d963-84f0-454f-b1f8-e538c451359e`) |

---

## Experiments Database

| Field | Value |
|-------|-------|
| **Name** | Ideas-Experiments |
| **URL** | https://app.notion.com/p/Ideas-Experiments-38a64a4709298022b997c86f7a583694 |
| **Page / Database ID** | `38a64a4709298022b997c86f7a583694` |
| **Data source ID** | `collection://TBD` — run `notion-fetch` on the URL above after granting access |

### Recommended database properties

Map these to existing Notion columns or add via `notion-update-data-source`:

| Property | Type | Purpose |
|----------|------|---------|
| **Name** | title | Experiment name |
| **Status** | select | Lifecycle state (see below) |
| **Owner** | person | DRI for the experiment |
| **Area** | select | Funnel stage / product area |
| **Tags** | multi_select | Triggers for extra sign-offs |
| **Start date** | date | Launch date |
| **End date** | date | Planned conclusion |
| **Primary metric** | text | North-star metric name |
| **Sign-off status** | select | `Pending` / `Partial` / `Complete` |

Page **body** always follows `docs/integrations/notion/templates/experiment.md` (Problema, Hipótesis, Métricas, Metodología, Sign-off, Resultados, Aprendizajes).

---

## Status Lifecycle

Valid transitions — do not skip states without explicit user approval:

```
Draft → Review → Approved → Running → Concluded → Scaled | Killed
```

| Status | Meaning | Who can set |
|--------|---------|-------------|
| **Draft** | Being written; missing pillars or sign-offs | Owner |
| **Review** | Complete draft; awaiting stakeholder sign-off | Owner |
| **Approved** | All required sign-offs done; ready to launch | Growth Lead |
| **Running** | Live in production / with users | Owner |
| **Concluded** | Data collection finished | Owner |
| **Scaled** | Winner rolled out broadly | Growth Lead |
| **Killed** | Stopped; learnings captured | Owner or Growth Lead |

**Hard rule:** Never move to `Running` unless `Sign-off status` = `Complete` and all required stakeholders are approved in the page body.

---

## Stakeholder Map

Update Notion user IDs after `notion-get-users` if needed.

| Stakeholder | Area | Notion user | Always required | Sign-off triggers |
|-------------|------|-------------|-----------------|-------------------|
| **Growth Lead** | Growth | Ignacio De La Cuba | Yes | All experiments |
| **Product** | Product | TBD | Yes | All experiments |
| **Engineering** | Tech | TBD | If `Tags` contains `tech-change` or `Area` = Product |
| **Legal / Privacy** | Compliance | TBD | If `Tags` contains `pii`, `gdpr`, or `user-data` |
| **Finance** | Revenue | TBD | If `Tags` contains `pricing`, `billing`, or `revenue` |
| **Brand / Marketing** | Comms | TBD | If `Tags` contains `messaging`, `ads`, or `external-comms` |

### Sign-off table (in page body)

Each experiment page includes:

| Stakeholder | Area | Estado | Fecha | Notas |
|-------------|------|--------|-------|-------|
| ... | ... | `Pending` / `Approved` / `Rejected` | | |

---

## Area values (suggested)

| Area | Examples |
|------|----------|
| **Acquisition** | Meta ads, landing pages, lead forms |
| **Activation** | Onboarding, first session, qualification |
| **Conversion** | Booking, show-up, close rate |
| **Retention** | Nurture, re-engagement |
| **Product** | In-app flows, InvestMap, tooling |
| **Ops** | Internal process, automation |

---

## Quick MCP commands

```text
# Verify connection
notion-fetch id=self

# Load experiments DB schema (after access granted)
notion-fetch id=https://app.notion.com/p/Ideas-Experiments-38a64a4709298022b997c86f7a583694

# List active experiments
notion-query-data-sources with SQL on collection ID

# Find experiment by name
notion-search query="nombre del experimento"
```

---

## Maintenance

1. After first successful `notion-fetch` of the DB, replace `collection://TBD` with the real data source ID from the `<data-source url="collection://...">` tag.
2. Fill in TBD stakeholder Notion user IDs via `notion-get-users`.
3. If PropHero uses a team workspace, update workspace name/ID and reconnect OAuth if needed.
