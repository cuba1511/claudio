# Create Experiment Workflow

## MCPs Utilizados

- Notion (crear página en Ideas-Experiments)

## Trigger

```
"Crea un experimento para [objetivo]"
"Crea un experimento de growth sobre [tema]"
"Nuevo experimento: [nombre]"
```

## Pasos

1. **Leer contexto** — `docs/integrations/notion/config.md` + template `templates/experiment.md`
2. **Recolectar inputs** — problema, hipótesis, métricas, metodología, área, tags
3. **Calcular sign-offs** — según stakeholder map (Area + Tags)
4. **Mostrar borrador** — propiedades DB + body del template; esperar confirmación
5. **Fetch schema** — `notion-fetch` en la DB Ideas-Experiments
6. **Crear página** — `notion-create-pages` con `data_source_id` y Status = `Draft`
7. **Resumir** — link Notion + sign-offs pendientes + siguiente paso (mover a Review)

## Inputs Requeridos

| Input | Descripción | Ejemplo |
|-------|-------------|---------|
| Nombre | Título del experimento | "WhatsApp reminder timing" |
| Problema | Impacto cuantificado | "30% no-show en GCs" |
| Hipótesis | If/then/because | "Si recordamos 2h antes, show-up +15%" |
| Métrica primaria | North star | "Show-up rate" |
| Baseline / Target | Números | "45% → 55%" |
| Metodología | Diseño y duración | "A/B 2 semanas, segmento ES leads" |
| Area | Funnel stage | Conversion |
| Owner | DRI | @ignacio.delacuba |
| Tags | Opcional; activan sign-offs | `messaging`, `user-data` |

## Validación antes de crear

- [ ] Los 4 pilares están completos (problema, hipótesis, métricas, metodología)
- [ ] Métrica primaria tiene baseline y target
- [ ] Tabla de sign-off incluye todos los stakeholders requeridos
- [ ] Usuario confirmó el borrador

## Output

- Página creada en Ideas-Experiments (link)
- Status: `Draft`
- Lista de sign-offs pendientes
- Sugerencia: "Pásalo a Review cuando el draft esté listo"

## Qué NO hacer

- Crear sin confirmación del usuario
- Pasar directamente a `Running`
- Inventar `collection://` ID — usar el de `config.md` o fetch en vivo
