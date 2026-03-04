# Epic Template

Epics live under their parent Initiative in the current quarter's Epics list (e.g. `901216091884` for Q2 2026).

Each Epic solves a distinct problem and has a clear hypothesis, measurable outcomes, and defined scope.

---

## Structure

---

### 1. 🚨 Problem to be Solved

[Describe the current situation and pain clearly. Be specific with numbers when available.]
[Include who is affected and what the quantified impact is.]
[Explain current workarounds and why they're insufficient.]

**Source:** [Data source, e.g. MBR December 2025]

---

### 2. 💡 Hypothesis

If we [specific action/solution],

Then [expected outcome(s)]:
- [Goal 1]
- [Goal 2]

Because [reasoning / mechanism — the causal link between action and outcome].

---

### 3. 🎯 Business Outcome

**Primary: [Main goal]**
- [Metric 1]: [baseline] → [target]
- [Metric 2]: [baseline] → [target]

**Secondary: [Secondary goal]**
- [Metric or capability unlocked]
- [Future path enabled]

---

### 4. 👤 User Outcome

**For [Persona 1]:**
- [What they can do now that they couldn't before]
- [Pain point eliminated]

**For [Persona 2]:**
- [Capability gained]
- [Experience improved]

**For [Persona 3]:**
- [Change in their workflow]

---

### 5. 📝 User Stories for this Epic

(See subtasks)

---

### 6. 🗺️ Scope

**Use Cases IN Scope**
- [Use case 1]
- [Use case 2]
- [Use case 3]

**Use Cases PARKED (Out of Scope)**
- [Parked item] → [Where it lives / why excluded]
- [Parked item] → [Future epic or separate initiative]

---

### 7. 📊 Business KPIs Impacted

**Flow Diagram**

```
[Starting Point / Trigger]
        ↓
[Action / Change 1]
        ↓
[Action / Change 2]
        ↓
[Intermediate Metric]
        ↓
[Final Business KPI]
```

---

### 8. 📦 Dependencies

| Dependency | Owner | Status | Blocking? |
|------------|-------|--------|-----------|
| [Dependency 1] | [Team/Person] | ✅ Ready / ⏳ In Progress / ❌ Blocked | Yes/No |
| [Dependency 2] | [Team/Person] | [Status] | Yes/No |

---

### 10. 🔗 Related Epics

| Epic | Relationship | Status |
|------|--------------|--------|
| [Epic Name] | Depends on / Enables / Parallel | [Status] |

---

### 11. 🎨 Design & Documentation

- **Figma File:** [Link or TBD]
- **Documentation:** [Link or TBD]

---

## Example

### 1. 🚨 Problem to be Solved

After attending a webinar, leads can book a 1:1 call with no qualification or filtering. The booking page has no form, so anyone with the link can book regardless of fit (wrong country, insufficient funds, no delegation intent, not ready to invest).

As a result, closers spend time on calls that could never convert. In December 2025, we booked 400 1:1 calls to get 84 engagements (21% conversion), meaning ~316 calls were wasted on unqualified or low-intent leads.

Pre-webinar forms exist but create friction and the data isn't used → we ask "how much money do you have?" but never act on it.

**Source:** MBR December 2025

### 2. 💡 Hypothesis

If we implement a WhatsApp-based qualification agent that asks structured questions after webinar attendance, scores leads based on fit criteria, and routes them intelligently before they can book a 1:1,

Then we will achieve two goals:
- **Efficiency:** Closers only speak to qualified, high-intent leads
- **Revenue Optimization:** Every lead gets matched to the product/funnel where they have the highest conversion probability

Because unqualified leads will be filtered automatically and routed to the right alternative path.

### 3. 🎯 Business Outcome

**Primary: Improve 1:1 Efficiency**
- Reduce 1:1 bookings: 400 → 280/month (30% reduction)
- Increase closer conversion rate: 21% → 30%+
- Maintain or increase 84 engagements/month with fewer calls

**Secondary: Intelligent Lead Routing**
- Route leads to the right product/funnel, not just filter them out
- Create multiple conversion paths based on lead profile
- Enable future direct-engagement path via Engagement Agent

### 4. 👤 User Outcome

**For Closers:**
- Receive only qualified leads with full context (country, budget, timeline, intent)
- Don't waste time on calls that could never convert

**For Sales Managers:**
- See lead profiles and routing decisions in HubSpot
- Analyze funnel performance and optimize scoring

**For SDRs:**
- Receive pre-qualified leads for nurture
- No longer manually qualify leads → agent handles it automatically

**For Leads:**
- Get matched to the right product/funnel without waiting for manual outreach
- Better experience = higher satisfaction and conversion

### 5. 📝 User Stories for this Epic

(See subtasks)

### 6. 🗺️ Scope

**Use Cases IN Scope**
- Lead attends webinar → receives WhatsApp qualification flow
- Lead completes qualification → gets scored and routed
- Lead routed to 1:1 booking (qualified, wants call)
- Lead routed to Engagement Agent (qualified, ready now)
- Lead routed to Value Hero (mid-tier, only €30k-€50k)
- Lead routed to SDR for nurture (low intent, not ready)
- Lead discarded (unqualified)
- Lead doesn't respond → follow-up and escalation

**Use Cases PARKED (Out of Scope)**
- Engagement Agent functionality → separate epic
- Closing deals (payment link) → Engagement Agent scope
- Call qualification → WhatsApp only for MVP
- Pre-webinar form removal → separate implementation

### 7. 📊 Business KPIs Impacted

**Flow Diagram**

```
Webinar Attendance
        ↓
HubSpot workflow (message)
        ↓ ← On lead reply
Qualification Agent (WhatsApp)
        ↓
Lead Scored & Profiled
        ↓
    ┌───────────────────────────────────────┐
    │         INTELLIGENT ROUTING           │
    ├───────────┬───────────┬───────────┬───┤
    ↓           ↓           ↓           ↓
  1:1 Call   Engagement  Value Hero   SDR/Nurture
  (Closer)    Agent       Funnel      Pipeline
    ↓           ↓           ↓           ↓
  Higher     Direct      Right       Long-term
  Conversion  Close      Product     Revenue
```

### 8. 📦 Dependencies

| Dependency | Owner | Status | Blocking? |
|------------|-------|--------|-----------|
| WhatsApp Business API | DevOps | ✅ Ready | No |
| HubSpot API Integration | Architecture | ⏳ In Progress | Yes |
| Scoring Criteria Definition | Sales Ops | ✅ Ready | No |

### 10. 🔗 Related Epics

| Epic | Relationship | Status |
|------|--------------|--------|
| Engagement Agent | Enables (downstream) | Planning |
| HubSpot Foundations | Depends on | In Progress |

### 11. 🎨 Design & Documentation

- **Figma File:** TBD
- **Documentation:** TBD

---

## Notes

- Section numbering: 1-8, then 10-11 (no section 9 — kept for consistency with ClickUp)
- User Stories are always listed as subtasks in ClickUp, not written inline
- The flow diagram in section 7 is key — shows causality, not just metrics
- Always specify data sources in section 1
- Scope section prevents scope creep — be explicit about what's parked and where it lives
