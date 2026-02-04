#!/usr/bin/env python3
"""
Bot de Slack que conecta con Claude Code CLI local.
Permite ejecutar comandos y MCPs desde Slack como si fuera la terminal local.

Soporta:
- DMs directos al bot
- Menciones en canales (@Claudio ...)
"""

import os
import subprocess
import logging
import asyncio
import re
import tempfile
import sys
import atexit
import time
from typing import Optional, Callable
from dotenv import load_dotenv

# Slack Bolt
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# OpenAI para transcripción de voz (opcional)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# File locking para prevenir múltiples instancias
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============== CONFIGURACIÓN ==============

# Tokens de Slack
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')  # xoxb-...
SLACK_APP_TOKEN = os.getenv('SLACK_APP_TOKEN')  # xapp-...

# Claude CLI
CLAUDE_CLI_PATH = os.getenv('CLAUDE_CLI_PATH', 'claude')
WORKSPACE_PATH = os.getenv('WORKSPACE_PATH', os.getcwd())

# Límites de Slack
MAX_MESSAGE_LENGTH = 3000  # Slack tiene límite de ~4000, dejamos margen

# Seguridad
COMMAND_TIMEOUT = float(os.getenv('COMMAND_TIMEOUT', '1800'))  # 30 min default
MAX_INPUT_LENGTH = int(os.getenv('MAX_INPUT_LENGTH', '10000'))

# Rate limiting
RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', '10'))
RATE_LIMIT_WINDOW = float(os.getenv('RATE_LIMIT_WINDOW', '60'))

# Usuarios permitidos (Slack User IDs)
# Formato: "U1234567890,U0987654321" o vacío para permitir todos
ALLOWED_USER_IDS = [
    uid.strip() 
    for uid in os.getenv('SLACK_ALLOWED_USER_IDS', '').split(',') 
    if uid.strip()
]

# Herramientas permitidas
ALLOWED_TOOLS = os.getenv('ALLOWED_TOOLS', '*')
SKIP_PERMISSIONS = os.getenv('SKIP_PERMISSIONS', 'true').lower() == 'true'

# OpenAI para transcripción
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '').strip()

# ============== ESTADO GLOBAL ==============

# Sesiones por usuario
user_sessions = {}

# Rate limiting tracker
rate_limit_tracker = {}

# Lock file
LOCK_FILE_PATH = os.path.join(tempfile.gettempdir(), 'slack_claude_bot.lock')
lock_file_handle = None


# ============== UTILIDADES ==============

def acquire_lock():
    """Adquiere lock file para prevenir múltiples instancias."""
    global lock_file_handle
    
    try:
        lock_file_handle = open(LOCK_FILE_PATH, 'w')
        lock_file_handle.write(str(os.getpid()))
        lock_file_handle.flush()
        
        if HAS_FCNTL:
            fcntl.flock(lock_file_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        else:
            # Fallback: verificar PID
            try:
                with open(LOCK_FILE_PATH, 'r') as f:
                    old_pid = int(f.read().strip())
                try:
                    os.kill(old_pid, 0)
                    logger.warning(f"Another instance may be running (PID: {old_pid})")
                    lock_file_handle.close()
                    return False
                except ProcessLookupError:
                    pass
            except (FileNotFoundError, ValueError):
                pass
        
        atexit.register(release_lock)
        return True
        
    except (IOError, OSError) as e:
        if lock_file_handle:
            lock_file_handle.close()
        logger.error(f"Could not acquire lock file: {e}")
        return False


def release_lock():
    """Libera el lock file."""
    global lock_file_handle
    
    try:
        if lock_file_handle:
            if HAS_FCNTL:
                fcntl.flock(lock_file_handle.fileno(), fcntl.LOCK_UN)
            lock_file_handle.close()
        
        if os.path.exists(LOCK_FILE_PATH):
            os.remove(LOCK_FILE_PATH)
            
        logger.info("Lock file released.")
    except Exception as e:
        logger.debug(f"Error releasing lock: {e}")


def remove_ansi_codes(text: str) -> str:
    """Elimina códigos ANSI del texto."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def is_user_authorized(user_id: str) -> bool:
    """Verifica si un usuario está autorizado."""
    if not ALLOWED_USER_IDS:
        logger.warning(f"SLACK_ALLOWED_USER_IDS no configurado. Permitiendo acceso a {user_id}")
        return True
    return user_id in ALLOWED_USER_IDS


def check_rate_limit(user_id: str) -> tuple[bool, float]:
    """Verifica rate limiting para un usuario."""
    current_time = time.time()
    
    if user_id in rate_limit_tracker:
        rate_limit_tracker[user_id] = [
            ts for ts in rate_limit_tracker[user_id]
            if current_time - ts < RATE_LIMIT_WINDOW
        ]
    else:
        rate_limit_tracker[user_id] = []
    
    request_count = len(rate_limit_tracker[user_id])
    
    if request_count >= RATE_LIMIT_REQUESTS:
        oldest_timestamp = min(rate_limit_tracker[user_id])
        time_until_reset = RATE_LIMIT_WINDOW - (current_time - oldest_timestamp)
        return False, max(0, time_until_reset)
    
    rate_limit_tracker[user_id].append(current_time)
    return True, 0


def split_message(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> list:
    """Divide un mensaje largo en partes."""
    if len(text) <= max_length:
        return [text]
    
    parts = []
    current = text
    
    while len(current) > max_length:
        split_pos = current.rfind('\n', 0, max_length)
        if split_pos == -1:
            split_pos = max_length
        
        parts.append(current[:split_pos])
        current = current[split_pos:].lstrip()
    
    if current:
        parts.append(current)
    
    return parts


# ============== CLAUDE CODE EXECUTOR ==============

class ClaudeCodeExecutor:
    """Ejecutor de comandos Claude Code CLI."""
    
    def __init__(self, workspace_path: str = None):
        self.workspace_path = workspace_path or WORKSPACE_PATH
        self.claude_path = CLAUDE_CLI_PATH
        self.active_processes = []
    
    def cleanup_processes(self):
        """Mata procesos activos de Claude CLI."""
        for process_info in self.active_processes[:]:
            try:
                pid, process = process_info
                if process.returncode is None:
                    logger.warning(f"Killing orphaned Claude CLI process (PID: {pid})")
                    process.kill()
                    process.wait()
            except Exception as e:
                logger.debug(f"Error cleaning up process: {e}")
        self.active_processes.clear()
    
    async def execute_streaming(
        self, 
        query: str, 
        user_id: str, 
        continue_session: bool,
        output_callback: Callable[[str], None],
        error_callback: Optional[Callable[[str], None]] = None
    ) -> dict:
        """Ejecuta comando en Claude Code CLI con streaming."""
        try:
            cmd = [self.claude_path]
            
            if continue_session and user_id in user_sessions:
                cmd.append('-c')
                logger.info(f"[Usuario {user_id}] Continuando sesión anterior")
            
            if SKIP_PERMISSIONS:
                cmd.append('--dangerously-skip-permissions')
            elif ALLOWED_TOOLS and ALLOWED_TOOLS != '*':
                cmd.extend(['--allowedTools', ALLOWED_TOOLS])
            
            cmd.extend(['-p', query])
            
            env = os.environ.copy()
            env['PWD'] = self.workspace_path
            
            logger.info(f"[Usuario {user_id}] Ejecutando: {' '.join(cmd[:3])}...")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.workspace_path,
                env=env
            )
            
            process_pid = process.pid
            self.active_processes.append((process_pid, process))
            
            async def read_stream(stream, is_error=False):
                buffer = b''
                while True:
                    chunk = await stream.read(1024)
                    if not chunk:
                        break
                    buffer += chunk
                    try:
                        text = buffer.decode('utf-8', errors='replace')
                        while '\n' in text:
                            line, text = text.split('\n', 1)
                            cleaned = remove_ansi_codes(line)
                            if cleaned.strip():
                                if is_error:
                                    logger.warning(f"[Usuario {user_id}] STDERR: {cleaned[:100]}")
                                    if error_callback:
                                        await error_callback(cleaned)
                                else:
                                    await output_callback(cleaned + '\n')
                        buffer = text.encode('utf-8', errors='replace')
                    except Exception as e:
                        logger.error(f"[Usuario {user_id}] Error decodificando: {e}")
                
                if buffer:
                    try:
                        text = buffer.decode('utf-8', errors='replace')
                        cleaned = remove_ansi_codes(text)
                        if cleaned.strip():
                            if is_error and error_callback:
                                await error_callback(cleaned)
                            elif not is_error:
                                await output_callback(cleaned)
                    except Exception as e:
                        logger.error(f"[Usuario {user_id}] Error buffer final: {e}")
            
            try:
                await asyncio.wait_for(
                    asyncio.gather(
                        read_stream(process.stdout, is_error=False),
                        read_stream(process.stderr, is_error=True)
                    ),
                    timeout=COMMAND_TIMEOUT
                )
                returncode = await process.wait()
            except asyncio.TimeoutError:
                logger.warning(f"[Usuario {user_id}] TIMEOUT: {COMMAND_TIMEOUT}s")
                try:
                    process.kill()
                    await process.wait()
                    self.active_processes = [p for p in self.active_processes if p[0] != process_pid]
                except Exception as kill_error:
                    logger.error(f"Error matando proceso: {kill_error}")
                
                return {'success': False, 'returncode': -2, 'timeout': True}
            
            success = returncode == 0
            logger.info(f"[Usuario {user_id}] Completado con código: {returncode}")
            
            self.active_processes = [p for p in self.active_processes if p[0] != process_pid]
            
            return {'success': success, 'returncode': returncode}
            
        except FileNotFoundError:
            error_msg = f'Claude CLI no encontrado en: {self.claude_path}'
            logger.error(f"[Usuario {user_id}] {error_msg}")
            if error_callback:
                await error_callback(error_msg)
            return {'success': False, 'returncode': -1}
        except Exception as e:
            error_msg = f'Error ejecutando comando: {str(e)}'
            logger.error(f"[Usuario {user_id}] {error_msg}", exc_info=True)
            if error_callback:
                await error_callback(error_msg)
            return {'success': False, 'returncode': -1}


# ============== SLACK APP ==============

# IMPORTANTE: Eliminar variables de OAuth del entorno para que Bolt no las detecte
# Queremos usar el BOT_TOKEN directamente, no OAuth flow
for var in ['SLACK_CLIENT_ID', 'SLACK_CLIENT_SECRET']:
    if var in os.environ:
        del os.environ[var]

# Inicializar app de Slack con token directo
app = App(token=SLACK_BOT_TOKEN)

# Executor global
executor = ClaudeCodeExecutor()


def get_bot_user_id():
    """Obtiene el User ID del bot."""
    try:
        response = app.client.auth_test()
        return response["user_id"]
    except Exception as e:
        logger.error(f"Error obteniendo bot user ID: {e}")
        return None


BOT_USER_ID = None  # Se inicializa en main()


async def process_message(user_id: str, text: str, say, channel: str, thread_ts: str = None):
    """Procesa un mensaje y ejecuta en Claude CLI."""
    
    # Verificar autorización
    if not is_user_authorized(user_id):
        logger.warning(f"[SEGURIDAD] Usuario no autorizado: {user_id}")
        say(
            text="❌ *Acceso denegado*\n\nNo estás autorizado para usar este bot.",
            thread_ts=thread_ts
        )
        return
    
    # Rate limiting
    is_allowed, time_until_reset = check_rate_limit(user_id)
    if not is_allowed:
        logger.warning(f"[SEGURIDAD] Rate limit excedido: {user_id}")
        say(
            text=f"⏱️ *Rate limit excedido*\n\nEspera {int(time_until_reset)} segundos.",
            thread_ts=thread_ts
        )
        return
    
    # Validar longitud
    if len(text) > MAX_INPUT_LENGTH:
        say(
            text=f"❌ *Mensaje demasiado largo*\n\nMáximo: {MAX_INPUT_LENGTH:,} caracteres.",
            thread_ts=thread_ts
        )
        return
    
    logger.info(f"[Usuario {user_id}] Procesando: {text[:100]}...")
    
    # Mostrar que está procesando
    result = app.client.chat_postMessage(
        channel=channel,
        text="⏳ Procesando...",
        thread_ts=thread_ts
    )
    processing_ts = result["ts"]
    
    # Acumular output
    all_output = []
    has_received_output = False
    
    async def handle_output(text_chunk: str):
        nonlocal all_output, has_received_output
        if text_chunk.strip():
            has_received_output = True
            all_output.append(text_chunk)
    
    async def handle_error(error_text: str):
        nonlocal all_output, has_received_output
        if error_text.strip():
            has_received_output = True
            all_output.append(f"⚠️ {error_text}\n")
    
    # Ejecutar
    continue_session = user_id in user_sessions
    
    result = await executor.execute_streaming(
        text,
        user_id,
        continue_session,
        handle_output,
        handle_error
    )
    
    # Enviar respuesta
    if all_output:
        combined = ''.join(all_output)
        cleaned = remove_ansi_codes(combined)
        
        if cleaned.strip():
            parts = split_message(cleaned)
            
            # Actualizar mensaje de "procesando" con la primera parte
            try:
                app.client.chat_update(
                    channel=channel,
                    ts=processing_ts,
                    text=parts[0]
                )
            except Exception as e:
                logger.error(f"Error actualizando mensaje: {e}")
                say(text=parts[0], thread_ts=thread_ts)
            
            # Enviar partes adicionales
            for part in parts[1:]:
                say(text=part, thread_ts=thread_ts)
    
    elif result.get('timeout'):
        try:
            app.client.chat_update(
                channel=channel,
                ts=processing_ts,
                text=f"⏱️ *Timeout alcanzado*\n\nEl comando excedió {COMMAND_TIMEOUT}s."
            )
        except:
            say(text=f"⏱️ *Timeout*\nComando excedió {COMMAND_TIMEOUT}s.", thread_ts=thread_ts)
    
    elif not result['success']:
        try:
            app.client.chat_update(
                channel=channel,
                ts=processing_ts,
                text=f"❌ *Error* (código: {result['returncode']})"
            )
        except:
            say(text=f"❌ Error (código: {result['returncode']})", thread_ts=thread_ts)
    
    else:
        try:
            app.client.chat_update(
                channel=channel,
                ts=processing_ts,
                text="✅ Comando ejecutado exitosamente."
            )
        except:
            pass
    
    # Marcar sesión activa
    if result['success']:
        user_sessions[user_id] = True


# ============== SYNC PROCESS MESSAGE ==============

def process_message_sync(user_id: str, text: str, say, channel: str, thread_ts: str = None):
    """Procesa un mensaje usando subprocess - igual que Telegram."""
    import threading
    
    # Verificar autorización
    if not is_user_authorized(user_id):
        logger.warning(f"[SEGURIDAD] Usuario no autorizado: {user_id}")
        say(text="❌ *Acceso denegado*\n\nNo estás autorizado para usar este bot.", thread_ts=thread_ts)
        return
    
    # Rate limiting
    is_allowed, time_until_reset = check_rate_limit(user_id)
    if not is_allowed:
        say(text=f"⏱️ *Rate limit excedido*\n\nEspera {int(time_until_reset)} segundos.", thread_ts=thread_ts)
        return
    
    # Validar longitud
    if len(text) > MAX_INPUT_LENGTH:
        say(text=f"❌ *Mensaje demasiado largo*\n\nMáximo: {MAX_INPUT_LENGTH:,} caracteres.", thread_ts=thread_ts)
        return
    
    logger.info(f"[Usuario {user_id}] Procesando: {text[:100]}...")
    
    # Mostrar que está procesando
    try:
        result = app.client.chat_postMessage(
            channel=channel,
            text="⏳ Procesando...",
            thread_ts=thread_ts
        )
        processing_ts = result["ts"]
    except Exception as e:
        logger.error(f"Error enviando mensaje de procesando: {e}")
        processing_ts = None
    
    def run_claude():
        """Ejecuta Claude CLI en un thread separado."""
        try:
            # Construir comando - EXACTAMENTE igual que Telegram
            cmd = [CLAUDE_CLI_PATH]
            
            # Cargar configuración de MCPs explícitamente
            mcp_config_path = os.path.expanduser("~/.cursor/mcp.json")
            if os.path.exists(mcp_config_path):
                cmd.extend(['--mcp-config', mcp_config_path])
                logger.info(f"[Usuario {user_id}] Cargando MCPs desde {mcp_config_path}")
            
            # Continuar sesión si existe
            if user_id in user_sessions:
                cmd.append('-c')
                logger.info(f"[Usuario {user_id}] Continuando sesión anterior")
            
            # Agregar flags para aprobar automáticamente herramientas/MCPs
            if SKIP_PERMISSIONS:
                cmd.append('--dangerously-skip-permissions')
            elif ALLOWED_TOOLS and ALLOWED_TOOLS != '*':
                cmd.extend(['--allowedTools', ALLOWED_TOOLS])
            
            # Agregar -p para modo no interactivo y la query
            cmd.extend(['-p', text])
            
            # Configurar entorno - EXACTAMENTE igual que Telegram
            env = os.environ.copy()
            env['PWD'] = WORKSPACE_PATH
            
            logger.info(f"[Usuario {user_id}] Ejecutando: {' '.join(cmd[:4])}...")
            logger.debug(f"[Usuario {user_id}] Comando completo: {' '.join(cmd)}")
            
            # Ejecutar Claude CLI
            # IMPORTANTE: stdin=subprocess.DEVNULL evita que se quede esperando input
            start_time = time.time()
            logger.info(f"[Usuario {user_id}] Iniciando subprocess.run()...")
            
            process_result = subprocess.run(
                cmd,
                stdin=subprocess.DEVNULL,  # Evita bloqueo esperando input
                capture_output=True,
                text=True,
                timeout=COMMAND_TIMEOUT,
                cwd=WORKSPACE_PATH,
                env=env
            )
            
            elapsed = time.time() - start_time
            logger.info(f"[Usuario {user_id}] subprocess.run() terminó en {elapsed:.2f}s")
            
            output = process_result.stdout or ""
            stderr = process_result.stderr or ""
            
            logger.info(f"[Usuario {user_id}] stdout: {len(output)} chars, stderr: {len(stderr)} chars")
            
            # Limpiar output
            cleaned_output = remove_ansi_codes(output).strip()
            
            if stderr:
                logger.warning(f"[Usuario {user_id}] STDERR: {stderr[:500]}")
                # Incluir stderr en el output si hay error
                if process_result.returncode != 0 and not cleaned_output:
                    cleaned_output = f"⚠️ {remove_ansi_codes(stderr).strip()}"
            
            logger.info(f"[Usuario {user_id}] Completado con código: {process_result.returncode}")
            
            # Enviar respuesta
            if cleaned_output:
                parts = split_message(cleaned_output)
                
                if processing_ts:
                    try:
                        app.client.chat_update(channel=channel, ts=processing_ts, text=parts[0])
                    except Exception as e:
                        logger.error(f"Error actualizando mensaje: {e}")
                        say(text=parts[0], thread_ts=thread_ts)
                else:
                    say(text=parts[0], thread_ts=thread_ts)
                
                for part in parts[1:]:
                    say(text=part, thread_ts=thread_ts)
            else:
                if processing_ts:
                    try:
                        app.client.chat_update(channel=channel, ts=processing_ts, text="✅ Listo.")
                    except:
                        pass
            
            # Marcar sesión activa
            if process_result.returncode == 0:
                user_sessions[user_id] = True
                
        except subprocess.TimeoutExpired:
            logger.warning(f"[Usuario {user_id}] TIMEOUT: {COMMAND_TIMEOUT}s")
            msg = f"⏱️ *Timeout*\n\nEl comando excedió {COMMAND_TIMEOUT}s."
            if processing_ts:
                try:
                    app.client.chat_update(channel=channel, ts=processing_ts, text=msg)
                except:
                    say(text=msg, thread_ts=thread_ts)
            else:
                say(text=msg, thread_ts=thread_ts)
        except Exception as e:
            logger.error(f"[Usuario {user_id}] Error: {e}", exc_info=True)
            msg = f"❌ Error: {str(e)}"
            if processing_ts:
                try:
                    app.client.chat_update(channel=channel, ts=processing_ts, text=msg)
                except:
                    say(text=msg, thread_ts=thread_ts)
            else:
                say(text=msg, thread_ts=thread_ts)
    
    # Ejecutar en thread para no bloquear el event loop de Slack
    thread = threading.Thread(target=run_claude)
    thread.start()


# ============== EVENT HANDLERS ==============

@app.event("app_mention")
def handle_mention(event, say):
    """Maneja menciones en canales (@Claudio ...)"""
    user_id = event.get("user")
    text = event.get("text", "")
    channel = event.get("channel")
    thread_ts = event.get("thread_ts") or event.get("ts")
    
    # Remover la mención del bot del texto
    if BOT_USER_ID:
        text = re.sub(f'<@{BOT_USER_ID}>', '', text).strip()
    
    if not text:
        say(
            text="👋 ¡Hola! Soy Claudio. ¿En qué puedo ayudarte?\n\nEscribe tu pregunta después de mencionarme.",
            thread_ts=thread_ts
        )
        return
    
    logger.info(f"[Mención] Usuario {user_id} en canal {channel}: {text[:50]}...")
    
    # Ejecutar de forma síncrona
    process_message_sync(user_id, text, say, channel, thread_ts)


@app.event("message")
def handle_dm(event, say):
    """Maneja mensajes directos (DMs)"""
    # Ignorar mensajes del bot mismo
    if event.get("bot_id"):
        return
    
    # Ignorar subtipos (ediciones, etc)
    if event.get("subtype"):
        return
    
    channel_type = event.get("channel_type")
    
    # Solo procesar DMs (im = instant message)
    if channel_type != "im":
        return
    
    user_id = event.get("user")
    text = event.get("text", "")
    channel = event.get("channel")
    thread_ts = event.get("thread_ts") or event.get("ts")
    
    if not text:
        return
    
    logger.info(f"[DM] Usuario {user_id}: {text[:50]}...")
    
    # Ejecutar de forma síncrona
    process_message_sync(user_id, text, say, channel, thread_ts)


# ============== COMANDOS SLASH (opcional) ==============

@app.command("/claudio")
def handle_slash_command(ack, respond, command):
    """Maneja el comando /claudio"""
    ack()  # Acknowledge inmediatamente
    
    user_id = command.get("user_id")
    text = command.get("text", "").strip()
    channel = command.get("channel_id")
    
    if not text:
        respond("👋 Soy Claudio. Usa `/claudio [tu pregunta]` para interactuar conmigo.")
        return
    
    logger.info(f"[Slash] Usuario {user_id}: {text[:50]}...")
    
    # Para slash commands, usamos respond en vez de say
    def say_wrapper(text, thread_ts=None):
        respond(text)
    
    asyncio.run(process_message(user_id, text, say_wrapper, channel))


@app.command("/claudio-new")
def handle_new_conversation(ack, respond, command):
    """Inicia una nueva conversación (limpia contexto)"""
    ack()
    
    user_id = command.get("user_id")
    
    if user_id in user_sessions:
        del user_sessions[user_id]
    
    respond("✨ Nueva conversación iniciada. El contexto anterior ha sido limpiado.")
    logger.info(f"[Usuario {user_id}] Nueva conversación iniciada")


@app.command("/claudio-status")
def handle_status(ack, respond, command):
    """Muestra el estado del bot"""
    ack()
    
    user_id = command.get("user_id")
    
    # Verificar Claude CLI
    try:
        result = subprocess.run(
            [CLAUDE_CLI_PATH, '--version'],
            capture_output=True,
            timeout=5,
            cwd=WORKSPACE_PATH
        )
        claude_status = "✅ Disponible"
        if result.stdout:
            claude_status += f" ({result.stdout.decode().strip()})"
    except Exception:
        claude_status = "❌ No disponible"
    
    is_authorized = is_user_authorized(user_id)
    
    status_text = (
        f"📊 *Estado del Bot Claudio*\n\n"
        f"*Claude CLI:* {claude_status}\n"
        f"*Workspace:* `{WORKSPACE_PATH}`\n"
        f"*Tu User ID:* `{user_id}`\n"
        f"*Autorizado:* {'✅ Sí' if is_authorized else '❌ No'}\n"
        f"*Sesión activa:* {'Sí' if user_id in user_sessions else 'No'}\n"
    )
    
    respond(status_text)


# ============== MAIN ==============

def main():
    """Función principal."""
    global BOT_USER_ID
    
    # Prevenir múltiples instancias
    if not acquire_lock():
        print("\n" + "="*70)
        print("❌ ERROR: Otra instancia del bot está ejecutándose")
        print("="*70)
        print("Solo puede haber una instancia del bot ejecutándose a la vez.")
        print("\nPara solucionarlo:")
        print("1. Busca procesos con: ps aux | grep slack.*bot")
        print("2. Mata procesos duplicados con: kill <PID>")
        print("="*70 + "\n")
        sys.exit(1)
    
    # Validar tokens
    if not SLACK_BOT_TOKEN:
        logger.error("SLACK_BOT_TOKEN no configurado en .env")
        print("\n❌ ERROR: SLACK_BOT_TOKEN no está configurado.")
        print("Obtén tu token en: https://api.slack.com/apps")
        release_lock()
        sys.exit(1)
    
    if not SLACK_APP_TOKEN:
        logger.error("SLACK_APP_TOKEN no configurado en .env")
        print("\n❌ ERROR: SLACK_APP_TOKEN no está configurado.")
        print("Habilita Socket Mode en tu Slack App y genera un App Token.")
        release_lock()
        sys.exit(1)
    
    # Obtener Bot User ID
    BOT_USER_ID = get_bot_user_id()
    if BOT_USER_ID:
        logger.info(f"✅ Bot User ID: {BOT_USER_ID}")
    else:
        logger.warning("⚠️ No se pudo obtener Bot User ID")
    
    # Mostrar configuración
    logger.info(f"✅ Workspace: {WORKSPACE_PATH}")
    logger.info(f"✅ Claude CLI: {CLAUDE_CLI_PATH}")
    
    if ALLOWED_USER_IDS:
        logger.info(f"✅ Usuarios autorizados: {len(ALLOWED_USER_IDS)}")
    else:
        logger.warning("⚠️ SLACK_ALLOWED_USER_IDS no configurado - todos pueden usar el bot")
    
    print("\n" + "="*50)
    print("🤖 Bot Claudio de Slack iniciado")
    print("="*50)
    print(f"Workspace: {WORKSPACE_PATH}")
    print(f"Bot User ID: {BOT_USER_ID}")
    print("\nEl bot escucha:")
    print("  - DMs directos")
    print("  - Menciones (@Claudio) en canales")
    print("  - Comandos: /claudio, /claudio-new, /claudio-status")
    print("\nPresiona Ctrl+C para detener.")
    print("="*50 + "\n")
    
    # Iniciar Socket Mode
    try:
        handler = SocketModeHandler(app, SLACK_APP_TOKEN)
        handler.start()
    except KeyboardInterrupt:
        logger.info("Bot detenido por el usuario.")
    except Exception as e:
        logger.error(f"Error en el bot: {e}", exc_info=True)
    finally:
        executor.cleanup_processes()
        release_lock()


if __name__ == '__main__':
    main()
