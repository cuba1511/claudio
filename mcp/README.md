# MCP Configuration

Configuración de Model Context Protocol (MCP) servers para Claudio.

## Archivos

| Archivo | Propósito | Ubicación Real |
|---------|-----------|----------------|
| `cursor-config.json` | Config para Cursor IDE | `~/.cursor/mcp.json` |
| `claude-code-config.example.json` | Ejemplo para Claude Code CLI | `~/.claude.json` |

## MCPs Configurados

| MCP | Tipo | Descripción |
|-----|------|-------------|
| **ClickUp** | npx package | Product Management |
| **GitHub** | Remote URL | GitHub Copilot MCP |
| **Slack** | npx package | Comunicación |
| **Google Docs** | Local server | Documentación |
| **Granola** | Python module | Meeting notes |

## Setup

### Para Cursor

1. Copia `cursor-config.json` a `~/.cursor/mcp.json`
2. Reemplaza los tokens/credenciales con los tuyos
3. Reinicia Cursor

### Para Claude Code CLI

1. Edita `~/.claude.json`
2. Agrega la sección `mcpServers` dentro del proyecto
3. Usa `claude-code-config.example.json` como referencia

## Notas

- **Slack**: Requiere tokens `xoxc` y `xoxd` del navegador (ver `docs/integrations/slack/guide.md`)
- **GitHub**: Requiere suscripción a GitHub Copilot
- **ClickUp**: Requiere licencia del MCP server
- **Granola**: Requiere app de Granola instalada
- **Google Docs**: Requiere OAuth setup (ver `docs/integrations/google-docs/guide.md`)

## Servidores Custom

Los servidores MCP custom están en `servers/`:

```
servers/
└── google-docs → symlink a mcp-servers/mcp-googledocs-server
```
