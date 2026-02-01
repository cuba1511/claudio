#!/bin/bash
# Script para matar procesos del bot de Telegram

echo "Buscando procesos del bot..."
pkill -f "python.*bot.py" 2>/dev/null

# Eliminar lock file si existe
LOCK_FILE="/tmp/telegram_claude_bot.lock"
if [ -f "$LOCK_FILE" ]; then
    rm -f "$LOCK_FILE"
    echo "Lock file eliminado"
fi

echo "✅ Bot processes killed"
