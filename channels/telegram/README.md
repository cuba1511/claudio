# Claudio - Canal Telegram

Bot de Telegram que conecta con Claude Code CLI local, dando acceso a todos los MCPs configurados.

## Arquitectura

```
Usuario (Telegram) → Bot → Claude Code CLI → MCPs
                              ↓
                         ~/.claude.json
                         (MCPs configurados)
```

## Setup

### 1. Instalar dependencias

```bash
cd channels/telegram
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus valores
```

Variables requeridas:
- `TELEGRAM_BOT_TOKEN` - Token de @BotFather
- `ALLOWED_USER_IDS` - Tu ID de Telegram (usa @userinfobot)

### 3. Verificar MCPs en Claude Code

Los MCPs deben estar configurados en `~/.claude.json`:
- ClickUp
- GitHub
- Slack
- Google Docs
- Granola

Ver `mcp/claude-code-config.example.json` como referencia.

### 4. Ejecutar

```bash
./start.sh
```

O manualmente:
```bash
cd /Users/ignaciodelacuba/Dev/claudio
python channels/telegram/bot.py
```

## Funcionalidades

El bot tiene acceso a todo lo que Claude Code puede hacer:

- **ClickUp**: Crear User Stories, Epics, Initiatives
- **GitHub**: Consultar PRs, crear issues
- **Slack**: Leer y enviar mensajes
- **Google Docs**: Crear y editar documentos
- **Granola**: Acceder a notas de reuniones
- **Terminal**: Ejecutar comandos en el workspace

## Comandos

| Comando | Descripción |
|---------|-------------|
| `/start` | Mensaje de bienvenida |
| `/help` | Ayuda detallada |
| `/new` | Nueva conversación (limpia contexto) |
| `/status` | Estado del bot y MCPs |
| `/myid` | Muestra tu ID de Telegram |

## Seguridad

- Solo usuarios en `ALLOWED_USER_IDS` pueden usar el bot
- Rate limiting para prevenir spam
- Timeout en comandos para prevenir bloqueos
- Lock file para prevenir múltiples instancias

## Transcripción de Voz

El bot puede transcribir mensajes de voz usando OpenAI Whisper.

Configura `OPENAI_API_KEY` en `.env` para habilitar.
