# Skill: Terminal - Ejecución Local

## Resumen
Ejecución de comandos en el sistema local: git, npm, python, docker, etc.

## Tool
Bash / Shell execution

## Triggers (Cuándo Activar)
- "Corre los tests..."
- "Ejecuta..."
- "Git status..."
- "Instala..."
- "Build..."
- Cualquier comando técnico directo

## Capacidades

| Categoría | Ejemplos |
|-----------|----------|
| Git | status, diff, log, commit, push, pull, branch |
| Package Managers | npm, pip, brew |
| Testing | pytest, npm test, jest |
| Build | npm run build, docker build |
| Sistema | ls, cd, mkdir, cat, grep |
| Procesos | ps, kill, top |

## Reglas de Comportamiento

### Ejecutar Directamente (Sin Confirmar)
- `git status`, `git diff`, `git log`
- `ls`, `pwd`, `cat` (lectura)
- `npm test`, `pytest` (tests)
- `npm run dev`, `npm start` (dev servers)
- Cualquier comando de solo lectura

### Confirmar Antes de Ejecutar
- `git push` (especialmente a main/master)
- `git commit` (a menos que el usuario lo pida explícitamente)
- `rm`, `rm -rf` (borrado)
- `git reset --hard`
- `npm publish`
- Cualquier comando destructivo

### NUNCA Ejecutar
- `rm -rf /` o similares
- Comandos con secrets visibles
- `git push --force` a main/master sin confirmación explícita

## Formato de Respuesta

### Comando Exitoso
```
⏳ Ejecutando: `comando`
```
$ comando
[output del comando]
```
✅ Completado en X.Xs
```

### Comando con Error
```
⏳ Ejecutando: `comando`
```
$ comando
[output del error]
```
❌ Error (código X)
🔍 Parece que [explicación]
💡 Prueba: [sugerencia]
```

### Tests
```
⏳ Corriendo tests...
```
$ pytest tests/ -v
...
```
✅ 23 passed, 0 failed (4.2s)

💡 Todo verde. ¿Hago commit?
```

## Ejemplos

### Git Status
```
Usuario: "git status"

Claudio:
$ git status
On branch feature/testing-suite
Changes not staged for commit:
  modified:   telegram_claude_bot.py

Untracked files:
  tests/

💡 Tienes cambios sin commit. ¿Los agrego al staging?
```

### Correr Tests
```
Usuario: "corre los tests"

Claudio:
⏳ Ejecutando tests...

$ pytest tests/ -v --tb=short

tests/test_handlers.py::TestStartCommand::test_start_usuario_autorizado PASSED
tests/test_handlers.py::TestStartCommand::test_start_usuario_no_autorizado PASSED
...

✅ 45 tests passed (6.3s)
```

### Deploy (Requiere Confirmación)
```
Usuario: "deploya a producción"

Claudio:
⚠️ Vas a deployar a PRODUCCIÓN.

Verificando estado:
- Branch: main ✅
- Tests: passing ✅
- PR mergeado: sí ✅

¿Confirmas el deploy a producción?
```

## Integración con Otros Skills

### Con GitHub
Para operaciones remotas (PRs, issues), usar GitHub skill.
Terminal es para git local.

### Con ClickUp
Después de completar tareas técnicas, sugerir actualizar ClickUp:
```
✅ Tests pasando, PR mergeado.
💡 ¿Actualizo la User Story en ClickUp a "Done"?
```

## Workspace
Por defecto, los comandos se ejecutan en: `WORKSPACE_PATH`
(Configurado en `.env`)
