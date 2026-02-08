# Documentacion de Claudio

El cerebro de Claudio -- toda la documentacion, guias, configuracion y workflows.

## Estructura

```
docs/
├── README.md                        ← Este archivo
├── INITIATIVE_CLAUDIO.md            ← Initiative del proyecto
│
├── integrations/                    ← Guias por MCP
│   ├── clickup/
│   │   ├── config.md               ← IDs de listas y espacios
│   │   ├── guide.md                ← Guia de uso
│   │   └── templates/              ← Templates para artifacts
│   │       ├── initiative.md
│   │       ├── epic.md
│   │       └── user-story.md
│   ├── github/guide.md             ← Codigo y PRs
│   ├── slack/guide.md              ← Comunicacion
│   ├── google-docs/guide.md        ← Documentacion
│   ├── google-sheets/guide.md      ← Datos y reportes
│   ├── granola/guide.md            ← Meeting notes
│   └── terminal.md                 ← Comandos locales
│
├── workflows/                       ← Workflows multi-MCP
│   ├── README.md
│   ├── daily-standup.md
│   ├── create-initiative.md
│   └── sprint-report.md
│
└── design-system/
    └── reference.md                 ← Design system de PropHero
```

## Como funciona

### CLAUDE.md (Raiz del proyecto)
Define la **identidad** de Claudio:
- Personalidad y tono
- Principios de comportamiento
- Resumen de capacidades
- Reglas de interaccion por contexto

### docs/integrations/
Documenta **cada integracion MCP en detalle**:
- Configuracion y setup
- Capacidades especificas
- Reglas de comportamiento
- Ejemplos de uso

### docs/integrations/clickup/
Configuracion especifica de ClickUp para PropHero:
- IDs de listas y espacios (`config.md`)
- Templates para Initiatives, Epics, User Stories (`templates/`)

### docs/workflows/
Workflows que combinan multiples MCPs:
- Daily Standup (Slack + Google Docs)
- Create Initiative (ClickUp + Google Docs)
- Sprint Report (ClickUp + Slack + Sheets)

### docs/design-system/
Referencia del Design System de PropHero para reviews de UI/UX.

## Agregar nueva integracion

1. Crear `docs/integrations/{nombre}/guide.md` con:
   - Setup y configuracion
   - Capacidades
   - Reglas
   - Ejemplos

2. Actualizar `CLAUDE.md` con resumen de la integracion

3. Agregar config MCP en `mcp/cursor-config.json`

## Mantener actualizado

### Cada Quarter
- Actualizar ID de Epics en `docs/integrations/clickup/config.md`

### Cuando cambie un MCP
- Actualizar guia correspondiente en `docs/integrations/`

### Cuando cambie el comportamiento
- Actualizar `CLAUDE.md`
