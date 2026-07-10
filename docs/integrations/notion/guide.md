# Notion Integration

Notion is the **source of truth** for Growth experiments in Claudio. Use it to create, review, update, and close experiment pages in the Ideas-Experiments database.

---

## Setup

### Cursor IDE

The Notion MCP is available via the **notion-workspace** plugin or by adding to `mcp/cursor-config.json`:

```json
"notion": {
  "url": "https://mcp.notion.com/mcp"
}
```

### Claude Code / Slack / Telegram bots

Same entry in `mcp/cursor-config.json`. On first use, complete **OAuth** in the browser when Claude Code prompts for Notion authentication.

### Grant access to Ideas-Experiments

1. Open the [Ideas-Experiments database](https://app.notion.com/p/Ideas-Experiments-38a64a4709298022b997c86f7a583694).
2. Share the page/database with the Notion MCP integration (or ensure your OAuth account has access).
3. Run `notion-fetch` on the DB URL and copy the `collection://` ID into `docs/integrations/notion/config.md`.

---

## Configuration

| File | Purpose |
|------|---------|
| [`config.md`](./config.md) | Workspace IDs, experiments DB, stakeholders, lifecycle |
| [`templates/experiment.md`](./templates/experiment.md) | Mandatory page structure |

---

## Tools (Notion MCP)

| Tool | Use for |
|------|---------|
| `notion-fetch` | Load page/DB schema; use `id: "self"` for workspace identity |
| `notion-search` | Find experiments by name or topic |
| `notion-create-pages` | Create new experiment rows in the DB |
| `notion-update-page` | Update properties, sign-offs, results |
| `notion-query-data-sources` | List/filter experiments (SQL or view mode; Business+ for SQL) |
| `notion-get-users` | Resolve stakeholder Notion user IDs |
| `notion-update-data-source` | Add missing DB columns |

Read the enhanced markdown spec before writing page content: resource `notion://docs/enhanced-markdown-spec`.

---

## Standard workflows

### Read

```
notion-search → notion-fetch(page or database) → synthesize
```

### Create experiment

```
Read config.md + experiment template
→ notion-fetch(database) for schema
→ Build draft (show user)
→ notion-create-pages(parent: data_source_id, properties, content)
→ Return Notion link
```

### Update / conclude

```
notion-search or notion-fetch by URL
→ notion-update-page (properties + append results/learnings)
→ Validate status transition rules from config.md
```

---

## Claudio Growth mode rules

1. **Always** read `docs/integrations/notion/config.md` before creating or updating experiments.
2. **Always** use `docs/integrations/notion/templates/experiment.md` for page body.
3. **Never** create an experiment without: Problema, Hipótesis, Métricas, Metodología.
4. **Confirm** draft with the user before `notion-create-pages` or substantive `notion-update-page`.
5. **Compute** required sign-offs from Area + Tags using the stakeholder map in `config.md`.
6. **Block** transition to `Running` until all required sign-offs are `Approved`.

---

## Triggers (natural language)

| Intent | Example |
|--------|---------|
| Create | "Crea un experimento para mejorar show-up rate" |
| Review prep | "Prepárame la review de experimentos" |
| Sign-off status | "¿Qué experimentos necesitan sign-off?" |
| Update results | "Actualiza el experimento X con estos resultados" |
| Close | "Cierra el experimento X como Scaled" |

See `docs/workflows/growth/` for step-by-step workflows.

---

## Limitations

- OAuth is per-user; bots use the authenticated Claude Code session.
- SQL queries on databases require Notion Business+ with Notion AI.
- If the DB returns 404, the integration lacks access — share the database or switch workspace.

---

## Related

- Skill: `.claude/skills/experiment-manager/SKILL.md`
- Workflows: `docs/workflows/growth/`
- CLAUDE.md: Modo Growth (Experimentos)
