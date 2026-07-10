# Experiment Review Workflow

Pre-meeting brief for growth / experiment review sessions.

## MCPs Utilizados

- Notion (query + fetch experiment pages)

## Triggers

```
"Prepárame la review de experimentos"
"¿Qué experimentos necesitan sign-off?"
"Agenda para la reunión de growth"
"Estado de experimentos activos"
```

## Pasos

### 1. Cargar configuración

Read `docs/integrations/notion/config.md` for lifecycle states and stakeholder rules.

### 2. Query experimentos

- `notion-fetch` Ideas-Experiments database
- `notion-query-data-sources` or `notion-search` for:
  - Status in `Draft`, `Review`, `Approved`, `Running`
  - Optional filter by Owner or Area

### 3. Clasificar por prioridad de reunión

| Prioridad | Criterio |
|-----------|----------|
| **P0 — Blockers** | `Review` + sign-offs pendientes > 7 días |
| **P1 — Launch ready** | `Approved`, listos para `Running` |
| **P2 — Needs decision** | `Running` con fecha fin próxima o resultados parciales |
| **P3 — Drafts** | `Draft` sin owner o pilares incompletos |

### 4. Por cada experimento relevante, extraer

- Nombre + link Notion
- Status + Owner
- Hipótesis (1 línea)
- Métrica primaria + target
- Sign-offs: quién falta (`Pending` / `Rejected`)
- Blockers o preguntas abiertas

### 5. Generar agenda sugerida

```markdown
## Experiment Review — [fecha]

### Sign-offs pendientes (acción hoy)
1. [Experimento A](url) — falta Legal, Product
2. ...

### Listos para lanzar
1. [Experimento B](url) — Approved, launch [fecha]

### En curso — updates
1. [Experimento C](url) — día 10/14, métrica intermedia X

### Drafts a completar
1. [Experimento D](url) — falta metodología

### Decisiones pedidas
- ¿Aprobar sign-off de X?
- ¿Escalar o matar Y con resultados preliminares?
```

### 6. Contexto de reunión (Slack)

Si el prompt incluye `--- CONTEXTO DEL HILO DE SLACK ---`, cruzar nombres mencionados en el hilo con experimentos en Notion. No pedir que repitan lo que ya está en el hilo.

## Output

- Agenda markdown lista para pegar en Slack / Notion
- Links a cada experimento
- Lista explícita de sign-offs pendientes por stakeholder

## Checklist de ejecución

- [ ] Query ejecutado sobre DB correcta
- [ ] Experimentos agrupados por prioridad
- [ ] Sign-offs mapeados a personas (no solo áreas)
- [ ] Decisiones concretas al final de la agenda
