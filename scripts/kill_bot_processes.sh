#!/bin/bash
# Script para matar procesos de los bots (Telegram y Slack)

echo "Buscando procesos del bot..."

# Matar procesos de bot.py (Python o python, mayúscula o minúscula)
pkill -if "python.*bot\.py" 2>/dev/null
pkill -if "channels/(telegram|slack)/bot\.py" 2>/dev/null

# También matar procesos de Claude CLI que puedan estar colgados
pkill -f "claude.*-p" 2>/dev/null

# Esperar un momento para que los procesos terminen
sleep 1

# Eliminar lock files
TELEGRAM_LOCK="/tmp/telegram_claude_bot.lock"
SLACK_LOCK="/tmp/slack_claude_bot.lock"

if [ -f "$TELEGRAM_LOCK" ]; then
    rm -f "$TELEGRAM_LOCK"
    echo "🗑️  Lock file de Telegram eliminado"
fi

if [ -f "$SLACK_LOCK" ]; then
    rm -f "$SLACK_LOCK"
    echo "🗑️  Lock file de Slack eliminado"
fi

# Verificar si quedaron procesos
REMAINING=$(ps aux | grep -E "[Pp]ython.*bot\.py" | grep -v grep | wc -l)

if [ "$REMAINING" -gt 0 ]; then
    echo "⚠️  Aún hay $REMAINING proceso(s) corriendo. Forzando kill..."
    ps aux | grep -E "[Pp]ython.*bot\.py" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null
    sleep 1
fi

# Verificación final
FINAL=$(ps aux | grep -E "[Pp]ython.*bot\.py" | grep -v grep | wc -l)

if [ "$FINAL" -eq 0 ]; then
    echo "✅ Todos los procesos del bot fueron terminados"
else
    echo "❌ No se pudieron matar todos los procesos. Intenta manualmente:"
    ps aux | grep -E "[Pp]ython.*bot\.py" | grep -v grep
fi
