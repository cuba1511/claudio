# Claudio

Asistente de productividad para el equipo de Product & Technology de PropHero.

## Qué es Claudio

Claudio es un sistema de asistencia basado en Claude que integra múltiples herramientas (MCPs) para automatizar tareas de product management, desarrollo y comunicación.

## Arquitectura

| Componente | Rol | Ubicación |
|------------|-----|-----------|
| **Cerebro** | Instrucciones, contextos, guías | `docs/` |
| **Manos** | MCPs (ClickUp, GitHub, Slack, Docs, Sheets) | `mcp/` |
| **Bocas** | Canales de acceso (Telegram, Cursor) | `channels/` |

## MCPs Integrados

- **ClickUp** - Product Management (Initiatives, Epics, User Stories)
- **GitHub** - Código, PRs, Issues
- **Slack** - Comunicación y notificaciones
- **Google Docs** - Documentación y specs
- **Google Sheets** - Datos y reportes

## Canales de Acceso

- **Cursor** - IDE con acceso a todos los MCPs
- **Telegram** - Bot para acceso móvil

## Quick Start

### Usar con Cursor

1. Abre este proyecto en Cursor
2. Los MCPs se configuran en `~/.cursor/mcp.json`
3. Referencia: `mcp/cursor-config.json`

### Usar con Telegram

```bash
cd channels/telegram
pip install -r requirements.txt
python bot.py
```

## Estructura

```
claudio/
├── CLAUDE.md           # Instrucciones para Claude
├── docs/
│   ├── integrations/   # Guías por MCP
│   └── workflows/      # Workflows multi-MCP
├── mcp/
│   ├── cursor-config.json
│   └── servers/
└── channels/
    ├── telegram/
    └── cursor/
```

## Documentación

- [Instrucciones de Claudio](./CLAUDE.md)
- [Integración ClickUp](./docs/integrations/clickup/guide.md)
- [Integración Slack](./docs/integrations/slack/guide.md)
- [Workflows](./docs/workflows/README.md)
