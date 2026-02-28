# Monthly DS & AI Report — Workflow

## Overview

Generates a monthly review report for the DS & AI Squad, pulling data from ClickUp and structuring it to match the meeting agenda. The report covers the previous calendar month.

**Trigger:** "Generate the monthly DS & AI report" or "Crea el reporte mensual del squad"

**MCPs Used:**
- **ClickUp** — Epics, User Stories, Sprint tasks, Initiatives
- **Google Docs** *(optional)* — Publish the final report as a shareable doc
- **Slack** *(optional)* — Share the report link to the team channel

**Estimated generation time:** 2–4 minutes

---

## Meeting Agenda

| Segment | Time | Topics |
|---------|------|--------|
| Wins & Learnings | 0–10 min | Top 3 wins, biggest learnings, general updates |
| Metrics Deep-Dive | 10–30 min | Outcome metrics, delivery metrics, speed & quality, team health |
| Initiatives & Epics Review | 30–50 min | Planned vs delivered, epic status, risks & blockers, support needed |
| Recap | 50–60 min | Summary, decisions, next steps |

---

## Data Sources in ClickUp

| Data | List ID | Notes |
|------|---------|-------|
| Initiatives | `901213053436` | P&T - General > Approved Initiatives |
| Current Epics (Q1 2026) | `901215396098` | DS & AI Squad > Strategic Roadmap |
| Sprint tasks / User Stories | All sprint lists in `90127761372` | DS & AI Squad > Product Backlog & Sprints |
| Tech Debt & Spikes | `901213056236` | DS & AI Squad |

> ⚠️ Update the Epics list ID each quarter. Q1 2026 = `901215396098`

---

## Step-by-Step Flow

### Step 1 — Determine Date Range

Calculate the **previous full calendar month** automatically.

```
today = 2026-02-27
report_month = January 2026
date_from = 2026-01-01
date_to   = 2026-01-31
```

---

### Step 2 — Pull Epics (Current Quarter)

Query all Epics from the current quarter to get the strategic layer.

```
get_workspace_tasks(
  list_ids: ["901215396098"],  # Q1 2026 Epics
  include_closed: true
)
```

**Extract per Epic:**
- Name, Status, Assignees
- Description / Business Outcome
- Due date vs actual completion
- Custom fields: priority, initiative link

---

### Step 3 — Pull Completed & In-Progress Tasks (Report Month)

Query all sprint tasks updated or closed within the report month.

```
get_workspace_tasks(
  list_ids: [
    "901213056238",  # Sprint Backlog (Upcoming)
    "901215046511",  # Sprint 8 (active sprint — update each sprint)
    "901213056239",  # Backlog Global
    "901213056236"   # Tech Debt & Spikes
  ],
  date_updated_gt: <date_from_unix_ms>,
  date_updated_lt: <date_to_unix_ms>,
  include_closed: true
)
```

**Extract per task:**
- Name, Status (Done / In Progress / Blocked / Carried Over)
- Epic link (parent)
- Story points / effort estimate
- Assignee
- Time in status (for cycle time approximation)
- Tags (bug, feature, spike, tech-debt)

---

### Step 4 — Pull Initiatives (Strategic Context)

```
get_workspace_tasks(
  list_ids: ["901213053436"]  # Approved Initiatives
)
```

Filter to initiatives where DS & AI Squad is involved.

**Extract per Initiative:**
- Name, Status
- OKR / Strategic goal
- Success metrics defined
- DS & AI Epics linked to it

---

### Step 5 — Compute Delivery Metrics

Using the task data from Step 3, calculate:

| Metric | Formula |
|--------|---------|
| **Say/Do Ratio** | `tasks_completed / tasks_committed` × 100% |
| **Carry-over Points** | Tasks planned in the month but not completed |
| **Bug Rate** | `bugs_resolved / total_tasks_closed` |
| **Cycle Time (approx)** | Average days from "In Progress" → "Done" |
| **Completion Rate per Epic** | `epic_done_stories / epic_total_stories` |

> ⚠️ ClickUp doesn't expose sprint commitment directly — use tasks with status changed to "In Progress" at the start of the month as a proxy for "committed."

---

### Step 6 — Build the Report

Structure the output following the meeting agenda:

---

#### Section 1 — Wins & Learnings (0–10 min)

- **Top 3 Wins:** Pull the 3 closed Epics or high-impact tasks with the most significant outcomes. Prefer tasks tagged as "milestone" or with the highest story points.
- **Biggest Learnings:** Derive from tasks tagged "spike", "tech-debt" resolved, or blockers that were cleared.
- **General Updates:** Any initiative status changes, new approvals, or team changes from ClickUp comments/descriptions.

---

#### Section 2 — Metrics (10–30 min)

**Outcome Metrics (North Star / KPIs)**
- Link to Initiative success metrics (from Step 4)
- Note which KPIs moved and which did not (data may need to come from external sources like Sheets or dashboards — flag for manual input if ClickUp doesn't have it)

**Delivery Metrics**
- Say/Do Ratio
- Carry-over points (list them by name)
- Sprint velocity trend (if multiple sprints in the month)

**Speed & Quality**
- Cycle time average
- Bug count opened vs closed
- Tech debt items resolved

**Team Health** *(manual input — flag for presenter)*
- Prompt the user to fill in: team sentiment, capacity issues, hiring/offboarding

---

#### Section 3 — Initiatives & Epics Review (30–50 min)

For each active Initiative linked to DS & AI:

```
## [Initiative Name]
**Status:** 🟡 At Risk / 🟢 On Track / 🔴 Off Track

### Active Epics
| Epic | Status | % Complete | Due Date |
|------|--------|------------|---------|
| ... | ... | ... | ... |

### Risks & Blockers
- [Derived from tasks with status "Blocked" or overdue]

### Support Needed
- Decisions required: [list]
- Resources: [list]
- Alignment: [list]
```

---

#### Section 4 — Recap (50–60 min)

Auto-generated summary:
- Total tasks completed
- Initiatives on track vs at risk
- Top 3 action items / decisions needed
- Proposed focus for next month (from Epic backlog)

---

### Step 7 — Output Options

| Option | Action |
|--------|--------|
| **Terminal** | Print formatted Markdown |
| **Google Doc** | Create a new doc in the DS & AI shared folder (see below) |
| **Slack** | Post summary to `#ds-ai-team` channel with doc link |

**Google Drive folder:** `1M7cqCebNXSJ-kcALWC3CVS44C6sAKcFo`
URL: https://drive.google.com/drive/folders/1M7cqCebNXSJ-kcALWC3CVS44C6sAKcFo

Document naming convention: `DS & AI Monthly Review — [Month] [Year]`
Example: `DS & AI Monthly Review — January 2026`

Default: print to terminal + ask if the user wants to publish to Drive.

---

## Limitations & Manual Inputs Required

| Item | Reason |
|------|--------|
| North Star / KPI values | Not stored in ClickUp — must come from dashboards/Sheets |
| Team health / sentiment | Subjective — presenter fills in live |
| Cycle time precision | ClickUp API doesn't expose full status history unless time-tracking is enabled |
| Sprint commitment baseline | Requires sprint start snapshot — use story points if tracked |

---

## Example Trigger Prompts

```
"Generate the monthly DS & AI report for January 2026"
"Crea el reporte mensual de DS & AI de enero"
"Monthly report DS AI"
```

---

## Files

| File | Path |
|------|------|
| This workflow | `docs/workflows/monthly-ds-ai-report.md` |
| ClickUp config | `docs/integrations/clickup/config.md` |
| Related workflow | `docs/workflows/sprint-report.md` |
