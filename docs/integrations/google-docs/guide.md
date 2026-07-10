# Google Docs Integration

## Setup (una sola vez)

### Paso 1: Crear proyecto en Google Cloud Console

1. Ir a https://console.cloud.google.com/
2. Crear proyecto nuevo (ej: "MCP Docs Server")
3. Habilitar 3 APIs (APIs & Services → Library):
   - Google Docs API
   - Google Sheets API
   - Google Drive API

### Paso 2: Configurar OAuth

1. APIs & Services → OAuth consent screen
2. User Type: External → Create
3. Llenar: App name, email de soporte, email de contacto → Save and Continue
4. Scopes → Add or Remove Scopes, agregar:
   - `https://www.googleapis.com/auth/documents`
   - `https://www.googleapis.com/auth/spreadsheets`
   - `https://www.googleapis.com/auth/drive.file`
5. Test Users → agregar tu email de Google → Save

### Paso 3: Crear credenciales

1. APIs & Services → Credentials
2. + Create Credentials → OAuth client ID
3. Application type: Desktop app
4. Click Create → Download JSON
5. Renombrar a `credentials.json`

### Paso 4: Clonar y compilar

```bash
cd ~/mcps
git clone https://github.com/a-bonus/google-docs-mcp.git google-docs-mcp
cd google-docs-mcp
cp ~/Downloads/credentials.json .
npm install
npm run build
```

### Paso 5: Autorizar (una sola vez)

```bash
node ./dist/server.js
```

1. Copiar la URL que imprime y abrirla en el browser
2. Loggearte con la cuenta agregada como Test User
3. Dar permisos → te redirige a localhost con error (es normal)
4. De la URL del browser, copiar el código entre `code=` y `&scope`
5. Pegarlo en la terminal cuando lo pida
6. Se genera `token.json` — **no subir a git nunca**

### Paso 6: Reiniciar Claude Code / Cursor

Salir y volver a entrar. Las herramientas de Google Docs, Sheets y Drive ya estarán disponibles.

---

## Configuración

El servidor compilado se ejecuta con `node` apuntando al `dist/server.js` local:

```json
"google-docs": {
  "command": "node",
  "args": ["/Users/ignaciodelacuba/mcps/google-docs-mcp/dist/index.js"]
}
```

Configurado en `mcp/cursor-config.json` (Cursor) y `~/.claude/settings.json` (Claude Code global).

> **Archivos que NO se commitean:** `credentials.json` y `token.json`

## Herramientas Disponibles

| Tool | Descripción |
|------|-------------|
| `createDocument` | Crear documento en Drive |
| `readGoogleDoc` | Leer contenido de un doc |
| `appendToGoogleDoc` | Añadir contenido al final |
| `insertText` | Insertar texto en posición |
| `applyTextStyle` | Formatear texto |
| `createSpreadsheet` | Crear hoja de cálculo |
| `readSpreadsheet` | Leer datos de una sheet |
| `writeSpreadsheet` | Escribir datos en una sheet |

## Carpeta DS & AI

Google Drive folder ID: `1M7cqCebNXSJ-kcALWC3CVS44C6sAKcFo`
URL: https://drive.google.com/drive/folders/1M7cqCebNXSJ-kcALWC3CVS44C6sAKcFo

Naming convention para reportes: `DS & AI Monthly Review — [Mes] [Año]`
