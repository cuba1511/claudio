#!/usr/bin/env python3
"""
Bot de Telegram que conecta con Claude Code CLI local.
Permite ejecutar comandos y MCPs desde Telegram como si fuera la terminal local.
"""

import os
import subprocess
import logging
import asyncio
from pathlib import Path
from typing import Optional
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

# Herramientas permitidas automáticamente (para MCPs y herramientas sin prompts)
# Por defecto permite todas las herramientas. Puedes restringir con: "Read,Edit,Bash"
ALLOWED_TOOLS = os.getenv('ALLOWED_TOOLS', '*')  # '*' permite todas las herramientas

# Usar --dangerously-skip-permissions para bypass todos los checks de permisos
# Esto es necesario porque los wildcards no funcionan con MCPs y -p no puede mostrar prompts
SKIP_PERMISSIONS = os.getenv('SKIP_PERMISSIONS', 'true').lower() == 'true'

# Almacenar conversaciones por usuario
user_sessions = {}


class ClaudeCodeExecutor:
    """Ejecutor de comandos Claude Code CLI."""
    
    def __init__(self, workspace_path: str = None):
        self.workspace_path = workspace_path or WORKSPACE_PATH
        self.claude_path = CLAUDE_CLI_PATH
        
    async def execute(self, query: str, user_id: int, continue_session: bool = False) -> dict:
        """
        Ejecuta un comando en Claude Code CLI.
        
        Args:
            query: El mensaje/comando a ejecutar
            user_id: ID del usuario para mantener sesiones separadas
            continue_session: Si True, continúa la conversación anterior usando -c
            
        Returns:
            dict con 'output', 'error', 'success'
        """
        try:
            # Construir comando
            cmd = [self.claude_path]
            
            # Si hay una sesión previa y queremos continuarla, usar -c (continue)
            # que automáticamente continúa la conversación más reciente sin necesidad de session ID
            if continue_session and user_id in user_sessions:
                cmd.append('-c')
            
            # Agregar flags para aprobar automáticamente herramientas/MCPs
            # Los wildcards no funcionan con MCPs, así que usamos --dangerously-skip-permissions
            # Esto es necesario porque -p (modo no interactivo) no puede mostrar prompts
            if SKIP_PERMISSIONS:
                cmd.append('--dangerously-skip-permissions')
            elif ALLOWED_TOOLS and ALLOWED_TOOLS != '*':
                # Solo usar --allowedTools si no estamos usando skip-permissions y no es wildcard
                cmd.extend(['--allowedTools', ALLOWED_TOOLS])
            
            # Agregar -p para modo no interactivo y la query
            cmd.extend(['-p', query])
            
            # Configurar entorno
            env = os.environ.copy()
            env['PWD'] = self.workspace_path
            
            logger.info(f"Ejecutando: {' '.join(cmd)}")
            
            # Ejecutar comando
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.workspace_path,
                env=env
            )
            
            stdout, stderr = await process.communicate()
            
            # Decodificar output
            output = stdout.decode('utf-8', errors='replace') if stdout else ''
            error = stderr.decode('utf-8', errors='replace') if stderr else ''
            
            return {
                'success': process.returncode == 0,
                'output': output,
                'error': error,
                'returncode': process.returncode
            }
            
        except FileNotFoundError:
            return {
                'success': False,
                'output': '',
                'error': f'Claude CLI no encontrado en: {self.claude_path}. Asegúrate de que está instalado y en PATH.',
                'returncode': -1
            }
        except Exception as e:
            logger.error(f"Error ejecutando comando: {e}", exc_info=True)
            return {
                'success': False,
                'output': '',
                'error': f'Error ejecutando comando: {str(e)}',
                'returncode': -1
            }


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
    welcome_message = (
        "🤖 *Bot Claude Code CLI*\n\n"
        "Envía mensajes aquí y se ejecutarán en tu instancia local de Claude Code CLI.\n\n"
        "Comandos disponibles:\n"
        "/start - Muestra este mensaje\n"
        "/help - Muestra ayuda detallada\n"
        "/new - Inicia una nueva conversación\n"
        "/status - Muestra el estado del bot\n\n"
        "Simplemente escribe tu mensaje y se ejecutará en Claude Code."
    )
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /help."""
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
    user_id = update.effective_user.id
    if user_id in user_sessions:
        del user_sessions[user_id]
    
    await update.message.reply_text(
        "✨ Nueva conversación iniciada. El contexto anterior ha sido limpiado."
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el estado del bot."""
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
    except:
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
    """Maneja mensajes de texto del usuario."""
    user_id = update.effective_user.id
    query = update.message.text
    
    if not query or not query.strip():
        await update.message.reply_text("Por favor envía un mensaje válido.")
        return
    
    # Mostrar que está procesando
    processing_msg = await update.message.reply_text("⏳ Procesando...")
    
    # Ejecutar comando
    executor = ClaudeCodeExecutor()
    continue_session = user_id in user_sessions
    result = await executor.execute(query, user_id, continue_session=continue_session)
    
    # Preparar respuesta
    if result['success']:
        response = result['output'] or "✅ Comando ejecutado exitosamente (sin output)."
        
        # Si hay errores pero también output, incluirlos
        if result['error']:
            response = f"{response}\n\n⚠️ *Warnings:*\n```\n{result['error']}\n```"
    else:
        response = f"❌ *Error ejecutando comando:*\n```\n{result['error']}\n```"
        if result['output']:
            response += f"\n\n*Output parcial:*\n```\n{result['output']}\n```"
    
    # Dividir mensaje si es muy largo
    message_parts = split_message(response)
    
    # Enviar primera parte editando el mensaje de procesamiento
    if message_parts:
        await processing_msg.edit_text(
            message_parts[0],
            parse_mode='Markdown'
        )
        
        # Enviar partes adicionales si existen
        for part in message_parts[1:]:
            await update.message.reply_text(part, parse_mode='Markdown')
    
    # Marcar que el usuario tiene una sesión activa (para usar -c en próximos mensajes)
    if result['success']:
        user_sessions[user_id] = True


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
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Iniciar bot
    logger.info("Bot iniciado. Presiona Ctrl+C para detener.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
