# Documentación de Claudio

## Estructura

```
docs/
├── README.md                    ← Este archivo
├── skills/                      ← Capacidades del agente por MCP
│   ├── README.md
│   ├── clickup.md              ← Product Management
│   ├── github.md               ← Código y PRs
│   ├── google-docs.md          ← Documentación
│   └── terminal.md             ← Comandos locales
│
└── clickup/                     ← Configuración específica de ClickUp
    ├── config.md               ← IDs de listas y espacios
    └── structure/              ← Templates para crear artifacts
        ├── user_story_structure.md
        ├── epic_structure.md
        └── initiative_structure.md
```

## Cómo Funciona

### CLAUDE.md (Raíz del proyecto)
Define la **identidad** de Claudio:
- Personalidad y tono
- Principios de comportamiento
- Resumen de skills
- Reglas de interacción por contexto

### docs/skills/
Documenta **cada skill en detalle**:
- Triggers (cuándo activar)
- Capacidades específicas
- Reglas de comportamiento
- Ejemplos de uso

### docs/clickup/
Configuración específica de ClickUp para PropHero:
- IDs de listas y espacios
- Templates para artifacts
- Workflows de creación

## Agregar Nuevo Skill

1. Crear `docs/skills/{nombre}.md` con:
   - Triggers
   - Capacidades
   - Reglas
   - Ejemplos

2. Actualizar `docs/skills/README.md`

3. Actualizar `CLAUDE.md` con resumen del skill

## Mantener Actualizado

### Cada Quarter
- Actualizar ID de Epics en `docs/clickup/config.md`

### Cuando Cambie un MCP
- Actualizar skill correspondiente en `docs/skills/`

### Cuando Cambie el Comportamiento
- Actualizar `CLAUDE.md`
