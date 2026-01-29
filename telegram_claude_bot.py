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
from typing import Optional, Callable
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Variables de configuración
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CLAUDE_CLI_PATH = os.getenv('CLAUDE_CLI_PATH', 'claude')  # Ruta al ejecutable de Claude CLI
WORKSPACE_PATH = os.getenv('WORKSPACE_PATH', os.getcwd())  # Directorio de trabajo
MAX_MESSAGE_LENGTH = 4096  # Límite de Telegram
BUFFER_TIMEOUT = float(os.getenv('BUFFER_TIMEOUT', '1.5'))  # Segundos para acumular salida antes de enviar

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
            
            # Leer ambos streams en paralelo
            await asyncio.gather(
                read_stream(process.stdout, is_error=False),
                read_stream(process.stderr, is_error=True)
            )
            
            # Esperar a que el proceso termine
            returncode = await process.wait()
            
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
    
    status_text = (
        "📊 *Estado del Bot*\n\n"
        f"*Claude CLI:* {claude_status}\n"
        f"*Ruta CLI:* `{CLAUDE_CLI_PATH}`\n"
        f"*Workspace:* `{WORKSPACE_PATH}`\n"
        f"*Usuario:* {update.effective_user.first_name}\n"
        f"*Sesión activa:* {'Sí' if update.effective_user.id in user_sessions else 'No'}\n"
    )
    
    await update.message.reply_text(status_text, parse_mode='Markdown')


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
    
    query = update.message.text
    
    if not query or not query.strip():
        await update.message.reply_text("Por favor envía un mensaje válido.")
        return
    
    logger.info(f"[Usuario {user_id} (@{username})] Nuevo mensaje recibido: {query[:100]}...")
    
    # Mostrar que está procesando
    processing_msg = await update.message.reply_text("⏳ Procesando...")
    current_message = processing_msg
    
    # Buffer inteligente para acumular salida
    accumulated_output = []
    buffer_lock = asyncio.Lock()
    buffer_task = None
    
    async def handle_output_chunk(text: str):
        """Maneja cada fragmento de salida con buffer inteligente."""
        nonlocal accumulated_output, buffer_task, current_message
        
        async with buffer_lock:
            accumulated_output.append(text)
            
            # Cancelar task anterior si existe
            if buffer_task and not buffer_task.done():
                buffer_task.cancel()
            
            # Programar envío después del timeout
            async def send_buffered():
                await asyncio.sleep(BUFFER_TIMEOUT)
                nonlocal current_message, accumulated_output
                async with buffer_lock:
                    local_accumulated = accumulated_output.copy() if accumulated_output else []
                    accumulated_output = []
                    
                    if local_accumulated:
                        combined = ''.join(local_accumulated)
                        
                        if combined.strip():
                            cleaned = remove_ansi_codes(combined)
                            if cleaned.strip():
                                # Dividir si es muy largo
                                parts = split_message(cleaned)
                                if parts:
                                    try:
                                        await current_message.edit_text(
                                            parts[0],
                                            parse_mode='Markdown'
                                        )
                                        # Enviar partes adicionales
                                        for part in parts[1:]:
                                            current_message = await update.message.reply_text(
                                                part,
                                                parse_mode='Markdown'
                                            )
                                    except Exception as e:
                                        logger.error(f"[Usuario {user_id}] Error enviando mensaje: {e}")
                                        # Si falla, crear nuevo mensaje
                                        try:
                                            current_message = await update.message.reply_text(
                                                parts[0],
                                                parse_mode='Markdown'
                                            )
                                            for part in parts[1:]:
                                                current_message = await update.message.reply_text(
                                                    part,
                                                    parse_mode='Markdown'
                                                )
                                        except Exception as e2:
                                            logger.error(f"[Usuario {user_id}] Error crítico enviando mensaje: {e2}")
            
            buffer_task = asyncio.create_task(send_buffered())
    
    async def handle_error_chunk(text: str):
        """Maneja fragmentos de error."""
        logger.warning(f"[Usuario {user_id}] Error recibido: {text[:200]}")
        # Los errores se mostrarán al final
    
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
        
        # Cancelar buffer task y enviar cualquier salida restante
        async with buffer_lock:
            if buffer_task and not buffer_task.done():
                buffer_task.cancel()
                try:
                    await buffer_task
                except (asyncio.CancelledError, Exception):
                    pass
            
            if accumulated_output:
                combined = ''.join(accumulated_output)
                accumulated_output = []
                
                if combined.strip():
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
                                logger.error(f"[Usuario {user_id}] Error enviando salida final: {e}")
        
        # Mostrar resultado final
        if not result['success']:
            error_msg = f"❌ *Error ejecutando comando (código: {result['returncode']})*"
            try:
                await current_message.edit_text(error_msg, parse_mode='Markdown')
            except Exception:
                await update.message.reply_text(error_msg, parse_mode='Markdown')
        else:
            # Verificar si hubo salida antes de mostrar mensaje de éxito
            async with buffer_lock:
                has_output = bool(accumulated_output)
            if not has_output:
                try:
                    await current_message.edit_text("✅ Comando ejecutado exitosamente.", parse_mode='Markdown')
                except Exception as e:
                    logger.debug(f"[Usuario {user_id}] No se pudo editar mensaje de éxito: {e}")
                    pass
        
        # Marcar que el usuario tiene una sesión activa
        if result['success']:
            user_sessions[user_id] = True
            logger.info(f"[Usuario {user_id}] Sesión marcada como activa")
        
    except Exception as e:
        logger.error(f"[Usuario {user_id}] Error en handle_message: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error interno: {str(e)}")


def main():
    """Función principal."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN no está configurado. Por favor configúralo en .env")
        return
    
    # Crear aplicación
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Registrar handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("new", new_conversation))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("myid", myid_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Iniciar bot
    logger.info("Bot iniciado. Presiona Ctrl+C para detener.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
