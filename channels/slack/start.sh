#!/bin/bash
# Script para iniciar el bot de Slack de Claudio

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDIO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo -e "${GREEN}🤖 Iniciando Bot de Slack de Claudio${NC}"
echo "================================================"

# Verificar que existe el archivo .env
if [ ! -f "$SCRIPT_DIR/.env" ] && [ ! -f "$CLAUDIO_ROOT/.env" ]; then
    echo -e "${RED}❌ Error: No se encontró archivo .env${NC}"
    echo ""
    echo "Copia el archivo de ejemplo y configúralo:"
    echo "  cp $SCRIPT_DIR/.env.example $SCRIPT_DIR/.env"
    echo ""
    echo "O usa el .env global en la raíz de claudio:"
    echo "  cp $CLAUDIO_ROOT/.env.example $CLAUDIO_ROOT/.env"
    exit 1
fi

# Cargar .env local primero, si no existe usar el global
if [ -f "$SCRIPT_DIR/.env" ]; then
    export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)
    echo -e "${GREEN}✅ Usando .env local${NC}"
elif [ -f "$CLAUDIO_ROOT/.env" ]; then
    export $(grep -v '^#' "$CLAUDIO_ROOT/.env" | xargs)
    echo -e "${GREEN}✅ Usando .env global${NC}"
fi

# Verificar tokens requeridos
if [ -z "$SLACK_BOT_TOKEN" ]; then
    echo -e "${RED}❌ Error: SLACK_BOT_TOKEN no está configurado${NC}"
    exit 1
fi

if [ -z "$SLACK_APP_TOKEN" ]; then
    echo -e "${RED}❌ Error: SLACK_APP_TOKEN no está configurado${NC}"
    echo ""
    echo "Necesitas habilitar Socket Mode en tu Slack App:"
    echo "1. Ve a https://api.slack.com/apps"
    echo "2. Selecciona tu app"
    echo "3. Settings > Socket Mode > Enable"
    echo "4. Basic Information > App-Level Tokens > Generate"
    exit 1
fi

# Verificar Claude CLI
if ! command -v claude &> /dev/null; then
    echo -e "${YELLOW}⚠️ Advertencia: Claude CLI no encontrado en PATH${NC}"
    echo "Asegúrate de que Claude CLI está instalado y en el PATH"
fi

# Activar entorno virtual si existe
if [ -d "$CLAUDIO_ROOT/venv" ]; then
    echo -e "${GREEN}✅ Activando entorno virtual${NC}"
    source "$CLAUDIO_ROOT/venv/bin/activate"
fi

# Instalar dependencias si es necesario
if ! python3 -c "import slack_bolt" 2>/dev/null; then
    echo -e "${YELLOW}📦 Instalando dependencias...${NC}"
    pip install -r "$SCRIPT_DIR/requirements.txt"
fi

# Configurar WORKSPACE_PATH si no está definido
export WORKSPACE_PATH="${WORKSPACE_PATH:-$CLAUDIO_ROOT}"

echo ""
echo "Configuración:"
echo "  Workspace: $WORKSPACE_PATH"
echo "  Bot Token: ${SLACK_BOT_TOKEN:0:15}..."
echo ""

# Iniciar el bot
cd "$CLAUDIO_ROOT"
python3 "$SCRIPT_DIR/bot.py"
