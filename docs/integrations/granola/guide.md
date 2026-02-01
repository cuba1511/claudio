# Granola Integration

## Qué es Granola

Granola es una app de meeting notes que graba y transcribe reuniones automáticamente.

## Configuración

Usa el MCP `granola-mcp` (módulo Python).

### Requisitos

1. Tener Granola app instalada
2. Tener reuniones grabadas en Granola

### Variables de entorno

```bash
GRANOLA_CACHE_PATH=/Users/YOUR_USER/Library/Application Support/Granola/cache-v3.json
```

## Herramientas Disponibles

| Tool | Descripción |
|------|-------------|
| `list_meetings` | Listar reuniones recientes |
| `get_meeting` | Obtener detalles de una reunión |
| `search_meetings` | Buscar en transcripciones |

## Ejemplos de Uso

### Listar reuniones recientes

```
list_meetings(limit: 10)
```

### Obtener transcripción

```
get_meeting(meeting_id: "abc123")
```

### Buscar en notas

```
search_meetings(query: "producto roadmap")
```

## Workflows Comunes

### Crear notas de reunión en Google Docs

1. Obtener meeting de Granola
2. Extraer puntos clave y action items
3. Crear documento en Google Docs
4. Compartir link en Slack

### Crear tareas desde reunión

1. Obtener meeting de Granola
2. Identificar action items
3. Crear User Stories en ClickUp
4. Notificar en Slack
