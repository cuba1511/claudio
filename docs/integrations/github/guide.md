# GitHub Integration

## Configuración

Usa el MCP de GitHub Copilot (requiere suscripción a GitHub Copilot).

## Herramientas Disponibles

| Tool | Descripción |
|------|-------------|
| `list_repos` | Listar repositorios |
| `list_pull_requests` | Listar PRs |
| `get_pull_request` | Detalles de un PR |
| `create_issue` | Crear issue |
| `search_code` | Buscar código |

## Ejemplos de Uso

### Listar PRs abiertos
```
list_pull_requests(
  owner: "PropHero",
  repo: "orders-agent",
  state: "open"
)
```

### Crear issue
```
create_issue(
  owner: "PropHero",
  repo: "orders-agent",
  title: "Bug: ...",
  body: "Descripción del bug"
)
```

## Workflows Comunes

### PR Review
1. Listar PRs abiertos
2. Obtener detalles del PR
3. Revisar cambios
4. Aprobar o solicitar cambios

### Bug Tracking
1. Crear issue en GitHub
2. Vincular con User Story en ClickUp
3. Notificar en Slack
