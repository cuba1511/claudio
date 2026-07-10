# Conclude Experiment Workflow

## MCPs Utilizados

- Notion (fetch + update + status)

## Triggers

```
"Cierra el experimento [nombre]"
"Concluye el experimento X como Scaled"
"Mata el experimento Y — no funcionó"
"Post-mortem del experimento Z"
```

## Pasos

### 1. Localizar y fetch

`notion-search` → `notion-fetch` experiment page.

### 2. Validar que está en estado válido

Solo desde `Running` o `Concluded` (si resultados ya cargados).

### 3. Recolectar cierre

| Campo | Requerido |
|-------|-----------|
| Resultados finales | Sí — tabla vs baseline/target |
| Aprendizajes | Sí — qué funcionó / no / next step |
| Decisión | `Scaled` o `Killed` |
| Evidencia | Link a dashboard, sheet, screenshot |

### 4. Completar secciones del template

- **Resultados** — periodo, métricas, delta
- **Aprendizajes** — bullets accionables

### 5. Mostrar borrador de conclusión

Incluir recomendación Scaled vs Killed basada en criterio de éxito de la hipótesis.

### 6. Aplicar updates

1. `notion-update-page` — body (Resultados + Aprendizajes)
2. Status → `Concluded` primero si aún `Running`
3. Status final → `Scaled` o `Killed`
4. End date si no estaba seteada

### 7. Post-cierre (opcional, sugerir al usuario)

- Si **Scaled**: crear initiative en ClickUp o doc de rollout
- Si **Killed**: capturar learning en wiki / link desde hub de growth
- Notificar en Slack (#growth o canal acordado) — solo si el usuario lo pide

## Criterios de recomendación

| Señal | Recomendación |
|-------|---------------|
| Métrica primaria ≥ target, guardrails OK | Scaled |
| Mejora marginal, coste alto | Killed o Iterate (nuevo experimento) |
| Inconcluso (muestra pequeña) | Concluded + nuevo experimento con más power |
| Guardrail degradado | Killed |

## Output

- Página con Resultados + Aprendizajes completos
- Status final `Scaled` o `Killed`
- Resumen ejecutivo (3-5 líneas) para compartir
- Link Notion

## Checklist

- [ ] Resultados vs baseline/target documentados
- [ ] Aprendizajes escritos (no solo "no funcionó")
- [ ] Decisión Scaled/Killed explícita
- [ ] Status actualizado en DB
