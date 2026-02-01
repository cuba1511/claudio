# Slack Integration

## Configuración

El MCP de Slack usa tokens `xoxc` + `xoxd` extraídos del navegador.

### Tokens necesarios

| Token | Descripción | Cómo obtener |
|-------|-------------|--------------|
| `SLACK_MCP_XOXC_TOKEN` | Token de sesión | DevTools → Console → localStorage |
| `SLACK_MCP_XOXD_TOKEN` | Cookie de sesión | DevTools → Application → Cookies → `d` |

### Variables de entorno

```json
{
  "SLACK_MCP_XOXC_TOKEN": "xoxc-...",
  "SLACK_MCP_XOXD_TOKEN": "xoxd-...",
  "SLACK_MCP_ADD_MESSAGE_TOOL": "true"
}
```

## Herramientas Disponibles

| Tool | Descripción |
|------|-------------|
| `channels_list` | Listar canales |
| `conversations_history` | Ver mensajes de un canal |
| `conversations_replies` | Ver threads |
| `conversations_add_message` | Enviar mensajes |
| `conversations_search_messages` | Buscar mensajes |

## Ejemplos de Uso

### Listar canales
```
channels_list(channel_types: "public_channel,private_channel,im")
```

### Enviar mensaje
```
conversations_add_message(
  channel_id: "@username",
  payload: "Mensaje de prueba",
  content_type: "text/plain"
)
```

### Ver historial
```
conversations_history(
  channel_id: "#general",
  limit: "1d"
)
```

## Notas

- Los mensajes se envían inmediatamente (no hay drafts)
- Para "borradores", enviar a tu propio DM primero
- Los tokens expiran - renovar si hay errores de autenticación
