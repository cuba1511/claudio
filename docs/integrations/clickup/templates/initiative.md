# Initiative Template

Initiatives live in **P&T - General > 01. P&T Strategic Planning > Approved Initiatives** (List ID: `901213053436`).

An Initiative is the strategic parent of a group of Epics. It answers the **Why**, the **How Much**, and the **How** — but leaves the detailed execution to each Epic underneath.

---

## Structure

Every Initiative uses this exact 4-section format:

---

### 2. 🎯 Vision and Justification (The "Why")

**🚨 Problem to be Solved:**
[Describe the current situation and pain. Be specific with metrics and data. What's broken, who feels it, what's the quantified impact.]

**✨ Business Opportunity/Strategic Value:**
[Why does the business care? What's the upside of solving this? Connect to revenue, efficiency, or pipeline.]

**💡 Initiative Goal (Elevator Pitch):**
[1-2 sentences max. What will we do and what will we achieve? Should be clear enough to explain to any stakeholder in 30 seconds.]

---

### 3. ✅ Success Criteria and Measurement (The "How Much")

**📈 Business KPIs Impacted:**

| KPI | Baseline | Target |
|-----|----------|--------|
| [Metric 1] | [Current value] | [Target value] |
| [Metric 2] | [Current value] | [Target value] |

**🥅 Specific Metric(s) (Goal):**
- [Metric 1]: [baseline] → [target] ([context: recover to X levels, surpass Y, etc.])
- [Metric 2]: [baseline] → [target]
- [How long targets must be sustained, e.g. "4 consecutive weeks by end of QX"]

**📝 Definition of Done:**
- [ ] [Metric target achieved and sustained]
- [ ] [Key deliverable 1 live]
- [ ] [Key deliverable 2 live]
- [ ] [Any technical/operational requirement]

---

### 4. ⚙️ Scope and Technical Detail (The "How")

**🗺️ Main Milestones:**
- **[Month 1]** — [What gets delivered]
- **[Month 2]** — [What gets delivered]
- **[Month 3]** — [Validation / optimization]

**🚫 Out of Scope (Key Exclusions):**
- [Item] → [Where it lives instead]
- [Item] → [Why excluded]

**🔗 Dependencies and Blockers:**
- [Dependency] ([Owner]) — [what it blocks]
- [Dependency] ([Owner]) — [what it blocks]

**📚 Documentation and Resources:**
- [Resource name]: [Link]
- [Resource name]: [Link]

---

## Example

### 2. 🎯 Vision and Justification (The "Why")

**🚨 Problem to be Solved:**
Since November 2025, two critical top-of-funnel metrics have been declining steadily. Show-up rate dropped from 40.2% to 28% (-30% relative) and CR Lead→Group Call Booked fell from 52% to 48.6%. The decline is operationally driven: the Sales Agent has accumulated capability drift without conversion guardrails, messages have never been iterated, HubSpot flows are ungoverned, and there is zero observability into bot performance — meaning regressions go undetected until metrics tank.

**✨ Business Opportunity/Strategic Value:**
The Sales Agent is the primary driver of top-of-funnel conversion. Recovering and improving these metrics means more group call attendees and more bookings — directly feeding the sales pipeline without increasing acquisition spend. Every point recovered in show-up rate is pipeline the business already paid to acquire.

**💡 Initiative Goal (Elevator Pitch):**
Fix the operational debt of the Sales Agent — HubSpot foundations, observability, scalable architecture, frictionless booking, and lead intelligence — to recover show-up rate to 40% and CR Lead→GC to 55% by end of Q2 2026.

---

### 3. ✅ Success Criteria and Measurement (The "How Much")

**📈 Business KPIs Impacted:**

| KPI | Baseline | Target |
|-----|----------|--------|
| Show-up Rate | 28% | **40%** |
| CR Lead → Group Call Booked | 48.6% | **55%** |

**🥅 Specific Metric(s) (Goal):**
- Show-up Rate: 28% → 40% (recover to Nov 2025 levels)
- CR Lead → Group Call Booked: 48.6% → 55% (surpass Nov 2025)
- Both targets sustained for 4+ consecutive weeks by end of Q2 2026

**📝 Definition of Done:**
- [ ] Show-up rate ≥ 40% sustained 4 consecutive weeks
- [ ] CR Lead → GC ≥ 55% sustained 4 consecutive weeks
- [ ] Analytics Service live and tracking bot performance in real time
- [ ] HubSpot flows governed, data completeness > 90%
- [ ] Agent running on scalable architecture with no regressions

---

### 4. ⚙️ Scope and Technical Detail (The "How")

**🗺️ Main Milestones:**
- **Apr 2026** — HubSpot Foundations + Analytics Service + Agent Migration
- **May 2026** — Frictionless In-Chat Booking + Lead Intelligence live
- **Jun 2026** — Optimization, iteration, metric validation

**🚫 Out of Scope (Key Exclusions):**
- Post-1:1 call experience → Engagement Agent initiative
- Lead acquisition and marketing → Growth team
- Payment and closing flows → Engagement Agent initiative

**🔗 Dependencies and Blockers:**
- HubSpot API access (Architecture) — blocks Epic 1 + Epic 5
- Q1 Sales Agent delivery ✅ Ready
- Lead profile / scoring criteria definition (Sales Ops) — blocks Epic 5

**📚 Documentation and Resources:**
- Q1 Sales Agent Initiative: https://app.clickup.com/t/869bvn0n7
- Q2 Epics: https://app.clickup.com/36668236/v/l/li/901216091884

---

## Writing Guidelines

### Problem to be Solved
- Lead with quantified metrics (%, €, hours)
- Always cite the data source
- Explain WHY the problem exists, not just what it is

### Business Opportunity
- Connect to revenue, pipeline, or efficiency — never just "it's better UX"
- Answer: what does the business gain by solving this?

### Initiative Goal
- One sentence if possible
- Outcome-focused, not feature-focused
- Bad: "Build a new analytics dashboard"
- Good: "Add real-time bot observability to detect and prevent conversion regressions"

### KPIs
- Always include baseline AND target
- Specify the timeline for achieving the target
- Define how long the target must be sustained (prevents gaming)

### Definition of Done
- Checkboxes, not vague descriptions
- Mix of metric targets + operational deliverables
- Must be objectively verifiable

### Out of Scope
- Be explicit — prevents scope creep
- Always say WHERE the excluded item lives instead

## Notes
- Section numbering starts at 2 because section 1 is the ClickUp task header (name, assignee, status, dates)
- Initiatives are created in List ID `901213053436` (Approved Initiatives, P&T General)
- Each Initiative should have 2-5 Epics underneath it
- Epics live in the current quarter's Epics list in DS & AI Squad (e.g. `901216091884` for Q2 2026)
