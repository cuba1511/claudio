# Claudio Web Dashboard

Interfaz web para monitorear y configurar Claudio.

## Características

- 🔌 **Vista de MCPs** - Lista todos los MCPs configurados
- 🏥 **Health Checks** - Verifica el estado de cada MCP
- 💬 **Chat con Claudio** - Habla con Claudio directo desde el browser via WebSocket
- 📚 **Documentación** - Acceso rápido a guías de integraciones
- ⚡ **Workflows** - Lista de workflows disponibles
- 🧠 **Contexto** - Visualiza el CLAUDE.md

## Inicio Rápido

```bash
# Desde el directorio raíz de claudio
cd channels/web
./start.sh

# O en modo desarrollo (con hot reload)
./start.sh --dev
```

Abre http://localhost:8000 en tu navegador.

## API Endpoints

| Endpoint | Descripción |
|----------|-------------|
| `GET /` | Dashboard principal (HTML) |
| `GET /api/mcps` | Lista todos los MCPs |
| `GET /api/mcps/health` | Health check de todos los MCPs |
| `GET /api/mcps/{name}/health` | Health check de un MCP específico |
| `GET /api/docs/{type}` | Lista documentación (integrations/workflows) |
| `GET /api/docs/read?path=...` | Lee un archivo de documentación |
| `GET /api/context` | Obtiene el CLAUDE.md |
| `WS /ws/chat` | WebSocket para chat con Claudio |

## Estados de Health Check

| Estado | Significado |
|--------|-------------|
| 🟢 `ready` | MCP listo para usar |
| 🔵 `configured` | MCP configurado (no verificado en runtime) |
| 🟡 `warning` | MCP puede tener problemas |
| 🔴 `error` | MCP con errores |
| ⚫ `unknown` | Estado no determinado |

## Dependencias

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
jinja2==3.1.3
python-multipart==0.0.6
python-dotenv==1.0.1
pyyaml==6.0.1
httpx==0.26.0
websockets==12.0
```

## Estructura

```
channels/web/
├── app.py           # FastAPI application
├── templates/
│   └── dashboard.html  # Template del dashboard
├── requirements.txt
├── start.sh
└── README.md
```
