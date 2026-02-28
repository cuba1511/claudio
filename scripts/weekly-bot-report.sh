#!/bin/bash
# Weekly Bot Report - Cron Script
# Runs every Monday at 9:00 AM
# Generates and sends the weekly bot performance report via email

set -e

WORKSPACE="/Users/ignaciodelacuba/Dev/claudio"
CLAUDE_BIN="/Users/ignaciodelacuba/.local/bin/claude"
LOG_FILE="$WORKSPACE/scripts/logs/weekly-bot-report.log"

mkdir -p "$WORKSPACE/scripts/logs"

echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting weekly bot report..." >> "$LOG_FILE"

cd "$WORKSPACE"

$CLAUDE_BIN -p "Genera el reporte semanal del bot de WhatsApp usando los datos del spreadsheet Full Funnel Performance (ID: 1PI2NnSzDhxCrb-NY18WgEiNpQyujgSG0RkPCw4c7IM8, sheet 'Full Funnel metrics (ES) v2' y 'Bot metrics').

Incluye estas métricas para la última semana completa vs la semana anterior:
1. Total de Group Calls bookeadas por el bot, con % respecto a no booked y respecto a total GC booked
2. Show Up Rate cohorted
3. Engagements del bot (GC y 1:1)
4. Bot Activity: mensajes enviados, success rate, reply rate, bot response rate

Manda el reporte por email en formato HTML con tablas a ignacio.delacuba@prophero.com con asunto 'Reporte Semanal Bot - Full Funnel Performance'. Usa los colores de PropHero (primary #2050f6)." \
  --allowedTools "mcp__google-docs-mcp__readSpreadsheet,mcp__google-docs-mcp__getSpreadsheetInfo,mcp__gmail__send_email" \
  2>&1 | tail -20 >> "$LOG_FILE"

echo "$(date '+%Y-%m-%d %H:%M:%S') - Weekly bot report completed." >> "$LOG_FILE"
