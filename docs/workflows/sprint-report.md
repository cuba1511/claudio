# Sprint Report Workflow

## MCPs Utilizados
- **ClickUp** — obtener tareas del sprint, puntos, estados
- **Google Sheets** — leer 3-hour work blocks + escribir métricas en hoja principal
- **Slack** — compartir reporte (opcional)

## Trigger

```
"Genera el reporte del sprint [N]"
"Llena el sheets del sprint [N]"
```

---

## Spreadsheet de Reporting

| Campo | Valor |
|-------|-------|
| **Spreadsheet** | DS & AI Measuring Performance (Internal) |
| **ID** | `1O7ZL9IzATToktPi9-VXPTfMZWg5Zu92eUyzQyDLGu9c` |
| **Hoja principal** | `Data Science & IA` (gid: `200815114`) |
| **Hoja work blocks** | `3-hour work blocks` (gid: `1897775165`) |

### Columnas de la Hoja Principal

| Col | Métrica | Fuente | Automático |
|-----|---------|--------|------------|
| A | Sprint # | Manual | - |
| B | Dates | Manual | - |
| C | Goal | ClickUp (sprint goal) | Si |
| D | Points Committed | ClickUp (suma de puntos de tareas parent) | Si |
| E | Points Completed | ClickUp (puntos de tareas con status type=closed) | Si |
| F | Carry-over Points | Calculado (D - E) | Si |
| G | Avg Cycle Time (Days) | ClickUp (ver sección abajo) | Parcial |
| H | Bugs Found | ClickUp (tareas con "bug" en el nombre) | Si |
| I | Team Happiness (1-5) | Encuesta al equipo | No |
| J | Team Pressure (1-5) | Encuesta al equipo | No |
| K | Team Quality (1-5) | Encuesta al equipo | No |
| L | Cognitive Load (1-5) | Encuesta al equipo | No |
| M | Goal Met (Yes/No) | Juicio basado en completitud | Parcial |
| N | Deep Work % (Flow) | Hoja `3-hour work blocks` | Si |
| O | Say/Do Ratio (%) | Calculado (E / D * 100) | Si |
| P | Quality Index (%) | Calculado (H / D * 100) | Si |
| Q | Health Score | Calculado (promedio de I, J, K, L) | No (depende de encuesta) |
| R | Historical Average (Velocity) | Calculado (promedio de E de todos los sprints) | Si |

---

## Proceso Paso a Paso

### Paso 1: Identificar la Lista del Sprint en ClickUp

Los sprints viven en el folder `02. Product Backlog & Sprints` (ID: `90127761372`) dentro del space `P&T - DS & AI Squad` (ID: `90125280978`).

```
Usar: clickup_get_workspace_hierarchy
space_ids: ["90125280978"]
```

Buscar la lista que corresponda al sprint, ej: `Sprint 9 (1/26 - 2/8)` -> ID `901215476720`.

**Listas de sprints conocidas:**

| Sprint | List ID | Dates |
|--------|---------|-------|
| Sprint 7 | `901215046507` | 12/29 - 1/11 |
| Sprint 8 | `901215046511` | 1/12 - 1/25 |
| Sprint 9 | `901215476720` | 1/26 - 2/8 |
| Sprint 10 | `901215681128` | 2/9 - 2/22 |

### Paso 2: Obtener Tareas del Sprint

```
Usar: get_workspace_tasks
list_ids: ["<sprint_list_id>"]
detail_level: "detailed"
include_closed: true
subtasks: true
```

**IMPORTANTE:** La respuesta puede ser muy grande. Guardar en archivo y procesar con Python.

### Paso 3: Calcular Métricas de ClickUp

Filtrar solo **tareas parent** (excluir subtasks donde `parent != null`).

#### Points Committed & Completed

```python
for task in tasks:
    if task['parent'] is not None:
        continue  # skip subtasks
    points = task.get('points') or 0
    total_points += points
    if task['status']['type'] == 'closed':
        completed_points += points
```

#### Bugs Found

```python
bugs = sum(1 for t in parent_tasks if 'bug' in t['name'].lower())
```

#### Avg Cycle Time

**Limitación:** La API de ClickUp NO expone historial de cambios de estado. No podemos saber exactamente cuándo una tarea pasó a "In Progress".

**Aproximación usada:**

1. Para tareas creadas **antes** del sprint: usar `sprint_start_date` como inicio
2. Para tareas creadas **durante** el sprint: usar `date_created` como inicio
3. Para el cierre:
   - Si `date_done` es el primer día del sprint PERO `date_updated` es posterior -> la tarea fue **reabierta**. Usar `date_updated` como cierre real.
   - Si no, usar `date_done`.

```python
sprint_start = datetime(2026, 1, 26)  # ajustar por sprint

for task in completed_parent_tasks:
    created = datetime.fromtimestamp(int(task['date_created'])/1000)
    done = datetime.fromtimestamp(int(task['date_done'])/1000)
    updated = datetime.fromtimestamp(int(task['date_updated'])/1000)

    # Inicio
    start = sprint_start if created < sprint_start else created

    # Cierre: detectar tareas reabierta
    if done.date() <= sprint_start.date() and updated.date() > done.date():
        end = updated  # tarea fue reabierta
    else:
        end = done

    cycle_time = (end - start).days
```

> **Nota:** Este cálculo es una aproximación. El cycle time real (In Progress -> Done) solo está disponible en el dashboard nativo de ClickUp que tiene "Time in Status". Para mejorar la precisión, el equipo debería llenar el campo `start_date` en ClickUp al mover tareas a In Progress.

#### Say/Do Ratio

```
say_do = (completed_points / committed_points) * 100
```

#### Quality Index

```
quality_index = (bugs / committed_points) * 100
```

#### Goal Met

Evaluar si todas las tareas core del goal se completaron. Si hay tareas en progress al final del sprint -> `No`.

### Paso 4: Calcular Deep Work % desde Work Blocks

Leer la hoja `3-hour work blocks`:

```
Usar: readSpreadsheet
spreadsheetId: "1O7ZL9IzATToktPi9-VXPTfMZWg5Zu92eUyzQyDLGu9c"
range: "'3-hour work blocks'!A1:E50"
```

**Cálculo:**

```python
max_blocks_per_day = 2  # máximo por persona
team_members = 4  # Erika, Joel, Evgeny, Santiago
working_days = 10  # días laborales del sprint (excluir fines de semana)

max_total = max_blocks_per_day * team_members * working_days
actual_total = sum(all_blocks_in_sprint_dates)

deep_work_pct = (actual_total / max_total) * 100
```

**Notas:**
- Solo contar días laborales (lunes a viernes) dentro del rango del sprint
- Si un valor está vacío, contar como 0
- Max blocks por día por persona = 2

### Paso 5: Calcular Historical Average Velocity

Promediar los `Points Completed` (columna E) de todos los sprints, incluyendo el actual.

```
Usar: readSpreadsheet
range: "'Data Science & IA'!E2:E<last_row>"
```

### Paso 6: Escribir en el Sheet

Escribir todos los valores calculados en la fila correspondiente al sprint:

```
Usar: writeSpreadsheet
range: "'Data Science & IA'!A<row>:R<row>"
values: [[sprint#, dates, goal, committed, completed, carryover, cycle_time,
          bugs, "", "", "", "", goal_met, deep_work_pct, say_do, quality_index,
          "", historical_avg]]
```

**Dejar vacíos (el equipo los llena manualmente):**
- I: Team Happiness
- J: Team Pressure
- K: Team Quality
- L: Cognitive Load
- Q: Health Score

---

## Desglose por Persona (Opcional)

Si el usuario lo pide, calcular métricas por assignee:

```python
for task in parent_tasks:
    for assignee in task['assignees']:
        name = assignee['username']
        # acumular puntos completados, total, cycle time por persona
```

Esto es útil para identificar carga desbalanceada o cuellos de botella.

---

## Checklist de Ejecución

- [ ] Identificar sprint list ID en ClickUp
- [ ] Obtener tareas del sprint (include_closed=true, subtasks=true)
- [ ] Calcular: Points Committed, Completed, Carry-over
- [ ] Calcular: Avg Cycle Time (con detección de tareas reabiertas)
- [ ] Calcular: Bugs Found
- [ ] Calcular: Say/Do Ratio, Quality Index
- [ ] Evaluar: Goal Met
- [ ] Leer hoja `3-hour work blocks` y calcular Deep Work %
- [ ] Calcular: Historical Average Velocity
- [ ] Escribir todos los valores en la hoja principal
- [ ] Informar al usuario qué métricas faltan (encuesta del equipo)
