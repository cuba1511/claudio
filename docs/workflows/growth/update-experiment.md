# Update Experiment Workflow

## MCPs Utilizados

- Notion (fetch + update page)

## Triggers

```
"Actualiza el experimento [nombre] con estos resultados"
"Añade sign-off de [stakeholder] al experimento X"
"Mueve el experimento X a Review / Running"
"Registra resultados intermedios de [experimento]"
```

## Pasos

1. **Localizar experimento** — `notion-search` por nombre o URL del usuario
2. **Fetch página** — `notion-fetch` para contenido y propiedades actuales
3. **Identificar tipo de update:**
   - Sign-off (tabla en body)
   - Resultados intermedios o finales (sección Resultados)
   - Cambio de Status (propiedad DB)
   - Edición de pilares (problema, hipótesis, etc.)
4. **Validar transición** — si cambia Status, verificar reglas en `config.md`
5. **Mostrar diff / borrador** — qué se va a cambiar; confirmar con usuario
6. **Aplicar** — `notion-update-page`:
   - `update_properties` para Status, fechas, Sign-off status
   - `insert_content` o `update_content` para body sections
7. **Recalcular Sign-off status** — si todos los requeridos = Approved → `Complete`; si algunos → `Partial`

## Reglas de transición de Status

| From | To | Requisito |
|------|-----|-----------|
| Draft | Review | 4 pilares completos |
| Review | Approved | Todos los sign-offs requeridos = Approved |
| Approved | Running | Fecha inicio definida; confirmación owner |
| Running | Concluded | Fecha fin alcanzada o stop manual |
| Concluded | Scaled / Killed | Sección Resultados + Aprendizajes completas |

**Nunca** Approved → Running si falta algún sign-off requerido.

## Inputs típicos

| Update | Input |
|--------|-------|
| Sign-off | Stakeholder, Approved/Rejected, notas |
| Resultados | Tabla métricas, periodo, vs target |
| Status | Nuevo estado + justificación |
| Metodología | Cambio de duración, segmento, etc. |

## Output

- Link a página actualizada
- Resumen de cambios
- Sign-offs aún pendientes (si aplica)
- Siguiente acción sugerida
