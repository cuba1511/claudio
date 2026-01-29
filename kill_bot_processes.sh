#!/bin/bash
# Script para encontrar y matar procesos duplicados del bot de Telegram

echo "🔍 Buscando procesos del bot de Telegram..."

# Buscar procesos de Python que ejecutan el bot
PROCESSES=$(ps aux | grep -i "telegram_claude_bot\|python.*telegram" | grep -v grep | grep -v "kill_bot_processes")

if [ -z "$PROCESSES" ]; then
    echo "✅ No se encontraron procesos del bot ejecutándose."
    exit 0
fi

echo "📋 Procesos encontrados:"
echo "$PROCESSES"
echo ""

# Extraer PIDs
PIDS=$(echo "$PROCESSES" | awk '{print $2}')

echo "⚠️  Procesos encontrados (PIDs): $PIDS"
echo ""
read -p "¿Deseas matar estos procesos? (s/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Ss]$ ]]; then
    for PID in $PIDS; do
        echo "🛑 Matando proceso $PID..."
        kill -9 $PID 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "✅ Proceso $PID terminado."
        else
            echo "❌ No se pudo terminar el proceso $PID (puede que ya no exista)."
        fi
    done
    echo ""
    echo "✅ Proceso completado. Ahora puedes iniciar el bot nuevamente."
else
    echo "❌ Operación cancelada."
fi
