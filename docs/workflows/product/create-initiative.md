# Create Initiative Workflow

## MCPs Utilizados
- ClickUp (crear initiative)
- Google Docs (spec document)
- Slack (notificar)

## Pasos

1. **Validar inputs** - OKR, problema, métricas
2. **Crear documento** de spec en Google Docs
3. **Crear Initiative** en ClickUp con link al doc
4. **Notificar** en Slack al equipo

## Trigger

```
"Crea una nueva initiative para [objetivo]"
```

## Inputs Requeridos

| Input | Descripción | Ejemplo |
|-------|-------------|---------|
| OKR | Objetivo que soporta | "Aumentar conversión 20%" |
| Problema | Problema cuantificado | "Perdemos 30% leads por X" |
| Métricas | Baseline y target | "De 10% a 25%" |
| Owner | Responsable | "@ignacio.delacuba" |

## Output

- Initiative creada en ClickUp (link)
- Spec document en Google Docs (link)
- Mensaje en #product-updates
