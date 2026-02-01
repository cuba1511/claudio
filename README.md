# Claudio

Asistente de productividad para el equipo de Product & Technology de PropHero.

![Arquitectura de Claudio](./claudio.png)

## Qué es Claudio

Claudio es un sistema de asistencia basado en Claude que integra múltiples herramientas (MCPs) para automatizar tareas de product management, desarrollo y comunicación.

### Usuarios
- **Product Manager** - Crea Initiatives, Epics, User Stories
- **Engineer / Dev** - Ejecuta código, gestiona PRs, debugging

### Canales de Entrada
- **Slack** - Mensajes directos
- **Terminal** - Claude Code CLI / Cursor
- **WhatsApp** - Bot (próximamente)
- **Telegram** - Bot móvil

### Flujo de Trabajo
```
Definition → Initiative → Epic → User Story → Execution
```

## Arquitectura

| Componente | Rol | Ubicación |
|------------|-----|-----------|
| **Cerebro** | Instrucciones, contextos, guías | `docs/` |
| **Manos** | MCPs (ClickUp, GitHub, Slack, Docs, etc.) | `mcp/` |
| **Bocas** | Canales de acceso (Telegram, Terminal) | `channels/` |

## MCPs Integrados

| MCP | Propósito | Estado |
|-----|-----------|--------|
| **ClickUp** | Product Management (Initiatives, Epics, User Stories) | ✅ |
| **GitHub** | Código, PRs, Issues | ✅ |
| **Slack** | Comunicación y notificaciones | ✅ |
| **Google Docs** | Documentación y specs | ✅ |
| **Google Sheets** | Datos y reportes | ✅ |
| **Granola** | Meeting notes, transcripciones | ✅ |
| **Gmail** | Email | 🔜 |
| **Slides** | Presentaciones | 🔜 |

## Canales de Acceso

| Canal | Descripción | Estado |
|-------|-------------|--------|
| **Terminal** | Claude Code CLI / Cursor IDE | ✅ |
| **Telegram** | Bot para acceso móvil | ✅ |
| **Slack** | Mensajes directos | 🔜 |
| **WhatsApp** | Bot móvil | 🔜 |

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
├── CLAUDE.md              # Instrucciones para Claude (rules)
├── claudio.png            # Diagrama de arquitectura
├── kill_bot_processes.sh  # Utilidad para el bot
├── docs/
│   ├── integrations/      # Guías por MCP
│   └── workflows/         # Workflows multi-MCP
├── mcp/
│   ├── cursor-config.json # Config para Cursor
│   └── servers/           # Servidores MCP
└── channels/
    └── telegram/          # Bot de Telegram
```

## Documentación

- [Instrucciones de Claudio](./CLAUDE.md)
- [Integración ClickUp](./docs/integrations/clickup/guide.md)
- [Integración Slack](./docs/integrations/slack/guide.md)
- [Workflows](./docs/workflows/README.md)
