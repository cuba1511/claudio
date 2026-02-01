# Sprint Report Workflow

## MCPs Utilizados
- ClickUp (obtener datos del sprint)
- Google Sheets (actualizar métricas)
- Slack (compartir reporte)

## Pasos

1. **Obtener tareas** del sprint actual en ClickUp
2. **Calcular métricas** (completadas, pendientes, velocity)
3. **Actualizar spreadsheet** con datos
4. **Generar resumen** 
5. **Enviar a Slack** con highlights

## Trigger

```
"Genera el reporte del sprint"
```

## Métricas Calculadas

| Métrica | Fórmula |
|---------|---------|
| Completion Rate | Completadas / Total |
| Velocity | Story Points completados |
| Carryover | Tareas no completadas |
| Blockers | Tareas bloqueadas |

## Output

- Spreadsheet actualizado
- Mensaje en #sprint-reviews con resumen
