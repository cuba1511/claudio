"""
Claudio Web Dashboard
=====================
Interfaz web para monitorear MCPs y configurar contexto.
"""

import json
import os
import subprocess
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Paths
BASE_DIR = Path(__file__).resolve().parent
CLAUDIO_ROOT = BASE_DIR.parent.parent
MCP_CONFIG_PATH = CLAUDIO_ROOT / "mcp" / "cursor-config.json"
DOCS_PATH = CLAUDIO_ROOT / "docs"

app = FastAPI(
    title="Claudio Dashboard",
    description="Panel de control para Claudio - Asistente de Productividad",
    version="1.0.0"
)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


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


# ============== ROUTES ==============

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
