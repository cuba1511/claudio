# ClickUp Integration

## Configuración

Usa el MCP server `@taazkareem/clickup-mcp-server`.

### Variables de entorno

```bash
CLICKUP_MCP_LICENSE_KEY=your_license_key
CLICKUP_API_KEY=your_api_key
CLICKUP_TEAM_ID=your_team_id
DOCUMENT_SUPPORT=true
```

### Obtener API Key

1. Ve a ClickUp Settings → Apps
2. Genera un API Token
3. Copia el Team ID de la URL del workspace

## Herramientas Disponibles

| Tool | Descripción |
|------|-------------|
| `get_workspace_hierarchy` | Ver estructura del workspace |
| `get_workspace_tasks` | Buscar tareas por lista |
| `get_task` | Obtener detalles de una tarea |
| `create_task` | Crear nueva tarea |
| `update_task` | Actualizar tarea existente |

## Workflow: Crear User Story

### 1. Buscar contexto (Initiative)

```
get_workspace_tasks(
  list_ids: ["901213053436"],  # Approved Initiatives
  ...
)
```

### 2. Buscar Epic relacionado

```
get_workspace_tasks(
  list_ids: ["901215396098", "901213056240"],  # Q1 2026 Epics + Backlog
  ...
)
```

### 3. Crear User Story

```
create_task(
  listId: "901213056238",  # Sprint Backlog
  name: "🎯 [Título]",
  markdown_description: "..."
)
```

## IDs Importantes

Ver `config.md` para la lista completa de IDs.

| Qué | List ID |
|-----|---------|
| Initiatives | `901213053436` |
| Q1 2026 Epics | `901215396098` |
| Sprint Backlog | `901213056238` |

## Templates

Ver carpeta `templates/` para estructuras de:
- Initiatives
- Epics
- User Stories
