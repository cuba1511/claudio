# Google Sheets Integration

## Configuración

Comparte el servidor MCP con Google Docs (`mcp/servers/google-docs/`).

## Herramientas Disponibles

| Tool | Descripción |
|------|-------------|
| `read_spreadsheet` | Leer datos |
| `update_spreadsheet` | Actualizar celdas |
| `append_rows` | Agregar filas |

## Ejemplos de Uso

### Leer datos
```
read_spreadsheet(
  spreadsheet_id: "1abc...",
  range: "Sheet1!A1:D10"
)
```

### Actualizar celdas
```
update_spreadsheet(
  spreadsheet_id: "1abc...",
  range: "Sheet1!A1",
  values: [["Valor1", "Valor2"]]
)
```

## Workflows Comunes

### Reportes
1. Leer datos de ClickUp
2. Actualizar spreadsheet
3. Notificar en Slack

### Tracking
1. Agregar fila con nuevo registro
2. Calcular métricas
3. Generar reporte
