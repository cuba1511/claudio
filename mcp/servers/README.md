# MCP Servers

Servidores MCP utilizados por Claudio.

## Tipos de Servidores

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| **Local** | Servidor corriendo localmente | Google Docs |
| **NPX** | Paquete npm ejecutado con npx | Slack, ClickUp |
| **Remote** | URL remota | GitHub Copilot |
| **Python** | Módulo Python | Granola |

## Servidores Configurados

### Google Docs (Local)
- **Ubicación**: `/Users/ignaciodelacuba/Dev/mcp-servers/mcp-googledocs-server/`
- **Comando**: `node dist/server.js`
- **Requiere**: OAuth setup con Google Cloud

### Slack (NPX)
- **Paquete**: `slack-mcp-server@latest`
- **Requiere**: Tokens `xoxc` y `xoxd` del navegador
- **Docs**: Ver `docs/integrations/slack/guide.md`

### ClickUp (NPX)
- **Paquete**: `@taazkareem/clickup-mcp-server@latest`
- **Requiere**: API Key y License Key
- **Docs**: Ver `docs/integrations/clickup/guide.md`

### GitHub (Remote)
- **URL**: `https://api.githubcopilot.com/mcp/`
- **Requiere**: Token de GitHub Copilot
- **Docs**: Ver `docs/integrations/github/guide.md`

### Granola (Python)
- **Módulo**: `granola_mcp.mcp`
- **Requiere**: App Granola instalada
- **Docs**: Ver `docs/integrations/granola/guide.md`

## Agregar nuevo servidor

1. Agregar configuración a `../cursor-config.json` (para Cursor IDE)
2. Agregar configuración a `~/.claude.json` (para Claude Code CLI)
3. Crear guía en `docs/integrations/{nombre}/guide.md`
