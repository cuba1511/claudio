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

$CLAUDE_BIN --dangerously-skip-permissions -p "Genera el reporte semanal del bot de WhatsApp usando los datos del spreadsheet Full Funnel Performance (ID: 1PI2NnSzDhxCrb-NY18WgEiNpQyujgSG0RkPCw4c7IM8, sheet con gid=1481538928 que es 'Full Funnel metrics (ES) v2').

Incluye estas métricas para la última semana completa vs la semana anterior (WoW), con delta absoluto y % de cambio:
1. Nuevos Leads
2. Group Calls Booked (Direct)
3. New Lead No Booked
4. Group Calls Booked by Bot (Total)
5. First Time - Group Calls Booked by Bot
6. % First Time
7. Rescheduled - Group Calls Booked by Bot
8. % Rescheduled
9. Group Calls Booked (Total)
10. % Group Calls Booked by Bot (from Total Group Calls)
11. Group Call Attended (Total)
12. Group Call Attended (Booked by Bot)
13. Show Up Rate (Total)
14. Bot - Show Up Rate

Manda el reporte por email en formato HTML con tablas a ignacio.delacuba@prophero.com con asunto 'Reporte Semanal Bot - Full Funnel Performance'. Usa los colores de PropHero (primary #2050f6). Usa flechas verdes/rojas para indicar si la métrica mejoró o empeoró." \
  2>&1 | tee -a "$LOG_FILE"

echo "$(date '+%Y-%m-%d %H:%M:%S') - Weekly bot report completed." >> "$LOG_FILE"
