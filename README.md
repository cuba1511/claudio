# Claudio

**Asistente de productividad del equipo de Product & Technology de PropHero.**

Integra MCPs (ClickUp, GitHub, Slack, Google Docs/Sheets, BigQuery, Granola) para automatizar tareas de product management, desarrollo y comunicación. Accesible desde Terminal, Slack, Telegram y Web.

![Arquitectura de Claudio](./docs/images/claudio.png)

---

## Quick Start

### Prerrequisitos

- Python 3.10+, Node.js 18+
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) (para bots)
- Cursor IDE (para uso directo)

### Setup

```bash
git clone <repo-url> claudio && cd claudio
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # editar con tus valores
```

### Uso con Cursor (recomendado)

1. Abre el proyecto en Cursor
2. Configura MCPs usando `mcp/cursor-config.json` como referencia para `~/.cursor/mcp.json`
3. Reinicia Cursor — listo

### Canales

| Canal | Iniciar | Docs |
|-------|---------|------|
| **Telegram** | `./channels/telegram/start.sh` | [README](./channels/telegram/README.md) |
| **Slack** | `./channels/slack/start.sh` | [README](./channels/slack/README.md) |
| **Web Dashboard** | `./channels/web/start.sh` → `localhost:8000` | [README](./channels/web/README.md) |

Cada canal tiene su propio `requirements.txt` — instala antes de iniciar.

---

## Estructura del Proyecto

```
claudio/
├── CLAUDE.md              # Identidad e instrucciones de Claudio
├── docs/                  # Cerebro — documentación y guías
│   ├── images/            # Assets (claudio.png)
│   ├── integrations/      # Guía por MCP (clickup, github, slack, etc.)
│   ├── workflows/         # Workflows multi-MCP
│   │   ├── product/       # daily-standup, create-initiative, sprint-report
│   │   └── revenue/       # funnel-master, hook-script-creator
│   └── design-system/     # Design system de PropHero
├── mcp/                   # Manos — configuración de MCPs
├── channels/              # Bocas — interfaces (telegram, slack, web)
└── scripts/               # Cron jobs automatizados
    ├── weekly-bot-report.sh
    └── monthly-ds-ai-report.sh
```

---

## Workflows

| Workflow | MCPs | Trigger |
|----------|------|---------|
| [Daily Standup](./docs/workflows/product/daily-standup.md) | Slack + Docs | "Crea las notas para la daily" |
| [Create Initiative](./docs/workflows/product/create-initiative.md) | ClickUp + Docs | "Crea una initiative para X" |
| [Sprint Report](./docs/workflows/product/sprint-report.md) | ClickUp + Slack + Sheets | "Genera el reporte del sprint" |
| [Weekly Bot Report](./docs/workflows/weekly-bot-report.md) | Sheets + Gmail | Cron: lunes 9 AM |
| [Monthly DS&AI Report](./docs/workflows/monthly-ds-ai-report.md) | ClickUp + Docs | Cron: día 1 del mes |
| [Funnel Master](./docs/workflows/revenue/funnel-master.md) | Sheets + BigQuery | "Analiza el funnel" |
| [Hook Script Creator](./docs/workflows/revenue/hook-script-creator-v3.md) | Docs | "Crea hook scripts" |

---

## Contribuir

### Agregar un MCP

1. Agregar config en `mcp/cursor-config.json`
2. Crear guía en `docs/integrations/{nombre}/guide.md`
3. Actualizar `CLAUDE.md`

### Agregar un workflow

1. Crear `.md` en `docs/workflows/{área}/`
2. Si requiere cron, agregar script en `scripts/`

### Agregar un canal

1. Crear directorio en `channels/{nombre}/` con `bot.py`, `requirements.txt`, `start.sh`, `.env.example`
2. Documentar en `channels/{nombre}/README.md`

### Mantenimiento periódico

- **Cada quarter**: actualizar ID de lista de Epics en [`docs/integrations/clickup/config.md`](./docs/integrations/clickup/config.md)
- **Si cambia un MCP**: actualizar guía y configs en `mcp/`
- **Si cambian reglas**: actualizar `CLAUDE.md`

---

*Claudio — Hecho con Claude para el equipo de P&T de PropHero.*
