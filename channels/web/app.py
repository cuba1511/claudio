"""
Claudio Web Dashboard
=====================
Interfaz web para monitorear MCPs, chatear con Claudio y configurar contexto.
"""

import json
import os
import re
import subprocess
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable

from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / ".env")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).resolve().parent
CLAUDIO_ROOT = BASE_DIR.parent.parent
MCP_CONFIG_PATH = CLAUDIO_ROOT / "mcp" / "cursor-config.json"
DOCS_PATH = CLAUDIO_ROOT / "docs"

# Chat config from env
CLAUDE_CLI_PATH = os.getenv('CLAUDE_CLI_PATH', 'claude')
WORKSPACE_PATH = os.getenv('WORKSPACE_PATH', str(CLAUDIO_ROOT))
COMMAND_TIMEOUT = float(os.getenv('COMMAND_TIMEOUT', '1800'))
SKIP_PERMISSIONS = os.getenv('SKIP_PERMISSIONS', 'true').lower() == 'true'

app = FastAPI(
    title="Claudio Dashboard",
    description="Panel de control para Claudio - Asistente de Productividad",
    version="1.0.0"
)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# ============== CHAT ENGINE ==============

def remove_ansi_codes(text: str) -> str:
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


chat_sessions: dict[str, bool] = {}


class ClaudeCodeExecutor:
    """Ejecutor de Claude Code CLI con streaming via WebSocket."""

    def __init__(self, workspace_path: str = None):
        self.workspace_path = workspace_path or WORKSPACE_PATH
        self.claude_path = CLAUDE_CLI_PATH

    async def execute_streaming(
        self,
        query: str,
        session_id: str,
        continue_session: bool,
        output_callback: Callable,
        error_callback: Optional[Callable] = None
    ) -> dict:
        try:
            cmd = [self.claude_path]

            if continue_session and session_id in chat_sessions:
                cmd.append('-c')

            if SKIP_PERMISSIONS:
                cmd.append('--dangerously-skip-permissions')

            cmd.extend(['-p', query])

            env = os.environ.copy()
            env['PWD'] = self.workspace_path

            logger.info(f"[Chat {session_id}] Ejecutando: {query[:80]}...")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.workspace_path,
                env=env
            )

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
                                if is_error and error_callback:
                                    await error_callback(cleaned)
                                elif not is_error:
                                    await output_callback(cleaned + '\n')
                        buffer = text.encode('utf-8', errors='replace')
                    except Exception as e:
                        logger.error(f"[Chat {session_id}] Stream decode error: {e}")

                if buffer:
                    try:
                        text = buffer.decode('utf-8', errors='replace')
                        cleaned = remove_ansi_codes(text)
                        if cleaned.strip():
                            if is_error and error_callback:
                                await error_callback(cleaned)
                            elif not is_error:
                                await output_callback(cleaned)
                    except Exception:
                        pass

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
                logger.warning(f"[Chat {session_id}] Timeout after {COMMAND_TIMEOUT}s")
                process.kill()
                await process.wait()
                if error_callback:
                    await error_callback(f"Timeout: el comando excedió {int(COMMAND_TIMEOUT)}s")
                return {'success': False, 'returncode': -2, 'timeout': True}

            if returncode == 0:
                chat_sessions[session_id] = True

            return {'success': returncode == 0, 'returncode': returncode}

        except FileNotFoundError:
            msg = f'Claude CLI no encontrado en: {self.claude_path}'
            logger.error(msg)
            if error_callback:
                await error_callback(msg)
            return {'success': False, 'returncode': -1}
        except Exception as e:
            msg = f'Error ejecutando comando: {str(e)}'
            logger.error(msg, exc_info=True)
            if error_callback:
                await error_callback(msg)
            return {'success': False, 'returncode': -1}


def load_mcp_config() -> dict:
    """Carga la configuración de MCPs desde cursor-config.json"""
    try:
        with open(MCP_CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e), "mcpServers": {}}


def get_mcp_type(config: dict) -> str:
    """Determina el tipo de MCP basado en su configuración"""
    if "url" in config:
        return "remote"
    elif "command" in config:
        cmd = config.get("command", "")
        # Check for npx first (can be full path)
        if "npx" in cmd:
            return "npx"
        elif "python" in cmd:
            return "python"
        elif "node" in cmd:
            return "node"
    return "unknown"


def get_mcp_icon(mcp_name: str) -> str:
    """Retorna un emoji/icono para cada MCP"""
    icons = {
        "github": "🐙",
        "slack": "💬",
        "clickup": "✅",
        "google-docs-mcp": "📄",
        "granola-mcp": "🎤",
    }
    return icons.get(mcp_name, "🔌")


async def check_mcp_health(name: str, config: dict) -> dict:
    """Verifica el estado de un MCP"""
    result = {
        "name": name,
        "status": "unknown",
        "message": "",
        "type": get_mcp_type(config),
        "icon": get_mcp_icon(name),
        "checked_at": datetime.now().isoformat()
    }
    
    try:
        if "url" in config:
            # MCP remoto (como GitHub)
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Solo verificamos que la URL sea alcanzable
                # No enviamos auth para no exponer tokens
                result["status"] = "configured"
                result["message"] = f"Remote MCP configured: {config['url']}"
                
        elif "command" in config:
            cmd = config["command"]
            args = config.get("args", [])
            
            # Verificar que el comando existe
            if "npx" in cmd:
                # Para npx (puede ser path completo), verificar que node está disponible
                check = subprocess.run(
                    ["which", "node"],
                    capture_output=True,
                    timeout=5
                )
                if check.returncode == 0:
                    # Find package name in args (usually after -y flag)
                    package_name = "unknown"
                    for i, arg in enumerate(args):
                        if arg == "-y" and i + 1 < len(args):
                            package_name = args[i + 1]
                            break
                        elif not arg.startswith("-") and "@" in arg:
                            package_name = arg
                            break
                    result["status"] = "ready"
                    result["message"] = f"npx package: {package_name}"
                else:
                    result["status"] = "error"
                    result["message"] = "Node.js not found"
                    
            elif cmd == "python" or "python" in cmd:
                # Para Python, verificar módulo
                module_name = None
                if "-m" in args:
                    idx = args.index("-m")
                    if idx + 1 < len(args):
                        module_name = args[idx + 1]
                
                if module_name:
                    check = subprocess.run(
                        ["python", "-c", f"import {module_name.split('.')[0]}"],
                        capture_output=True,
                        timeout=5
                    )
                    if check.returncode == 0:
                        result["status"] = "ready"
                        result["message"] = f"Python module: {module_name}"
                    else:
                        result["status"] = "warning"
                        result["message"] = f"Module {module_name} may not be installed"
                else:
                    result["status"] = "configured"
                    result["message"] = "Python MCP configured"
                    
            elif cmd == "node" or "node" in cmd:
                # Para Node, verificar que el archivo existe
                if args:
                    script_path = Path(args[0])
                    if script_path.exists():
                        result["status"] = "ready"
                        result["message"] = f"Node script: {script_path.name}"
                    else:
                        result["status"] = "error"
                        result["message"] = f"Script not found: {args[0]}"
                else:
                    result["status"] = "configured"
                    result["message"] = "Node MCP configured"
            else:
                # Comando genérico
                check = subprocess.run(
                    ["which", cmd],
                    capture_output=True,
                    timeout=5
                )
                if check.returncode == 0:
                    result["status"] = "ready"
                    result["message"] = f"Command available: {cmd}"
                else:
                    result["status"] = "warning"
                    result["message"] = f"Command not found: {cmd}"
                    
    except subprocess.TimeoutExpired:
        result["status"] = "warning"
        result["message"] = "Health check timed out"
    except Exception as e:
        result["status"] = "error"
        result["message"] = str(e)
    
    return result


def get_integration_docs() -> list:
    """Obtiene la lista de documentación de integraciones"""
    integrations = []
    integrations_path = DOCS_PATH / "integrations"
    
    if integrations_path.exists():
        for item in integrations_path.iterdir():
            if item.is_dir():
                guide_path = item / "guide.md"
                if guide_path.exists():
                    integrations.append({
                        "name": item.name,
                        "path": str(guide_path.relative_to(CLAUDIO_ROOT)),
                        "has_config": (item / "config.md").exists()
                    })
            elif item.suffix == ".md":
                integrations.append({
                    "name": item.stem,
                    "path": str(item.relative_to(CLAUDIO_ROOT)),
                    "has_config": False
                })
    
    return sorted(integrations, key=lambda x: x["name"])


def get_workflows() -> list:
    """Obtiene la lista de workflows disponibles"""
    workflows = []
    workflows_path = DOCS_PATH / "workflows"
    
    if workflows_path.exists():
        for item in workflows_path.iterdir():
            if item.suffix == ".md" and item.name != "README.md":
                workflows.append({
                    "name": item.stem.replace("-", " ").title(),
                    "path": str(item.relative_to(CLAUDIO_ROOT)),
                    "filename": item.name
                })
    
    return sorted(workflows, key=lambda x: x["name"])


# ============== WEBSOCKET CHAT ==============

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    session_id = "web_default"
    executor = ClaudeCodeExecutor()

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "message")

            if msg_type == "new_session":
                if session_id in chat_sessions:
                    del chat_sessions[session_id]
                await websocket.send_json({"type": "system", "content": "Nueva conversación iniciada."})
                continue

            if msg_type == "message":
                query = data.get("content", "").strip()
                if not query:
                    continue

                await websocket.send_json({"type": "start"})

                async def on_output(text: str):
                    await websocket.send_json({"type": "chunk", "content": text})

                async def on_error(text: str):
                    await websocket.send_json({"type": "error", "content": text})

                continue_session = session_id in chat_sessions
                result = await executor.execute_streaming(
                    query, session_id, continue_session, on_output, on_error
                )

                await websocket.send_json({
                    "type": "done",
                    "success": result["success"],
                    "returncode": result["returncode"]
                })

    except WebSocketDisconnect:
        logger.info(f"[Chat {session_id}] WebSocket disconnected")
    except Exception as e:
        logger.error(f"[Chat {session_id}] WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({"type": "error", "content": str(e)})
        except Exception:
            pass


# ============== ROUTES ==============

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """Página de chat a pantalla completa"""
    return templates.TemplateResponse("chat.html", {"request": request})


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard principal"""
    config = load_mcp_config()
    mcps = config.get("mcpServers", {})
    
    mcp_list = []
    for name, cfg in mcps.items():
        mcp_list.append({
            "name": name,
            "type": get_mcp_type(cfg),
            "icon": get_mcp_icon(name),
            "config": cfg
        })
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "mcps": mcp_list,
            "integrations": get_integration_docs(),
            "workflows": get_workflows(),
            "total_mcps": len(mcp_list)
        }
    )


@app.get("/api/mcps")
async def list_mcps():
    """Lista todos los MCPs configurados"""
    config = load_mcp_config()
    return config.get("mcpServers", {})


@app.get("/api/mcps/health")
async def check_all_mcps_health():
    """Verifica el estado de todos los MCPs"""
    config = load_mcp_config()
    mcps = config.get("mcpServers", {})
    
    # Ejecutar health checks en paralelo
    tasks = [check_mcp_health(name, cfg) for name, cfg in mcps.items()]
    results = await asyncio.gather(*tasks)
    
    return {
        "checked_at": datetime.now().isoformat(),
        "mcps": results
    }


@app.get("/api/mcps/{mcp_name}/health")
async def check_single_mcp_health(mcp_name: str):
    """Verifica el estado de un MCP específico"""
    config = load_mcp_config()
    mcps = config.get("mcpServers", {})
    
    if mcp_name not in mcps:
        raise HTTPException(status_code=404, detail=f"MCP '{mcp_name}' not found")
    
    return await check_mcp_health(mcp_name, mcps[mcp_name])


@app.get("/api/docs/{doc_type}")
async def get_docs(doc_type: str):
    """Obtiene documentación por tipo (integrations o workflows)"""
    if doc_type == "integrations":
        return get_integration_docs()
    elif doc_type == "workflows":
        return get_workflows()
    else:
        raise HTTPException(status_code=404, detail="Doc type not found")


@app.get("/api/docs/read")
async def read_doc(path: str):
    """Lee el contenido de un archivo de documentación"""
    full_path = CLAUDIO_ROOT / path
    
    # Seguridad: asegurar que el path está dentro de docs/
    if not str(full_path).startswith(str(DOCS_PATH)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        with open(full_path, "r") as f:
            content = f.read()
        return {"path": path, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/context")
async def get_context():
    """Obtiene el contexto actual de Claudio (CLAUDE.md)"""
    claude_md = CLAUDIO_ROOT / "CLAUDE.md"
    
    try:
        with open(claude_md, "r") as f:
            content = f.read()
        return {"path": "CLAUDE.md", "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
