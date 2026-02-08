# Claudio

**Asistente de productividad para el equipo de Product & Technology de PropHero.**

Claudio es un sistema de asistencia basado en Claude que integra multiples herramientas (MCPs) para automatizar tareas de product management, desarrollo y comunicacion. Funciona a traves de Slack, Telegram, Terminal y una interfaz web.

![Arquitectura de Claudio](./claudio.png)

---

## Tabla de Contenidos

- [Arquitectura](#arquitectura)
- [MCPs Integrados](#mcps-integrados)
- [Canales de Acceso](#canales-de-acceso)
- [Quick Start](#quick-start)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Configuracion de MCPs](#configuracion-de-mcps)
- [Workflows](#workflows)
- [Documentacion](#documentacion)
- [Mantenimiento](#mantenimiento)

---

## Arquitectura

Claudio se compone de tres capas:

| Capa | Descripcion | Ubicacion |
|------|-------------|-----------|
| **Cerebro** | Instrucciones, contextos, guias, workflows | `docs/` |
| **Manos** | MCPs para ejecutar acciones (ClickUp, GitHub, Slack, etc.) | `mcp/` |
| **Bocas** | Canales de acceso (Telegram, Slack, Terminal, Web) | `channels/` |

### Flujo de Trabajo

```
Definition → Initiative → Epic → User Story → Execution
```

### Usuarios

| Rol | Uso Principal |
|-----|---------------|
| **Product Manager** | Crear Initiatives, Epics, User Stories en ClickUp |
| **Engineer / Dev** | Ejecutar codigo, gestionar PRs, debugging |

---

## MCPs Integrados

| MCP | Proposito | Estado |
|-----|-----------|--------|
| **ClickUp** | Product Management (Initiatives, Epics, User Stories) | Activo |
| **GitHub** | Codigo, PRs, Issues | Activo |
| **Slack** | Comunicacion y notificaciones | Activo |
| **Google Docs** | Documentacion y specs | Activo |
| **Google Sheets** | Datos y reportes | Activo |
| **Granola** | Meeting notes, transcripciones | Activo |
| **Gmail** | Email | Proximo |
| **Slides** | Presentaciones | Proximo |

Cada MCP tiene su guia en [`docs/integrations/`](./docs/integrations/).

---

## Canales de Acceso

| Canal | Descripcion | Estado | Docs |
|-------|-------------|--------|------|
| **Terminal** | Claude Code CLI / Cursor IDE | Activo | [Guia](./docs/integrations/terminal.md) |
| **Telegram** | Bot para acceso movil | Activo | [README](./channels/telegram/README.md) |
| **Slack** | DMs y menciones en canales | Activo | [README](./channels/slack/README.md) |
| **Web Dashboard** | Monitoreo de MCPs | Activo | [README](./channels/web/README.md) |
| **WhatsApp** | Bot movil | Proximo | -- |

---

## Quick Start

### Prerrequisitos

- **Python 3.10+**
- **Claude Code CLI** instalado (`claude` en PATH) -- para bots de Telegram/Slack
- **Cursor IDE** -- para uso directo como asistente
- **Node.js 18+** -- para MCPs basados en npx

### 1. Clonar y configurar

```bash
git clone <repo-url> claudio
cd claudio

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias base
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus valores
```

### 3. Usar con Cursor (recomendado)

1. Abre este proyecto en Cursor IDE
2. Copia la config de MCPs: usa `mcp/cursor-config.json` como referencia para `~/.cursor/mcp.json`
3. Reinicia Cursor -- Claudio ya esta listo

### 4. Usar con Telegram Bot

```bash
pip install -r channels/telegram/requirements.txt

# Configura TELEGRAM_BOT_TOKEN y ALLOWED_USER_IDS en .env
./channels/telegram/start.sh
```

Ver configuracion completa en [`channels/telegram/README.md`](./channels/telegram/README.md).

### 5. Usar con Slack Bot

```bash
pip install -r channels/slack/requirements.txt

# Configura SLACK_BOT_TOKEN y SLACK_APP_TOKEN en .env
./channels/slack/start.sh
```

Ver configuracion completa en [`channels/slack/README.md`](./channels/slack/README.md).

### 6. Web Dashboard

```bash
pip install -r channels/web/requirements.txt
./channels/web/start.sh
# Abre http://localhost:8000
```

---

## Estructura del Proyecto

```
claudio/
├── CLAUDE.md                  # Identidad e instrucciones de Claudio
├── README.md                  # Este archivo
├── claudio.png                # Diagrama de arquitectura
├── requirements.txt           # Dependencias compartidas
├── .env.example               # Variables de entorno (template)
├── kill_bot_processes.sh      # Utilidad para detener bots
│
├── docs/                      # CEREBRO - Documentacion
│   ├── README.md              # Indice de documentacion
│   ├── INITIATIVE_CLAUDIO.md  # Initiative del proyecto
│   ├── integrations/          # Guia por cada MCP
│   │   ├── clickup/
│   │   │   ├── config.md      # IDs y configuracion
│   │   │   ├── guide.md       # Guia de uso
│   │   │   └── templates/     # Templates (Initiative, Epic, US)
│   │   ├── github/guide.md
│   │   ├── slack/guide.md
│   │   ├── google-docs/guide.md
│   │   ├── google-sheets/guide.md
│   │   ├── granola/guide.md
│   │   └── terminal.md
│   ├── workflows/             # Workflows multi-MCP
│   │   ├── daily-standup.md
│   │   ├── create-initiative.md
│   │   └── sprint-report.md
│   └── design-system/
│       └── reference.md       # Design system de PropHero
│
├── mcp/                       # MANOS - Configuracion de MCPs
│   ├── README.md
│   ├── cursor-config.json     # Config para Cursor IDE
│   ├── claude-code-config.example.json  # Config para Claude Code CLI
│   └── servers/README.md      # Docs de servidores MCP
│
└── channels/                  # BOCAS - Interfaces de acceso
    ├── telegram/              # Bot de Telegram
    │   ├── bot.py
    │   ├── requirements.txt
    │   ├── start.sh
    │   └── .env.example
    ├── slack/                 # Bot de Slack
    │   ├── bot.py
    │   ├── requirements.txt
    │   ├── start.sh
    │   └── .env.example
    └── web/                   # Dashboard web (FastAPI)
        ├── app.py
        ├── templates/dashboard.html
        ├── requirements.txt
        └── start.sh
```

---

## Configuracion de MCPs

Los MCPs se configuran de forma diferente segun el cliente:

| Cliente | Archivo de Config | Referencia |
|---------|-------------------|------------|
| **Cursor IDE** | `~/.cursor/mcp.json` | [`mcp/cursor-config.json`](./mcp/cursor-config.json) |
| **Claude Code CLI** | `~/.claude.json` | [`mcp/claude-code-config.example.json`](./mcp/claude-code-config.example.json) |

Ver detalles en [`mcp/README.md`](./mcp/README.md).

### Resumen de servidores

| MCP | Tipo | Paquete / URL |
|-----|------|---------------|
| ClickUp | npx | `@taazkareem/clickup-mcp-server@latest` |
| GitHub | Remote | `https://api.githubcopilot.com/mcp/` |
| Slack | npx | `slack-mcp-server@latest` |
| Google Docs | Local | Node server (OAuth) |
| Granola | Python | `granola_mcp.mcp` |

---

## Workflows

Workflows que combinan multiples MCPs para tareas recurrentes:

| Workflow | MCPs | Trigger |
|----------|------|---------|
| [Daily Standup](./docs/workflows/daily-standup.md) | Slack + Google Docs | "Crea las notas para la daily" |
| [Create Initiative](./docs/workflows/create-initiative.md) | ClickUp + Google Docs | "Crea una initiative para X" |
| [Sprint Report](./docs/workflows/sprint-report.md) | ClickUp + Slack + Sheets | "Genera el reporte del sprint" |

Ver todos los workflows en [`docs/workflows/`](./docs/workflows/).

---

## Documentacion

| Recurso | Descripcion |
|---------|-------------|
| [`CLAUDE.md`](./CLAUDE.md) | Identidad, reglas e instrucciones de Claudio |
| [`docs/INITIATIVE_CLAUDIO.md`](./docs/INITIATIVE_CLAUDIO.md) | Initiative del proyecto en ClickUp |
| [`docs/integrations/`](./docs/integrations/) | Guias detalladas por cada MCP |
| [`docs/workflows/`](./docs/workflows/) | Workflows multi-MCP |
| [`docs/design-system/reference.md`](./docs/design-system/reference.md) | Design System de PropHero |
| [`mcp/README.md`](./mcp/README.md) | Configuracion de servidores MCP |

---

## Mantenimiento

### Cada Quarter
- Actualizar ID de lista de Epics en [`docs/integrations/clickup/config.md`](./docs/integrations/clickup/config.md)

### Cuando cambie un MCP
- Actualizar la guia en `docs/integrations/{mcp}/guide.md`
- Actualizar config en `mcp/cursor-config.json` y `mcp/claude-code-config.example.json`

### Cuando cambien reglas de comportamiento
- Actualizar `CLAUDE.md`

### Agregar un nuevo MCP
1. Agregar config en `mcp/cursor-config.json`
2. Crear guia en `docs/integrations/{nombre}/guide.md`
3. Actualizar `CLAUDE.md` con resumen
4. Actualizar este README

### Agregar un nuevo canal
1. Crear directorio en `channels/{nombre}/`
2. Incluir `bot.py`, `requirements.txt`, `start.sh`, `.env.example`, `README.md`
3. Actualizar este README

---

*Claudio - Hecho con Claude para el equipo de P&T de PropHero.*
