# Canal Slack - Claudio

Bot de Slack que permite interactuar con Claudio directamente desde Slack.

## Características

- 💬 **DMs directos** - Escríbele al bot en un mensaje directo
- 📢 **Menciones en canales** - Menciona `@Claudio` en cualquier canal
- ⚡ **Comandos slash** - `/claudio`, `/claudio-new`, `/claudio-status`
- 🔒 **Seguridad** - Lista de usuarios autorizados, rate limiting
- 🔄 **Sesiones persistentes** - Mantiene contexto de conversación

## Configuración de la Slack App

### 1. Crear la App

1. Ve a [api.slack.com/apps](https://api.slack.com/apps)
2. Click en **Create New App** > **From scratch**
3. Nombre: `Claudio` (o el que prefieras)
4. Workspace: Selecciona tu workspace de PropHero

### 2. Configurar Permisos (OAuth & Permissions)

Ve a **OAuth & Permissions** y agrega estos **Bot Token Scopes**:

| Scope | Descripción |
|-------|-------------|
| `app_mentions:read` | Leer menciones al bot |
| `channels:history` | Leer mensajes en canales públicos |
| `channels:read` | Ver canales públicos |
| `chat:write` | Enviar mensajes |
| `commands` | Crear comandos slash |
| `groups:history` | Leer mensajes en canales privados |
| `groups:read` | Ver canales privados |
| `im:history` | Leer DMs |
| `im:read` | Ver DMs |
| `im:write` | Enviar DMs |
| `users:read` | Ver usuarios |

### 3. Habilitar Socket Mode

1. Ve a **Socket Mode** en el menú lateral
2. Habilita **Enable Socket Mode**
3. Te pedirá crear un App-Level Token:
   - Nombre: `socket-mode`
   - Scopes: `connections:write`
   - Click **Generate**
4. Copia el token `xapp-...` (este es tu `SLACK_APP_TOKEN`)

### 4. Configurar Event Subscriptions

1. Ve a **Event Subscriptions**
2. Habilita **Enable Events**
3. En **Subscribe to bot events**, agrega:
   - `app_mention`
   - `message.im`

### 5. Crear Comandos Slash (opcional pero recomendado)

Ve a **Slash Commands** y crea:

| Command | Description | Usage Hint |
|---------|-------------|------------|
| `/claudio` | Envía un mensaje a Claudio | `[tu pregunta]` |
| `/claudio-new` | Inicia nueva conversación | |
| `/claudio-status` | Muestra estado del bot | |

### 6. Instalar la App

1. Ve a **Install App**
2. Click en **Install to Workspace**
3. Autoriza los permisos
4. Copia el **Bot User OAuth Token** (`xoxb-...`)

### 7. Obtener tu User ID

En Slack:
1. Click en tu perfil
2. Click en **More** (tres puntos)
3. Click en **Copy member ID**

## Configuración Local

### 1. Crear archivo .env

```bash
cp .env.example .env
```

### 2. Configurar tokens

Edita `.env` con tus valores:

```bash
# Tokens de Slack (REQUERIDOS)
SLACK_BOT_TOKEN=xoxb-tu-bot-token
SLACK_APP_TOKEN=xapp-tu-app-token

# Tu User ID de Slack
SLACK_ALLOWED_USER_IDS=U1234567890

# Workspace de Claudio
WORKSPACE_PATH=/Users/tuusuario/Dev/claudio
```

### 3. Instalar dependencias

```bash
# Desde la raíz de claudio
source venv/bin/activate
pip install -r channels/slack/requirements.txt
```

## Uso

### Iniciar el bot

```bash
# Opción 1: Script de inicio
./channels/slack/start.sh

# Opción 2: Directamente
python3 channels/slack/bot.py
```

### Interactuar con Claudio

**DM directo:**
```
Tú: Hola Claudio, lista mis PRs abiertos
Claudio: [respuesta con tus PRs]
```

**Mención en canal:**
```
Tú: @Claudio crea una user story para el feature de login
Claudio: [respuesta en thread]
```

**Comando slash:**
```
/claudio lista las tareas pendientes en ClickUp
```

### Comandos disponibles

| Comando | Descripción |
|---------|-------------|
| `/claudio [mensaje]` | Envía un mensaje a Claudio |
| `/claudio-new` | Inicia nueva conversación (limpia contexto) |
| `/claudio-status` | Muestra estado del bot y tu autorización |

## Seguridad

### Usuarios autorizados

Por defecto, si `SLACK_ALLOWED_USER_IDS` está vacío, **todos** pueden usar el bot.

Para restringir:
```bash
# Un usuario
SLACK_ALLOWED_USER_IDS=U1234567890

# Múltiples usuarios
SLACK_ALLOWED_USER_IDS=U1234567890,U0987654321,U1122334455
```

### Rate Limiting

Configurado por defecto a 10 requests por minuto por usuario:
```bash
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW=60
```

### Timeout

Los comandos tienen un timeout de 30 minutos por defecto:
```bash
COMMAND_TIMEOUT=1800
```

## Troubleshooting

### "Socket Mode is not enabled"

Asegúrate de habilitar Socket Mode en la configuración de tu app.

### "not_allowed_token_type"

Estás usando el token incorrecto. Verifica:
- `SLACK_BOT_TOKEN` empieza con `xoxb-`
- `SLACK_APP_TOKEN` empieza con `xapp-`

### "missing_scope"

Agrega el scope faltante en **OAuth & Permissions** y reinstala la app.

### El bot no responde a menciones

1. Verifica que agregaste `app_mention` en Event Subscriptions
2. Invita al bot al canal: `/invite @Claudio`

### El bot no responde a DMs

Verifica que agregaste `message.im` en Event Subscriptions.

## Arquitectura

```
┌─────────────────────────────────────────┐
│              SLACK                       │
│  ┌─────────┐    ┌─────────────────────┐ │
│  │   DM    │    │ Canal: @Claudio ... │ │
│  └────┬────┘    └──────────┬──────────┘ │
└───────┼────────────────────┼────────────┘
        │                    │
        ▼                    ▼
┌─────────────────────────────────────────┐
│     Socket Mode (WebSocket)              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│     bot.py (Slack Bolt)                  │
│  ┌─────────────────────────────────────┐│
│  │     ClaudeCodeExecutor              ││
│  │     (igual que Telegram)            ││
│  └─────────────────────────────────────┘│
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│     Claude Code CLI (local)              │
│     + MCPs (ClickUp, GitHub, etc.)       │
└─────────────────────────────────────────┘
```

## Diferencias con Telegram

| Aspecto | Telegram | Slack |
|---------|----------|-------|
| Librería | python-telegram-bot | slack-bolt |
| Conexión | Long polling | Socket Mode |
| Formato | Markdown | mrkdwn (Slack) |
| Threads | No nativo | Sí, responde en thread |
| Comandos | /comando | /comando slash |
| Menciones | @bot_username | @Claudio |

## Próximos pasos

- [ ] Soporte para archivos/imágenes
- [ ] Botones interactivos
- [ ] Modals para formularios
- [ ] Shortcuts de Slack
