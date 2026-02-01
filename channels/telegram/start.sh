#!/bin/bash
# Script para iniciar el bot de Telegram de Claudio
# El bot se ejecuta en el directorio claudio/ para que Claude Code lea CLAUDE.md

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🤖 Iniciando Claudio Bot..."
echo "📁 Workspace: $PROJECT_ROOT"

# Cambiar al directorio del proyecto
cd "$PROJECT_ROOT"

# Verificar que existe .env
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "❌ Error: No existe .env en $SCRIPT_DIR"
    echo "   Copia .env.example a .env y configura las variables"
    exit 1
fi

# Cargar variables de entorno
export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)

# Sobrescribir WORKSPACE_PATH para que apunte al proyecto
export WORKSPACE_PATH="$PROJECT_ROOT"

# Ejecutar el bot
python "$SCRIPT_DIR/bot.py"
