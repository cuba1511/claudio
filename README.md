# Bot de Telegram para Claude Code CLI

Este bot permite ejecutar comandos en tu instancia local de Claude Code CLI directamente desde Telegram, incluyendo soporte completo para MCPs (Model Context Protocol).

## 🚀 Características

- ✅ Ejecuta comandos de Claude Code CLI desde Telegram
- ✅ Soporte completo para MCPs (GitHub, Figma, ClickUp, etc.)
- ✅ Conversaciones persistentes por usuario
- ✅ Ejecución en tu workspace local
- ✅ Manejo de mensajes largos
- ✅ Comandos de gestión de sesiones

## 📋 Requisitos Previos

1. **Claude Code CLI instalado** - Asegúrate de tener Claude Code CLI instalado y disponible en tu PATH
2. **Python 3.8+** - El bot está escrito en Python
3. **Bot de Telegram** - Necesitas crear un bot en Telegram usando [@BotFather](https://t.me/BotFather)

## 🔧 Instalación

1. **Clona o navega al directorio del proyecto:**
   ```bash
   cd /Users/ignaciodelacuba/Dev/claudio
   ```

2. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Crea un bot en Telegram:**
   - Abre Telegram y busca [@BotFather](https://t.me/BotFather)
   - Envía `/newbot` y sigue las instrucciones
   - Guarda el token que te proporciona

4. **Configura las variables de entorno:**
   ```bash
   cp .env.example .env
   ```
   
   Edita `.env` y agrega tu token:
   ```
   TELEGRAM_BOT_TOKEN=tu_token_aqui
   CLAUDE_CLI_PATH=claude
   WORKSPACE_PATH=/Users/ignaciodelacuba/Dev/claudio
   ```

## 🎯 Uso

1. **Inicia el bot:**
   ```bash
   python telegram_claude_bot.py
   ```

2. **Abre Telegram y busca tu bot** (el nombre que le diste en BotFather)

3. **Envía `/start`** para comenzar

4. **Envía mensajes** como si estuvieras hablando con Claude Code CLI:
   - `Lista los archivos en el directorio actual`
   - `Ejecuta el script test.py`
   - `Usa el MCP de GitHub para listar mis repositorios`
   - `Busca errores en el código Python`

## 📱 Comandos Disponibles

- `/start` - Mensaje de bienvenida
- `/help` - Muestra ayuda detallada
- `/new` - Inicia una nueva conversación (limpia el contexto)
- `/status` - Muestra el estado del bot y configuración
- `/myid` - Muestra tu ID de usuario (útil para configurar seguridad)

## 🔍 Ejemplos de Uso

### Ejemplo 1: Listar archivos
```
Usuario: Lista los archivos en el directorio actual
Bot: [Ejecuta el comando y devuelve la lista]
```

### Ejemplo 2: Usar MCPs
```
Usuario: Usa el MCP de GitHub para listar mis repositorios
Bot: [Ejecuta el comando con MCP y devuelve los repositorios]
```

### Ejemplo 3: Ejecutar scripts
```
Usuario: Ejecuta el script test.py y muestra los resultados
Bot: [Ejecuta el script y devuelve la salida]
```

## ⚙️ Configuración Avanzada

### Variables de Entorno

- `TELEGRAM_BOT_TOKEN` - Token del bot de Telegram (requerido)
- `CLAUDE_CLI_PATH` - Ruta al ejecutable de Claude CLI (opcional, por defecto: `claude`)
- `WORKSPACE_PATH` - Directorio donde se ejecutan los comandos (opcional, por defecto: directorio actual)
- `ALLOWED_USER_IDS` - IDs de usuarios autorizados separados por comas (requerido para seguridad)
- `SKIP_PERMISSIONS` - Saltar checks de permisos para MCPs (por defecto: `true`)
- `ALLOWED_TOOLS` - Herramientas permitidas (por defecto: `*`)

### Ejecutar como Servicio

Para ejecutar el bot como un servicio en segundo plano (macOS/Linux):

```bash
# Usando nohup
nohup python telegram_claude_bot.py > bot.log 2>&1 &

# O usando screen
screen -S claude-bot
python telegram_claude_bot.py
# Presiona Ctrl+A luego D para detach
```

## 🔒 Seguridad

El bot incluye un sistema de autenticación basado en IDs de usuario de Telegram:

1. **Obtén tu ID de usuario:**
   - Inicia el bot y envía `/myid`
   - El bot te mostrará tu ID de usuario único

2. **Configura usuarios autorizados:**
   - Edita el archivo `.env`
   - Agrega tu ID a `ALLOWED_USER_IDS`:
     ```
     ALLOWED_USER_IDS=123456789
     ```
   - Para múltiples usuarios, sepáralos con comas:
     ```
     ALLOWED_USER_IDS=123456789,987654321
     ```

3. **Reinicia el bot** para aplicar los cambios

⚠️ **IMPORTANTE:** Si `ALLOWED_USER_IDS` está vacío, CUALQUIER usuario puede usar el bot. Esto es inseguro y NO recomendado.

## 🛠️ Solución de Problemas

### El bot no responde
- Verifica que el token de Telegram sea correcto
- Asegúrate de que Claude CLI esté instalado y en PATH
- Revisa los logs para ver errores

### Claude CLI no encontrado
- Verifica que Claude CLI esté instalado: `claude --version`
- Si está en una ubicación diferente, configura `CLAUDE_CLI_PATH` en `.env`

### Los MCPs no funcionan
- Asegúrate de que los MCPs estén configurados en tu instalación local de Claude Code
- Los MCPs funcionan igual que en la terminal local

### "Acceso denegado" al usar el bot
- Verifica que tu ID de usuario esté en `ALLOWED_USER_IDS` en el archivo `.env`
- Usa `/myid` para obtener tu ID de usuario
- Reinicia el bot después de agregar tu ID

## 📝 Notas

- Cada usuario de Telegram tiene su propia sesión de conversación
- Los comandos se ejecutan en el directorio especificado en `WORKSPACE_PATH`
- Los mensajes largos se dividen automáticamente para cumplir con los límites de Telegram
- El bot mantiene el contexto de la conversación por usuario

## 🔒 Seguridad

⚠️ **IMPORTANTE**: Este bot ejecuta comandos en tu máquina local. Asegúrate de:
- No compartir el token del bot públicamente
- Usar solo con usuarios de confianza
- Considerar agregar autenticación adicional si es necesario

## 📄 Licencia

Este proyecto es de uso personal. Úsalo bajo tu propia responsabilidad.
