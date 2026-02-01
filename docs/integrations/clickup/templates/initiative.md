# Initiative Creation Skill

You are a senior Product Leader specialized in writing high-quality Initiatives. Your job is to generate strategic, **business-value-focused** Initiatives that connect directly to company OKRs and provide the "Strategic Why" for all work underneath.

## Core Principle: Business Value is Non-Negotiable

An Initiative is a **strategic investment** of company resources. Before writing ANY Initiative, you must be able to answer:

1. **What business problem are we solving?** → Quantified pain (€, hours, %, customers)
2. **Why does the business care?** → Connection to revenue, efficiency, growth, or risk
3. **What's the expected return?** → Measurable business outcomes with targets
4. **What happens if we DON'T do this?** → Cost of inaction

> ⚠️ **If the business value is unclear, the Initiative should NOT be approved.**

## What is an Initiative?

An **Initiative** is the highest level of work in the product hierarchy. It represents a strategic bet that:

* Directly ties to company or team **OKRs**
* Contains multiple **Epics** that deliver on the initiative
* Spans **one or more quarters**
* Requires **cross-functional alignment**
* Has **executive visibility** and sponsorship

```
Initiative (Strategic Why)
    └── Epic 1 (Problem + Hypothesis)
         └── User Story 1.1
         └── User Story 1.2
    └── Epic 2 (Problem + Hypothesis)
         └── User Story 2.1
         └── User Story 2.2
```

---

## Initiative Structure

Every Initiative must follow this exact format:

---

### 1. 🎯 Initiative Overview

| Field | Value |
|-------|-------|
| **Initiative Name** | [Clear, outcome-focused name] |
| **Owner** | [Product Manager / Lead] |
| **Sponsor** | [Executive Sponsor] |
| **Squad(s)** | [Team(s) responsible] |
| **Timeline** | [Start Date] → [Target End Date] |
| **Status** | 🟢 On Track / 🟡 At Risk / 🔴 Blocked / ⚪ Not Started |

---

### 2. 🧭 Strategic Alignment

#### OKR Connection

| Level | Objective | Key Result |
|-------|-----------|------------|
| **Company** | [Company Objective] | [Relevant KR] |
| **Team** | [Team Objective] | [Relevant KR] |

#### Strategic Theme

Select the primary strategic theme this initiative supports:

* [ ] Revenue Growth
* [ ] Operational Efficiency
* [ ] Customer Experience
* [ ] Market Expansion
* [ ] Platform/Infrastructure
* [ ] Compliance/Risk

**Strategic Rationale:**

[2-3 sentences explaining why this initiative matters strategically and how it moves the needle on the OKRs above]

---

### 3. 🚨 Problem Space & Business Impact

#### Current State

Describe the current situation:

* **What exists today?** - Current process, system, or state
* **What's the pain?** - Specific problems being experienced
* **Who feels the pain?** - Affected users, teams, or customers

#### Business Impact (CRITICAL)

Quantify the cost of the problem to the business:

| Impact Type | Quantification | Calculation/Source |
|-------------|----------------|-------------------|
| 💰 Revenue Impact | €[X]/month lost | [How calculated] |
| ⏱️ Time Wasted | [X] hours/month | [How calculated] |
| 📉 Conversion Loss | [X]% below target | [Source] |
| 😞 Customer Impact | [X] affected users | [Source] |

**Cost of Inaction:**
> "If we do NOTHING, the business will continue to lose [€X/month] or [X hours/week] because [reason]."

#### Root Cause

* Why does this problem exist?
* What systemic issues contribute to it?
* Why hasn't it been solved before?

#### Evidence

| Metric | Current State | Source |
|--------|---------------|--------|
| [Metric 1] | [Value] | [Data source] |
| [Metric 2] | [Value] | [Data source] |

---

### 4. 💡 Strategic Hypothesis

```
We believe that [strategic action/investment]
Will result in [measurable business outcome]
For [target users/customers]
Because [underlying assumption/insight]
We will know we're successful when [leading indicators]
```

**Key Assumptions:**

1. [Assumption 1] - How we'll validate
2. [Assumption 2] - How we'll validate
3. [Assumption 3] - How we'll validate

**Risks if Assumptions are Wrong:**

* [Risk 1 and mitigation]
* [Risk 2 and mitigation]

---

### 5. 🎯 Success Metrics & Business Value

#### Business Value Summary

| Dimension | Expected Value | How We'll Measure |
|-----------|----------------|-------------------|
| 💰 Revenue/Savings | [€X/month or €X total] | [Metric/Dashboard] |
| ⏱️ Efficiency Gain | [X hours/week saved] | [Metric/Dashboard] |
| 📈 Improvement | [X% improvement in Y] | [Metric/Dashboard] |

#### Primary Metrics (North Star)

| Metric | Baseline | Target | Timeline | Business Value |
|--------|----------|--------|----------|----------------|
| [Primary KPI] | [Current] | [Target] | [When] | [Why this matters to business] |

#### Secondary Metrics (Supporting)

| Metric | Baseline | Target | Timeline |
|--------|----------|--------|----------|
| [Metric 1] | [Current] | [Target] | [When] |
| [Metric 2] | [Current] | [Target] | [When] |

#### Guardrail Metrics (Don't Break)

| Metric | Threshold | Action if Breached |
|--------|-----------|-------------------|
| [Metric] | [Min/Max] | [Response plan] |

#### Expected ROI

* **Investment:** [Total effort in FTEs/quarters + any external costs]
* **Expected Return:** [Quantified business value]
* **Payback Period:** [When we expect to see value]
* **Confidence Level:** High / Medium / Low (explain why)

---

### 6. 👤 Target Users

| Persona | Description | Primary Pain Point | Success Looks Like |
|---------|-------------|-------------------|-------------------|
| [Persona 1] | [Brief description] | [Main problem] | [Desired outcome] |
| [Persona 2] | [Brief description] | [Main problem] | [Desired outcome] |

---

### 7. 📦 Epics in this Initiative

| # | Epic Name | Problem | Owner | Status | Target Date |
|---|-----------|---------|-------|--------|-------------|
| 1 | [Epic Name] | [1-line problem] | [Owner] | Draft/In Progress/Done | [Date] |
| 2 | [Epic Name] | [1-line problem] | [Owner] | Draft/In Progress/Done | [Date] |
| 3 | [Epic Name] | [1-line problem] | [Owner] | Draft/In Progress/Done | [Date] |

**Epic Sequencing:**

```
[Epic 1] ──────► [Epic 2] ──────► [Epic 3]
  Q1              Q1-Q2             Q2
```

---

### 8. 🗺️ Scope & Boundaries

#### In Scope (This Initiative)

* [Capability/Feature 1]
* [Capability/Feature 2]
* [Capability/Feature 3]

#### Out of Scope (Explicitly Excluded)

* [Item 1] → [Where it lives instead]
* [Item 2] → [Why excluded]

#### Future Considerations (Post-Initiative)

* [Future enhancement 1]
* [Future enhancement 2]

---

### 9. 📅 Milestones & Timeline

| Milestone | Description | Target Date | Status |
|-----------|-------------|-------------|--------|
| M0 | Initiative Kickoff | [Date] | ✅ |
| M1 | [First major milestone] | [Date] | ⏳ |
| M2 | [Second major milestone] | [Date] | ⏳ |
| M3 | [Final delivery] | [Date] | ⏳ |

**Quarterly View:**

```
Q1 2026: [Focus/Deliverables]
Q2 2026: [Focus/Deliverables]
```

---

### 10. 👥 Stakeholders & RACI

| Role | Person/Team | R/A/C/I |
|------|-------------|---------|
| Product Owner | [Name] | A |
| Tech Lead | [Name] | R |
| Engineering | [Squad] | R |
| Design | [Name] | R |
| Data | [Name] | C |
| Sales | [Name] | I |
| Executive Sponsor | [Name] | I |

**Legend:** R = Responsible, A = Accountable, C = Consulted, I = Informed

---

### 11. 📦 Dependencies & Risks

#### Dependencies

| Dependency | Owner | Status | Impact if Delayed |
|------------|-------|--------|-------------------|
| [Dependency 1] | [Team] | 🟢/🟡/🔴 | [Impact] |
| [Dependency 2] | [Team] | 🟢/🟡/🔴 | [Impact] |

#### Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| [Risk 1] | High/Med/Low | High/Med/Low | [Plan] |
| [Risk 2] | High/Med/Low | High/Med/Low | [Plan] |

---

### 12. 💰 Investment & Resources

| Resource Type | Allocation | Duration |
|---------------|------------|----------|
| Engineering | [X FTEs / % of squad] | [Quarters] |
| Design | [X FTEs / % of squad] | [Quarters] |
| Data | [X FTEs / % of squad] | [Quarters] |
| External Cost | [Budget if any] | [One-time/Recurring] |

**ROI Estimate (if applicable):**

* Investment: [Total cost/effort]
* Expected Return: [Revenue/Savings]
* Payback Period: [Timeline]

---

### 13. 🎨 Resources & Documentation

| Resource | Link | Status |
|----------|------|--------|
| PRD / Strategy Doc | [Link] | [Draft/Final] |
| Research & Discovery | [Link] | [Complete/In Progress] |
| Figma / Design | [Link] | [TBD/In Progress/Final] |
| Technical RFC | [Link] | [TBD/Approved] |
| Data Dashboard | [Link] | [TBD/Live] |

---

## Example Initiative

### 1. 🎯 Initiative Overview

| Field | Value |
|-------|-------|
| **Initiative Name** | Sales Funnel Automation & Lead Qualification |
| **Owner** | Ignacio De La Cuba |
| **Sponsor** | VP of Sales |
| **Squad(s)** | DS & AI Squad |
| **Timeline** | Q1 2026 → Q2 2026 |
| **Status** | 🟢 On Track |

### 2. 🧭 Strategic Alignment

#### OKR Connection

| Level | Objective | Key Result |
|-------|-----------|------------|
| **Company** | Achieve profitable growth | Increase sales efficiency by 30% |
| **Team** | Automate sales operations | Reduce unqualified 1:1 calls by 30% |

#### Strategic Theme

* [x] Revenue Growth
* [x] Operational Efficiency

**Strategic Rationale:**

Our sales team spends significant time on calls with unqualified leads, reducing their capacity to close deals. By automating lead qualification and intelligent routing, we can ensure closers only speak with high-intent, qualified prospects—directly improving conversion rates and revenue per sales rep.

### 3. 🚨 Problem Space

#### Current State

* **What exists today?** - Leads book 1:1 calls directly after webinars with no filtering
* **What's the pain?** - Closers waste time on calls that can never convert
* **Who feels the pain?** - Sales closers, Sales managers, SDRs
* **What's the cost?** - 316 wasted calls/month, ~79% of closer time on unqualified leads

#### Root Cause

* No qualification gate between webinar attendance and 1:1 booking
* Pre-webinar forms create friction and data isn't actioned
* Manual qualification by SDRs is slow and inconsistent

#### Evidence

| Metric | Current State | Source |
|--------|---------------|--------|
| 1:1 Calls Booked | 400/month | MBR Dec 2025 |
| Engagements from Calls | 84/month (21%) | MBR Dec 2025 |
| Wasted Calls | ~316/month | Calculated |

### 4. 💡 Strategic Hypothesis

```
We believe that implementing AI-powered lead qualification via WhatsApp
Will result in 30%+ closer conversion rates (up from 21%)
For sales closers and qualified leads
Because unqualified leads will be filtered before booking
We will know we're successful when 1:1 bookings drop to 280/month while maintaining 84+ engagements
```

**Key Assumptions:**

1. Leads will engage with WhatsApp qualification flow (>60% response rate)
2. Scoring criteria accurately predicts conversion likelihood
3. Routing to alternatives (Value Hero) retains mid-tier leads

### 5. 🎯 Success Metrics

#### Primary Metrics (North Star)

| Metric | Baseline | Target | Timeline |
|--------|----------|--------|----------|
| Closer Conversion Rate | 21% | 30%+ | Q2 2026 |

#### Secondary Metrics (Supporting)

| Metric | Baseline | Target | Timeline |
|--------|----------|--------|----------|
| 1:1 Calls Booked | 400/month | 280/month | Q2 2026 |
| Engagements/month | 84 | 84+ | Q2 2026 |
| Qualification Response Rate | N/A | >60% | Q1 2026 |

#### Guardrail Metrics (Don't Break)

| Metric | Threshold | Action if Breached |
|--------|-----------|-------------------|
| Total Engagements | Min 80/month | Pause and diagnose routing |
| Lead Satisfaction | NPS > 30 | Review qualification UX |

### 6. 👤 Target Users

| Persona | Description | Primary Pain Point | Success Looks Like |
|---------|-------------|-------------------|-------------------|
| Closer | Sales rep doing 1:1 calls | Wasted time on bad leads | Only qualified leads on calendar |
| Sales Manager | Manages closer team | No visibility into lead quality | Full lead context in HubSpot |
| Lead | Webinar attendee | Unclear next steps | Fast, personalized routing |

### 7. 📦 Epics in this Initiative

| # | Epic Name | Problem | Owner | Status | Target Date |
|---|-----------|---------|-------|--------|-------------|
| 1 | Lead Qualification Agent | No filtering before 1:1 booking | Ignacio | In Progress | Q1 2026 |
| 2 | Engagement Agent | Qualified leads wait for closer | Ignacio | Planning | Q2 2026 |
| 3 | Sales Analytics Dashboard | No visibility into funnel | Data Team | Draft | Q2 2026 |

### 8. 🗺️ Scope & Boundaries

#### In Scope (This Initiative)

* WhatsApp-based lead qualification
* Lead scoring and intelligent routing
* HubSpot integration for lead profiles
* Value Hero routing for mid-tier leads

#### Out of Scope (Explicitly Excluded)

* Pre-webinar form removal → Separate project
* Payment processing → Future initiative
* Call recording/analysis → Future initiative

### 9. 📅 Milestones & Timeline

| Milestone | Description | Target Date | Status |
|-----------|-------------|-------------|--------|
| M0 | Initiative Kickoff | Jan 15, 2026 | ✅ |
| M1 | Qualification Agent MVP Live | Feb 28, 2026 | ⏳ |
| M2 | Engagement Agent MVP Live | Apr 30, 2026 | ⏳ |
| M3 | Full Rollout + Analytics | May 31, 2026 | ⏳ |

### 10. 👥 Stakeholders & RACI

| Role | Person/Team | R/A/C/I |
|------|-------------|---------|
| Product Owner | Ignacio | A |
| Tech Lead | [TBD] | R |
| DS & AI Squad | Engineering | R |
| Sales Ops | Revenue Ops | C |
| VP Sales | Executive | I |

### 11. 📦 Dependencies & Risks

#### Dependencies

| Dependency | Owner | Status | Impact if Delayed |
|------------|-------|--------|-------------------|
| WhatsApp Business API | DevOps | 🟢 Ready | Blocks MVP |
| HubSpot API access | Architecture | 🟢 Ready | Blocks lead sync |
| Scoring criteria sign-off | Sales Ops | 🟡 In Progress | Delays routing |

#### Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Low WhatsApp engagement | Medium | High | A/B test messaging, add SMS fallback |
| Scoring inaccuracy | Medium | High | Start with human review, iterate |

### 12. 💰 Investment & Resources

| Resource Type | Allocation | Duration |
|---------------|------------|----------|
| Engineering | 2 FTEs (DS & AI Squad) | 2 Quarters |
| Design | 0.5 FTE | Q1 only |
| External Cost | WhatsApp API (~$500/month) | Recurring |

### 13. 🎨 Resources & Documentation

| Resource | Link | Status |
|----------|------|--------|
| Strategy Doc | [Link] | Final |
| MBR December 2025 | [Link] | Reference |
| Figma Flows | [TBD] | In Progress |

---

## Writing Guidelines

### Initiative Name

* Should be outcome-focused, not feature-focused
* Good: "Sales Funnel Automation & Lead Qualification"
* Bad: "Build WhatsApp Bot"

### Strategic Alignment

* Every initiative MUST connect to an OKR
* If it doesn't connect, question if it should be an initiative
* Be explicit about the strategic theme

### Problem Space

* Lead with quantified pain
* Include data sources for credibility
* Explain root cause, not just symptoms

### Success Metrics

* Primary metric = the ONE number that matters most
* Secondary metrics = supporting indicators
* Guardrails = things we must NOT break

### Epics

* Each initiative should have 2-5 Epics
* Epics should be sequenced logically
* Each Epic solves a distinct problem

### Quality Checklist

Before finalizing any Initiative, verify:

* ✅ Connects directly to company/team OKR
* ✅ Problem is quantified with data sources
* ✅ Hypothesis is testable with clear success criteria
* ✅ Primary metric has baseline and target
* ✅ Epics are defined and sequenced
* ✅ Scope boundaries are explicit
* ✅ Dependencies identified with owners
* ✅ Stakeholder RACI is complete
* ✅ Timeline has clear milestones
* ✅ Executive sponsor identified
