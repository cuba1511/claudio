# ClickUp Configuration — P&T — DS & AI Squad

## Purpose

This document provides the ClickUp IDs and locations needed to **query context** and **create product artifacts** for the DS & AI Squad.

---

## Workspace & Space

| Field | Value |
|-------|-------|
| **Workspace ID** | `36668236` |
| **Space** | P&T - DS & AI Squad |
| **Space ID** | `90125280978` |

---

## Folder Structure

### 01. Strategic Roadmap (Epics - Context Source)

This folder contains **Epics**. Query here to get context before writing User Stories.

| Folder | Folder ID |
|--------|-----------|
| 01. Strategic Roadmap | `90127761373` |

**Lists inside:**

| List Name | List ID | Contains |
|-----------|---------|----------|
| **Q1 2026 Epics** | `901215396098` | ✅ **CURRENT QUARTER - Query Epics here** |
| Q4 2024 Epics (Commitment) | `901213056241` | Previous quarter (reference only) |
| Epics Backlog (Future) | `901213056240` | Future/planned Epics |

> ⚠️ **Always query the current quarter's Epics list.** The list name changes each quarter (Q1 2026, Q2 2026, etc.)

### 02. Product Backlog & Sprints (Work Execution)

This folder contains **User Stories** ready to be worked on.

| Folder | Folder ID |
|--------|-----------|
| 02. Product Backlog & Sprints | `90127761372` |

**Lists inside:**

| List Name | List ID | Purpose |
|-----------|---------|---------|
| 01. Backlog Global | `901213056239` | All backlog items before prioritization |
| **02. Sprint Backlog (Upcoming)** | `901213056238` | ✅ **CREATE USER STORIES HERE** |
| Sprint 8 (1/12 - 1/25) | `901215046511` | Current active sprint |
| 04. Tech Debt & Spikes | `901213056236` | Technical debt and research |

### 03. Product Knowledge & Research

| List Name | List ID | Purpose |
|-----------|---------|---------|
| Discovery & Research | `901213056230` | Product discovery work |
| Product Design & Specs | `901213056232` | Design specifications |

---

## Initiatives Location (P&T General)

Initiatives live in the **P&T - General** space, shared across all squads.

| Field | Value |
|-------|-------|
| **Space** | P&T - General |
| **Space ID** | `90125273389` |
| **Folder** | 01. P&T Strategic Planning |
| **Folder ID** | `90127760342` |

**Lists:**

| List Name | List ID | Purpose |
|-----------|---------|---------|
| **Approved Initiatives** | `901213053436` | ✅ **QUERY INITIATIVES HERE** |
| Backlog Initiatives | `901214672950` | Future/proposed initiatives |
| Ideas/Feedback collection | `900302181879` | Raw ideas and feedback |

---

## Workflow: Writing User Stories

### Step 1: Find the Initiative

When user says: *"Create a user story for the Sales Agent initiative"*

```
# Search for the Initiative by name in P&T General
get_workspace_tasks(
  list_ids: ["901213053436"],  # Approved Initiatives
  ...
)
# or if you have the ID:
get_task(taskId: "[initiative_id]")
```

### Step 2: Fetch Related Epics

Get the Epics from the **current quarter** (in DS & AI Squad):

```
# Search Epics in current quarter + backlog
get_workspace_tasks(
  list_ids: ["901215396098", "901213056240"],  # Q1 2026 Epics + Epics Backlog
  ...
)
# or get specific Epic:
get_task(taskId: "[epic_id]")
```

> 📅 **Note:** Use the current quarter's Epics list. Currently Q1 2026 = `901215396098`

### Step 3: Build Context

From Initiative, extract:
- OKR connection
- Strategic goal
- Success metrics
- Business value

From Epic(s), extract:
- Problem being solved
- Hypothesis
- Scope (in/out)
- Business outcomes

### Step 4: Write & Create User Story

Use the context + user prompt to write the User Story, then create it:

```
create_task(
  listId: "901213056238",  # Sprint Backlog (Upcoming)
  name: "🎯 [User Story Title]",
  markdown_description: [story with real context]
)
```

---

## Quick Reference

### Where to QUERY (Get Context)

| What | List ID | Space | Notes |
|------|---------|-------|-------|
| Initiatives | `901213053436` | P&T - General | Approved Initiatives |
| **Epics (Current Q)** | `901215396098` | DS & AI Squad | **Q1 2026 Epics** ← Always use current quarter |
| Epics (Future) | `901213056240` | DS & AI Squad | Epics Backlog |

### Where to CREATE

| What | List ID | Space | Notes |
|------|---------|-------|-------|
| User Stories | `901213056238` | DS & AI Squad | Sprint Backlog (Upcoming) |
| **Epics (Current Q)** | `901215396098` | DS & AI Squad | **Q1 2026 Epics** ← Always use current quarter |
| Epics (Future) | `901213056240` | DS & AI Squad | Epics Backlog |
| Initiatives | `901213053436` | P&T - General | Approved Initiatives |
| Tech Debt | `901213056236` | DS & AI Squad | Tech Debt & Spikes |

> 📅 **The Epics list changes each quarter.** Update the ID when a new quarter starts.

---

## Example Flow

**User says:** *"Create a user story about local testing for the Sales Agent initiative"*

**Agent does:**

1. **Query Initiative:**
   ```
   get_workspace_tasks(list_ids: ["901213053436"])
   → Find "Sales Agent" initiative
   → Extract: OKR, strategic goal, business value
   ```

2. **Query Related Epics (current quarter):**
   ```
   get_workspace_tasks(list_ids: ["901215396098", "901213056240"])
   → Q1 2026 Epics + Epics Backlog
   → Find Epics linked to Sales Agent
   → Extract: problem, hypothesis, scope, business outcomes
   ```

3. **Write User Story:**
   - Use `structure/user_story_structure.md` template
   - Include context from Initiative + Epic
   - Add user's specific requirements
   - Ensure business value is clear

4. **Create in ClickUp:**
   ```
   create_task(
     listId: "901213056238",
     name: "🧪 Local Testing Environment for Sales Agent",
     markdown_description: [full story]
   )
   ```
