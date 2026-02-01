# Google Docs Integration

## Configuración

Usa el servidor MCP local en `mcp/servers/google-docs/`.

### Setup inicial

```bash
cd mcp/servers/google-docs
npm install
npm run build
```

### Autenticación

1. Crear proyecto en Google Cloud Console
2. Habilitar Google Docs API y Google Sheets API
3. Crear credenciales OAuth 2.0
4. Descargar `client_secret.json`
5. Ejecutar el servidor y autorizar

## Herramientas Disponibles

| Tool | Descripción |
|------|-------------|
| `create_document` | Crear documento |
| `read_document` | Leer contenido |
| `update_document` | Actualizar documento |
| `list_documents` | Listar documentos |

## Ejemplos de Uso

### Crear documento
```
create_document(
  title: "Daily Standup - 2026-02-01",
  content: "## Participantes\n- ..."
)
```

### Leer documento
```
read_document(
  document_id: "1abc..."
)
```

## Workflows Comunes

### Meeting Notes
1. Crear documento con template
2. Compartir link en Slack
3. Actualizar durante la reunión

### Specs Técnicos
1. Crear documento
2. Vincular desde Epic en ClickUp
3. Compartir para review
