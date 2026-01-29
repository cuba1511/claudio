#!/usr/bin/env python3
"""
Bot de Telegram que conecta con Claude Code CLI local.
Permite ejecutar comandos y MCPs desde Telegram como si fuera la terminal local.
"""

import os
import subprocess
import logging
import asyncio
import re
import tempfile
from typing import Optional, Callable
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.error import Conflict
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Verificar disponibilidad de OpenAI (ya se verificó arriba, solo loguear si falta)
if not OPENAI_AVAILABLE:
    logger.warning("OpenAI no está instalado. La transcripción de voz no funcionará. Instala con: pip install openai")

# Variables de configuración
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CLAUDE_CLI_PATH = os.getenv('CLAUDE_CLI_PATH', 'claude')  # Ruta al ejecutable de Claude CLI
WORKSPACE_PATH = os.getenv('WORKSPACE_PATH', os.getcwd())  # Directorio de trabajo
MAX_MESSAGE_LENGTH = 4096  # Límite de Telegram
BUFFER_TIMEOUT = float(os.getenv('BUFFER_TIMEOUT', '1.5'))  # Segundos para acumular salida antes de enviar
# SEGURIDAD: Timeout máximo para ejecución de comandos (en segundos)
# Previene que comandos maliciosos bloqueen el bot indefinidamente
COMMAND_TIMEOUT = float(os.getenv('COMMAND_TIMEOUT', '300'))  # Por defecto 5 minutos
# SEGURIDAD: Longitud máxima de input para prevenir DoS por mensajes gigantes
# Previene que usuarios envíen mensajes extremadamente largos que consuman recursos
MAX_INPUT_LENGTH = int(os.getenv('MAX_INPUT_LENGTH', '10000'))  # Por defecto 10,000 caracteres

# SEGURIDAD: Rate limiting para prevenir spam/DoS
# Máximo número de requests permitidas por ventana de tiempo
RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', '10'))  # Por defecto 10 requests
RATE_LIMIT_WINDOW = float(os.getenv('RATE_LIMIT_WINDOW', '60'))  # Por defecto 60 segundos (1 minuto)

# Configuración de transcripción de voz
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '').strip()  # API key de OpenAI para Whisper
USE_WHISPER_API = os.getenv('USE_WHISPER_API', 'true').lower() == 'true'  # Usar API o modelo local

# Log inicial de configuración
if OPENAI_API_KEY:
    logger.info(f"OpenAI API key configurada: {OPENAI_API_KEY[:10]}...{OPENAI_API_KEY[-4:]}")
else:
    logger.warning("OPENAI_API_KEY no configurada. La transcripción de voz no funcionará.")

# Herramientas permitidas automáticamente (para MCPs y herramientas sin prompts)
# Por defecto permite todas las herramientas. Puedes restringir con: "Read,Edit,Bash"
ALLOWED_TOOLS = os.getenv('ALLOWED_TOOLS', '*')  # '*' permite todas las herramientas

# Usar --dangerously-skip-permissions para bypass todos los checks de permisos
# Esto es necesario porque los wildcards no funcionan con MCPs y -p no puede mostrar prompts
SKIP_PERMISSIONS = os.getenv('SKIP_PERMISSIONS', 'true').lower() == 'true'

# Seguridad: Lista de IDs de usuario de Telegram autorizados
# Formato: "123456789,987654321" o un solo ID: "123456789"
# Si está vacío, cualquier usuario puede usar el bot (NO RECOMENDADO)
ALLOWED_USER_IDS = [
    int(uid.strip()) 
    for uid in os.getenv('ALLOWED_USER_IDS', '').split(',') 
    if uid.strip()
]

# Almacenar conversaciones por usuario
user_sessions = {}

# Almacenar procesos activos por usuario (para modo interactivo)
active_processes = {}

# SEGURIDAD: Rate limiting - rastrear timestamps de requests por usuario
# Estructura: {user_id: [timestamp1, timestamp2, ...]}
rate_limit_tracker = {}


def remove_ansi_codes(text: str) -> str:
    """
    Elimina códigos ANSI (colores y caracteres de escape) del texto.
    
    Args:
        text: Texto que puede contener códigos ANSI
        
    Returns:
        Texto limpio sin códigos ANSI
    """
    # Patrón para códigos ANSI (CSI sequences)
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


class OutputBuffer:
    """Buffer inteligente que acumula salida y la envía después de un timeout."""
    
    def __init__(self, callback: Callable, timeout: float = BUFFER_TIMEOUT):
        self.buffer = ""
        self.callback = callback
        self.timeout = timeout
        self.last_update = None
        self.task = None
        self.lock = asyncio.Lock()
    
    async def append(self, text: str):
        """Agrega texto al buffer y programa el envío."""
        async with self.lock:
            self.buffer += text
            self.last_update = asyncio.get_event_loop().time()
            
            # Cancelar task anterior si existe
            if self.task and not self.task.done():
                self.task.cancel()
            
            # Programar nuevo envío
            self.task = asyncio.create_task(self._send_after_timeout())
    
    async def _send_after_timeout(self):
        """Espera el timeout y envía el buffer."""
        try:
            await asyncio.sleep(self.timeout)
            async with self.lock:
                if self.buffer:
                    text = self.buffer
                    self.buffer = ""
                    await self.callback(text)
        except asyncio.CancelledError:
            pass
    
    async def flush(self):
        """Fuerza el envío inmediato del buffer."""
        async with self.lock:
            if self.task and not self.task.done():
                self.task.cancel()
            if self.buffer:
                text = self.buffer
                self.buffer = ""
                await self.callback(text)


class ClaudeCodeExecutor:
    """Ejecutor de comandos Claude Code CLI con lectura en tiempo real."""
    
    def __init__(self, workspace_path: str = None):
        self.workspace_path = workspace_path or WORKSPACE_PATH
        self.claude_path = CLAUDE_CLI_PATH
    
    async def execute_streaming(
        self, 
        query: str, 
        user_id: int, 
        continue_session: bool,
        output_callback: Callable[[str], None],
        error_callback: Optional[Callable[[str], None]] = None
    ) -> dict:
        """
        Ejecuta un comando en Claude Code CLI con lectura en tiempo real.
        
        Args:
            query: El mensaje/comando a ejecutar
            user_id: ID del usuario para mantener sesiones separadas
            continue_session: Si True, continúa la conversación anterior usando -c
            output_callback: Función async que se llama con cada fragmento de salida
            error_callback: Función async opcional para manejar errores
            
        Returns:
            dict con 'success', 'returncode'
        """
        try:
            # Construir comando
            cmd = [self.claude_path]
            
            # Si hay una sesión previa y queremos continuarla, usar -c (continue)
            if continue_session and user_id in user_sessions:
                cmd.append('-c')
                logger.info(f"[Usuario {user_id}] Continuando sesión anterior")
            
            # Agregar flags para aprobar automáticamente herramientas/MCPs
            if SKIP_PERMISSIONS:
                cmd.append('--dangerously-skip-permissions')
            elif ALLOWED_TOOLS and ALLOWED_TOOLS != '*':
                cmd.extend(['--allowedTools', ALLOWED_TOOLS])
            
            # Agregar -p para modo no interactivo y la query
            cmd.extend(['-p', query])
            
            # Configurar entorno
            env = os.environ.copy()
            env['PWD'] = self.workspace_path
            
            logger.info(f"[Usuario {user_id}] Ejecutando comando: {' '.join(cmd[:3])}... (query: {query[:50]}...)")
            logger.debug(f"[Usuario {user_id}] Comando completo: {' '.join(cmd)}")
            
            # Ejecutar comando con lectura en tiempo real
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.workspace_path,
                env=env
            )
            
            # Leer stdout y stderr en paralelo
            async def read_stream(stream, is_error=False):
                buffer = b''
                while True:
                    chunk = await stream.read(1024)
                    if not chunk:
                        break
                    buffer += chunk
                    # Intentar decodificar líneas completas
                    try:
                        text = buffer.decode('utf-8', errors='replace')
                        # Buscar líneas completas
                        while '\n' in text:
                            line, text = text.split('\n', 1)
                            cleaned = remove_ansi_codes(line)
                            if cleaned.strip():
                                if is_error:
                                    logger.warning(f"[Usuario {user_id}] STDERR: {cleaned[:100]}")
                                    if error_callback:
                                        await error_callback(cleaned)
                                else:
                                    logger.debug(f"[Usuario {user_id}] STDOUT: {cleaned[:100]}")
                                    await output_callback(cleaned + '\n')
                        buffer = text.encode('utf-8', errors='replace')
                    except Exception as e:
                        logger.error(f"[Usuario {user_id}] Error decodificando stream: {e}")
                
                # Procesar buffer restante
                if buffer:
                    try:
                        text = buffer.decode('utf-8', errors='replace')
                        cleaned = remove_ansi_codes(text)
                        if cleaned.strip():
                            if is_error:
                                logger.warning(f"[Usuario {user_id}] STDERR final: {cleaned[:100]}")
                                if error_callback:
                                    await error_callback(cleaned)
                            else:
                                logger.debug(f"[Usuario {user_id}] STDOUT final: {cleaned[:100]}")
                                await output_callback(cleaned)
                    except Exception as e:
                        logger.error(f"[Usuario {user_id}] Error decodificando buffer final: {e}")
            
            # SEGURIDAD: Ejecutar con timeout para prevenir comandos que bloqueen el bot
            try:
                # Leer ambos streams en paralelo con timeout
                await asyncio.wait_for(
                    asyncio.gather(
                        read_stream(process.stdout, is_error=False),
                        read_stream(process.stderr, is_error=True)
                    ),
                    timeout=COMMAND_TIMEOUT
                )
                
                # Esperar a que el proceso termine
                returncode = await process.wait()
            except asyncio.TimeoutError:
                # Timeout alcanzado - matar el proceso
                logger.warning(f"[Usuario {user_id}] ⚠️ TIMEOUT: Comando excedió {COMMAND_TIMEOUT}s. Terminando proceso...")
                try:
                    process.kill()
                    await process.wait()
                except Exception as kill_error:
                    logger.error(f"[Usuario {user_id}] Error matando proceso: {kill_error}")
                
                timeout_msg = (
                    f"⏱️ *Timeout alcanzado*\n\n"
                    f"El comando excedió el tiempo máximo permitido ({COMMAND_TIMEOUT}s) "
                    f"y fue terminado por seguridad.\n\n"
                    f"Esto previene que comandos maliciosos bloqueen el bot indefinidamente."
                )
                if error_callback:
                    await error_callback(timeout_msg)
                
                return {
                    'success': False,
                    'returncode': -2,  # Código especial para timeout
                    'timeout': True
                }
            
            success = returncode == 0
            logger.info(f"[Usuario {user_id}] Comando completado con código: {returncode} (éxito: {success})")
            
            return {
                'success': success,
                'returncode': returncode
            }
            
        except FileNotFoundError:
            error_msg = f'Claude CLI no encontrado en: {self.claude_path}'
            logger.error(f"[Usuario {user_id}] {error_msg}")
            if error_callback:
                await error_callback(error_msg)
            return {
                'success': False,
                'returncode': -1
            }
        except Exception as e:
            error_msg = f'Error ejecutando comando: {str(e)}'
            logger.error(f"[Usuario {user_id}] {error_msg}", exc_info=True)
            if error_callback:
                await error_callback(error_msg)
            return {
                'success': False,
                'returncode': -1
            }


def is_user_authorized(user_id: int) -> bool:
    """
    Verifica si un usuario está autorizado para usar el bot.
    
    Args:
        user_id: ID del usuario de Telegram
        
    Returns:
        True si el usuario está autorizado, False en caso contrario
    """
    # Si no hay lista de usuarios permitidos, permitir a todos (modo inseguro)
    if not ALLOWED_USER_IDS:
        logger.warning(f"ALLOWED_USER_IDS no configurado. Permitiendo acceso a usuario {user_id}")
        return True
    
    return user_id in ALLOWED_USER_IDS


def check_rate_limit(user_id: int) -> tuple[bool, float]:
    """
    Verifica si un usuario ha excedido el límite de rate limiting.
    
    Args:
        user_id: ID del usuario de Telegram
        
    Returns:
        Tupla (is_allowed, time_until_reset)
        - is_allowed: True si el usuario puede hacer la request, False si excedió el límite
        - time_until_reset: Segundos hasta que se resetee la ventana (0 si está permitido)
    """
    import time
    current_time = time.time()
    
    # Limpiar timestamps antiguos (fuera de la ventana)
    if user_id in rate_limit_tracker:
        # Mantener solo timestamps dentro de la ventana
        rate_limit_tracker[user_id] = [
            ts for ts in rate_limit_tracker[user_id]
            if current_time - ts < RATE_LIMIT_WINDOW
        ]
    else:
        rate_limit_tracker[user_id] = []
    
    # Verificar si excedió el límite
    request_count = len(rate_limit_tracker[user_id])
    
    if request_count >= RATE_LIMIT_REQUESTS:
        # Calcular tiempo hasta que expire el timestamp más antiguo
        oldest_timestamp = min(rate_limit_tracker[user_id])
        time_until_reset = RATE_LIMIT_WINDOW - (current_time - oldest_timestamp)
        return False, max(0, time_until_reset)
    
    # Registrar esta request
    rate_limit_tracker[user_id].append(current_time)
    return True, 0


async def transcribe_voice_message(voice_file_path: str) -> Optional[str]:
    """
    Transcribe un archivo de audio a texto usando OpenAI Whisper API.
    
    Args:
        voice_file_path: Ruta al archivo de audio
        
    Returns:
        Texto transcrito o None si hay error
    """
    if not OPENAI_AVAILABLE:
        logger.error("OpenAI no está disponible. Instala: pip install openai")
        return None
    
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY no está configurado en .env")
        return None
    
    try:
        logger.info(f"[Transcripción] Transcribiendo audio: {voice_file_path}")
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Obtener idioma de configuración o usar español por defecto
        language = os.getenv('WHISPER_LANGUAGE', 'es')
        if language.lower() == 'none' or language == '':
            language = None
        
        with open(voice_file_path, 'rb') as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language
            )
        
        text = transcript.text.strip()
        logger.info(f"[Transcripción] Transcripción exitosa ({len(text)} caracteres): {text[:100]}...")
        return text
        
    except Exception as e:
        logger.error(f"[Transcripción] Error transcribiendo audio: {e}", exc_info=True)
        return None


async def download_voice_file(voice, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    """
    Descarga un archivo de voz de Telegram.
    
    Args:
        voice: Objeto Voice de Telegram
        context: Contexto del bot
        
    Returns:
        Ruta al archivo descargado o None si hay error
    """
    try:
        # Obtener el archivo
        file = await context.bot.get_file(voice.file_id)
        
        # Crear archivo temporal
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f"voice_{voice.file_id}.ogg")
        
        # Descargar el archivo
        await file.download_to_drive(temp_file)
        logger.info(f"Archivo de voz descargado: {temp_file}")
        
        return temp_file
        
    except Exception as e:
        logger.error(f"Error descargando archivo de voz: {e}", exc_info=True)
        return None


def split_message(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> list:
    """Divide un mensaje largo en partes más pequeñas."""
    if len(text) <= max_length:
        return [text]
    
    parts = []
    current = text
    
    while len(current) > max_length:
        # Intentar dividir en un salto de línea cercano
        split_pos = current.rfind('\n', 0, max_length)
        if split_pos == -1:
            # Si no hay salto de línea, dividir en el límite
            split_pos = max_length
        
        parts.append(current[:split_pos])
        current = current[split_pos:].lstrip()
    
    if current:
        parts.append(current)
    
    return parts


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /start."""
    user_id = update.effective_user.id
    
    # Verificar autorización
    if not is_user_authorized(user_id):
        logger.warning(f"Usuario no autorizado intentó usar el bot: {user_id} (@{update.effective_user.username})")
        await update.message.reply_text(
            "❌ *Acceso denegado*\n\n"
            "No estás autorizado para usar este bot.\n"
            "Contacta al administrador para obtener acceso.",
            parse_mode='Markdown'
        )
        return
    
    # Mostrar ID del usuario para facilitar la configuración inicial
    user_info = f"*Tu ID de usuario:* `{user_id}`\n\n"
    if not ALLOWED_USER_IDS:
        user_info += "⚠️ *Advertencia:* No hay usuarios autorizados configurados. Cualquiera puede usar el bot.\n\n"
    
    welcome_message = (
        "🤖 *Bot Claude Code CLI*\n\n"
        f"{user_info}"
        "Envía mensajes aquí y se ejecutarán en tu instancia local de Claude Code CLI.\n\n"
        "Comandos disponibles:\n"
        "/start - Muestra este mensaje\n"
        "/help - Muestra ayuda detallada\n"
        "/new - Inicia una nueva conversación\n"
        "/status - Muestra el estado del bot\n"
        "/myid - Muestra tu ID de usuario\n\n"
        "Simplemente escribe tu mensaje y se ejecutará en Claude Code."
    )
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def myid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el ID del usuario para facilitar la configuración."""
    user_id = update.effective_user.id
    username = update.effective_user.username or "sin username"
    first_name = update.effective_user.first_name or "Usuario"
    
    is_authorized = is_user_authorized(user_id)
    auth_status = "✅ Autorizado" if is_authorized else "❌ No autorizado"
    
    message = (
        f"👤 *Información de Usuario*\n\n"
        f"*Nombre:* {first_name}\n"
        f"*Username:* @{username}\n"
        f"*ID:* `{user_id}`\n"
        f"*Estado:* {auth_status}\n\n"
        f"Para autorizar este usuario, agrega este ID a `ALLOWED_USER_IDS` en tu archivo `.env`:\n"
        f"`ALLOWED_USER_IDS={user_id}`"
    )
    
    await update.message.reply_text(message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /help."""
    # Verificar autorización
    if not is_user_authorized(update.effective_user.id):
        await update.message.reply_text("❌ No estás autorizado para usar este bot.")
        return
    
    help_text = (
        "📚 *Ayuda - Bot Claude Code CLI*\n\n"
        "*Uso básico:*\n"
        "Simplemente escribe tu mensaje y se ejecutará en Claude Code CLI.\n\n"
        "*Ejemplos:*\n"
        "• `Lista los archivos en el directorio actual`\n"
        "• `Ejecuta el script test.py`\n"
        "• `Busca errores en el código`\n"
        "• `Usa el MCP de GitHub para listar repositorios`\n\n"
        "*Comandos:*\n"
        "/start - Mensaje de bienvenida\n"
        "/help - Esta ayuda\n"
        "/new - Inicia nueva conversación (limpia contexto)\n"
        "/status - Estado del bot y configuración\n\n"
        "*Notas:*\n"
        "• Las conversaciones se mantienen por usuario\n"
        "• Puedes usar todos los MCPs disponibles localmente\n"
        "• Los comandos se ejecutan en: `{WORKSPACE_PATH}`"
    ).format(WORKSPACE_PATH=WORKSPACE_PATH)
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def new_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia una nueva conversación."""
    # Verificar autorización
    if not is_user_authorized(update.effective_user.id):
        await update.message.reply_text("❌ No estás autorizado para usar este bot.")
        return
    
    user_id = update.effective_user.id
    if user_id in user_sessions:
        del user_sessions[user_id]
    
    await update.message.reply_text(
        "✨ Nueva conversación iniciada. El contexto anterior ha sido limpiado."
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el estado del bot."""
    # Verificar autorización
    if not is_user_authorized(update.effective_user.id):
        await update.message.reply_text("❌ No estás autorizado para usar este bot.")
        return
    
    executor = ClaudeCodeExecutor()
    
    # Verificar si Claude CLI está disponible
    try:
        result = subprocess.run(
            [executor.claude_path, '--version'],
            capture_output=True,
            timeout=5,
            cwd=WORKSPACE_PATH
        )
        claude_status = "✅ Disponible"
        if result.stdout:
            claude_status += f" ({result.stdout.decode().strip()})"
    except Exception:
        claude_status = "❌ No disponible"
    
    # Verificar estado de transcripción de voz
    whisper_status = "❌ No disponible"
    if OPENAI_AVAILABLE:
        if OPENAI_API_KEY:
            whisper_status = f"✅ Configurado (key: {OPENAI_API_KEY[:10]}...{OPENAI_API_KEY[-4:]})"
        else:
            whisper_status = "⚠️ OpenAI instalado pero falta API key"
    else:
        whisper_status = "❌ OpenAI no instalado"
    
    status_text = (
        "📊 *Estado del Bot*\n\n"
        f"*Claude CLI:* {claude_status}\n"
        f"*Ruta CLI:* `{CLAUDE_CLI_PATH}`\n"
        f"*Workspace:* `{WORKSPACE_PATH}`\n"
        f"*Usuario:* {update.effective_user.first_name}\n"
        f"*Sesión activa:* {'Sí' if update.effective_user.id in user_sessions else 'No'}\n"
        f"*Transcripción de voz:* {whisper_status}\n"
    )
    
    await update.message.reply_text(status_text, parse_mode='Markdown')


async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja mensajes de voz del usuario."""
    user_id = update.effective_user.id
    username = update.effective_user.username or "sin username"
    
    # Verificar autorización
    if not is_user_authorized(user_id):
        logger.warning(f"[SEGURIDAD] Usuario no autorizado intentó enviar voz: {user_id} (@{username})")
        await update.message.reply_text(
            "❌ *Acceso denegado*\n\n"
            "No estás autorizado para usar este bot.\n"
            "Contacta al administrador para obtener acceso.",
            parse_mode='Markdown'
        )
        return
    
    # SEGURIDAD: Verificar rate limiting
    is_allowed, time_until_reset = check_rate_limit(user_id)
    if not is_allowed:
        logger.warning(f"[SEGURIDAD] Usuario {user_id} (@{username}) excedió rate limit. Esperar {time_until_reset:.1f}s")
        await update.message.reply_text(
            f"⏱️ *Rate limit excedido*\n\n"
            f"Has enviado demasiadas solicitudes en poco tiempo.\n"
            f"Por favor espera {int(time_until_reset)} segundos antes de intentar de nuevo.\n\n"
            f"Límite: {RATE_LIMIT_REQUESTS} requests por {int(RATE_LIMIT_WINDOW)} segundos.",
            parse_mode='Markdown'
        )
        return
    
    # Verificar disponibilidad de OpenAI
    if not OPENAI_AVAILABLE:
        logger.error(f"[Usuario {user_id}] OpenAI no está instalado")
        await update.message.reply_text(
            "❌ *Transcripción no disponible*\n\n"
            "OpenAI no está instalado.\n"
            "Instala con: `pip install openai`",
            parse_mode='Markdown'
        )
        return
    
    # Verificar API key
    if not OPENAI_API_KEY or not OPENAI_API_KEY.strip():
        logger.error(f"[Usuario {user_id}] OPENAI_API_KEY no configurada")
        await update.message.reply_text(
            "❌ *Transcripción no disponible*\n\n"
            "OPENAI_API_KEY no está configurada en el archivo .env.\n"
            "Agrega tu API key y reinicia el bot.",
            parse_mode='Markdown'
        )
        return
    
    logger.info(f"[Usuario {user_id}] API key encontrada: {OPENAI_API_KEY[:10]}...{OPENAI_API_KEY[-4:]}")
    
    voice = update.message.voice
    
    # Mostrar que está procesando
    processing_msg = await update.message.reply_text("🎤 Transcribiendo audio...")
    
    try:
        # Descargar archivo de voz
        voice_file_path = await download_voice_file(voice, context)
        if not voice_file_path:
            await processing_msg.edit_text("❌ Error descargando el archivo de voz.")
            return
        
        # Transcribir audio
        await processing_msg.edit_text("🔄 Procesando transcripción...")
        transcribed_text = await transcribe_voice_message(voice_file_path)
        
        # Limpiar archivo temporal
        try:
            os.remove(voice_file_path)
        except Exception as e:
            logger.warning(f"No se pudo eliminar archivo temporal: {e}")
        
        if not transcribed_text:
            await processing_msg.edit_text("❌ Error transcribiendo el audio. Intenta de nuevo.")
            return
        
        # Mostrar transcripción
        await processing_msg.edit_text(f"📝 *Transcripción:*\n\n{transcribed_text}")
        
        # Procesar el texto transcrito como si fuera un mensaje de texto normal
        logger.info(f"[Usuario {user_id} (@{username})] Voz transcrita: {transcribed_text[:100]}...")
        
        # Procesar el texto transcrito directamente
        await process_query(update, context, transcribed_text, user_id, username)
        
    except Exception as e:
        logger.error(f"[Usuario {user_id}] Error procesando voz: {e}", exc_info=True)
        await processing_msg.edit_text(f"❌ Error procesando voz: {str(e)}")


async def process_query(
    update: Update, 
    context: ContextTypes.DEFAULT_TYPE, 
    query: str, 
    user_id: int, 
    username: str
):
    """
    Procesa una query (texto) y la ejecuta en Claude Code CLI.
    
    Args:
        update: Update de Telegram
        context: Contexto del bot
        query: Texto a procesar
        user_id: ID del usuario
        username: Username del usuario
    """
    if not query or not query.strip():
        await update.message.reply_text("Por favor envía un mensaje válido.")
        return
    
    # SEGURIDAD: Validar longitud máxima de input para prevenir DoS
    if len(query) > MAX_INPUT_LENGTH:
        logger.warning(f"[SEGURIDAD] Usuario {user_id} (@{username}) envió mensaje demasiado largo: {len(query)} caracteres (máximo: {MAX_INPUT_LENGTH})")
        await update.message.reply_text(
            f"❌ *Mensaje demasiado largo*\n\n"
            f"El mensaje excede el límite máximo permitido de {MAX_INPUT_LENGTH:,} caracteres.\n"
            f"Tu mensaje tiene {len(query):,} caracteres.\n\n"
            f"Por favor divide tu mensaje en partes más pequeñas.",
            parse_mode='Markdown'
        )
        return
    
    logger.info(f"[Usuario {user_id} (@{username})] Procesando query: {query[:100]}...")
    
    # Mostrar que está procesando
    processing_msg = await update.message.reply_text("⏳ Procesando...")
    current_message = processing_msg
    
    # Acumular toda la salida
    all_output = []
    has_received_output = False
    
    async def handle_output_chunk(text: str):
        """Maneja cada fragmento de salida."""
        nonlocal all_output, has_received_output, current_message
        
        if text.strip():
            has_received_output = True
            all_output.append(text)
            logger.debug(f"[Usuario {user_id}] Salida recibida: {text[:100]}...")
    
    async def handle_error_chunk(text: str):
        """Maneja fragmentos de error."""
        nonlocal all_output, has_received_output
        if text.strip():
            has_received_output = True
            logger.warning(f"[Usuario {user_id}] Error recibido: {text[:200]}")
            all_output.append(f"⚠️ Error: {text}\n")
    
    # Ejecutar comando con streaming
    executor = ClaudeCodeExecutor()
    continue_session = user_id in user_sessions
    
    try:
        result = await executor.execute_streaming(
            query,
            user_id,
            continue_session,
            handle_output_chunk,
            handle_error_chunk
        )
        
        # Procesar y enviar toda la salida acumulada
        if all_output:
            combined = ''.join(all_output)
            cleaned = remove_ansi_codes(combined)
            
            if cleaned.strip():
                parts = split_message(cleaned)
                if parts:
                    try:
                        await current_message.edit_text(
                            parts[0],
                            parse_mode='Markdown'
                        )
                        for part in parts[1:]:
                            await update.message.reply_text(part, parse_mode='Markdown')
                    except Exception as e:
                        logger.error(f"[Usuario {user_id}] Error enviando mensaje: {e}")
                        # Si falla edit, crear nuevo mensaje
                        try:
                            await update.message.reply_text(parts[0], parse_mode='Markdown')
                            for part in parts[1:]:
                                await update.message.reply_text(part, parse_mode='Markdown')
                        except Exception as e2:
                            logger.error(f"[Usuario {user_id}] Error crítico enviando mensaje: {e2}")
        
        # Mostrar resultado final solo si no hubo salida
        if not result['success']:
            # Manejar timeout específicamente
            if result.get('timeout'):
                timeout_msg = (
                    f"⏱️ *Timeout alcanzado*\n\n"
                    f"El comando excedió el tiempo máximo permitido ({COMMAND_TIMEOUT}s) "
                    f"y fue terminado por seguridad.\n\n"
                    f"Esto previene que comandos maliciosos bloqueen el bot indefinidamente."
                )
                if not has_received_output:
                    try:
                        await current_message.edit_text(timeout_msg, parse_mode='Markdown')
                    except Exception:
                        await update.message.reply_text(timeout_msg, parse_mode='Markdown')
            else:
                error_msg = f"❌ *Error ejecutando comando (código: {result['returncode']})*"
                if not has_received_output:
                    try:
                        await current_message.edit_text(error_msg, parse_mode='Markdown')
                    except Exception:
                        await update.message.reply_text(error_msg, parse_mode='Markdown')
        elif not has_received_output:
            # Solo mostrar éxito si no hubo ninguna salida
            try:
                await current_message.edit_text("✅ Comando ejecutado exitosamente.", parse_mode='Markdown')
            except Exception as e:
                logger.debug(f"[Usuario {user_id}] No se pudo editar mensaje de éxito: {e}")
        
        # Marcar que el usuario tiene una sesión activa
        if result['success']:
            user_sessions[user_id] = True
            logger.info(f"[Usuario {user_id}] Sesión marcada como activa")
        
    except Exception as e:
        logger.error(f"[Usuario {user_id}] Error en process_query: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error interno: {str(e)}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja mensajes de texto del usuario con lectura en tiempo real."""
    user_id = update.effective_user.id
    username = update.effective_user.username or "sin username"
    
    # Verificar autorización
    if not is_user_authorized(user_id):
        logger.warning(f"[SEGURIDAD] Usuario no autorizado intentó enviar mensaje: {user_id} (@{username})")
        await update.message.reply_text(
            "❌ *Acceso denegado*\n\n"
            "No estás autorizado para usar este bot.\n"
            "Contacta al administrador para obtener acceso.",
            parse_mode='Markdown'
        )
        return
    
    # SEGURIDAD: Verificar rate limiting
    is_allowed, time_until_reset = check_rate_limit(user_id)
    if not is_allowed:
        logger.warning(f"[SEGURIDAD] Usuario {user_id} (@{username}) excedió rate limit. Esperar {time_until_reset:.1f}s")
        await update.message.reply_text(
            f"⏱️ *Rate limit excedido*\n\n"
            f"Has enviado demasiadas solicitudes en poco tiempo.\n"
            f"Por favor espera {int(time_until_reset)} segundos antes de intentar de nuevo.\n\n"
            f"Límite: {RATE_LIMIT_REQUESTS} requests por {int(RATE_LIMIT_WINDOW)} segundos.",
            parse_mode='Markdown'
        )
        return
    
    query = update.message.text
    
    if not query or not query.strip():
        await update.message.reply_text("Por favor envía un mensaje válido.")
        return
    
    # Procesar el mensaje usando la función compartida
    await process_query(update, context, query, user_id, username)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """
    Global error handler to catch errors that occur during polling.
    Specifically handles Conflict errors when multiple bot instances are running.
    """
    error = context.error
    
    if isinstance(error, Conflict):
        logger.error(
            f"❌ CONFLICT: Another bot instance is running.\n"
            f"Error: {error}\n\n"
            f"SOLUTION:\n"
            f"1. Check if there's another bot instance running in another terminal\n"
            f"2. Find processes with: ps aux | grep telegram_claude_bot\n"
            f"3. Kill duplicate processes with: kill <PID>\n"
            f"4. Or use the helper script: ./kill_bot_processes.sh\n"
        )
        # Stop the application to allow restart
        if context.application:
            await context.application.stop()
            await context.application.shutdown()
        raise error  # Re-raise to trigger retry logic in main()
    else:
        logger.error(f"Exception while handling an update: {error}", exc_info=error)


def main():
    """Función principal."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN no está configurado. Por favor configúralo en .env")
        return
    
    # SEGURIDAD: Validar que ALLOWED_USER_IDS esté configurado
    if not ALLOWED_USER_IDS:
        logger.error(
            "❌ SEGURIDAD CRÍTICA: ALLOWED_USER_IDS no está configurado.\n"
            "El bot NO se iniciará porque esto permitiría acceso público a tu sistema.\n"
            "Por favor configura ALLOWED_USER_IDS en tu archivo .env con al menos un ID de usuario.\n"
            "Para obtener tu ID, puedes iniciar el bot temporalmente o usar @userinfobot en Telegram."
        )
        print("\n" + "="*70)
        print("❌ ERROR DE SEGURIDAD CRÍTICA")
        print("="*70)
        print("ALLOWED_USER_IDS no está configurado.")
        print("Esto permitiría que CUALQUIER usuario use el bot y ejecute comandos en tu sistema.")
        print("\nPara solucionarlo:")
        print("1. Agrega tu ID de usuario a ALLOWED_USER_IDS en el archivo .env")
        print("2. Formato: ALLOWED_USER_IDS=123456789")
        print("3. Para múltiples usuarios: ALLOWED_USER_IDS=123456789,987654321")
        print("="*70 + "\n")
        return
    
    logger.info(f"✅ Seguridad: {len(ALLOWED_USER_IDS)} usuario(s) autorizado(s)")
    
    # Crear aplicación
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Registrar handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("new", new_conversation))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("myid", myid_command))
    
    # Handler para mensajes de voz (debe ir antes del handler de texto)
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    
    # Handler para mensajes de texto
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add global error handler to catch Conflict and other errors
    application.add_error_handler(error_handler)
    
    # Iniciar bot con manejo de errores de red
    logger.info("Bot iniciado. Presiona Ctrl+C para detener.")
    
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,  # Ignore pending updates on startup
                close_loop=False  # Don't close loop on stop
            )
            break  # If we reach here, bot stopped normally
        except Conflict as e:
            retry_count += 1
            logger.error(
                f"❌ CONFLICT: Another bot instance is running.\n"
                f"Error: {e}\n\n"
                f"SOLUTION:\n"
                f"1. Check if there's another bot instance running in another terminal\n"
                f"2. Find processes with: ps aux | grep telegram_claude_bot\n"
                f"3. Kill duplicate processes with: kill <PID>\n"
                f"4. Or use the helper script: ./kill_bot_processes.sh\n"
            )
            if retry_count < max_retries:
                wait_time = 5 * retry_count
                logger.info(f"Waiting {wait_time} seconds before retrying ({retry_count}/{max_retries})...")
                import time
                time.sleep(wait_time)
            else:
                logger.error("❌ Maximum retries reached. Bot cannot start due to conflict.")
                logger.error("Please ensure only one bot instance is running.")
                return
        except KeyboardInterrupt:
            logger.info("Bot stopped by user.")
            break
        except Exception as e:
            logger.error(f"Error in bot: {e}", exc_info=True)
            retry_count += 1
            if retry_count < max_retries:
                wait_time = 5
                logger.info(f"Retrying connection in {wait_time} seconds... ({retry_count}/{max_retries})")
                import time
                time.sleep(wait_time)
            else:
                logger.error(f"Critical error after {max_retries} attempts: {e}. Bot cannot connect.")
                return


if __name__ == '__main__':
    main()
