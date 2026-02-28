#!/bin/bash
# Monthly DS & AI Report - Cron Script
# Runs on the 1st of each month at 10:00 AM
# Generates the DS & AI squad monthly review from ClickUp and publishes to Google Drive

set -e

WORKSPACE="/Users/ignaciodelacuba/Dev/claudio"
CLAUDE_BIN="/Users/ignaciodelacuba/.local/bin/claude"
LOG_FILE="$WORKSPACE/scripts/logs/monthly-ds-ai-report.log"

mkdir -p "$WORKSPACE/scripts/logs"

echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting monthly DS & AI report..." >> "$LOG_FILE"

cd "$WORKSPACE"

$CLAUDE_BIN --dangerously-skip-permissions -p "Genera el reporte mensual de DS & AI del mes anterior completo. Sigue el workflow definido en docs/workflows/monthly-ds-ai-report.md paso a paso:

1. Calcula el rango de fechas del mes anterior automáticamente
2. Pull Epics del quarter actual desde ClickUp (list 901215396098)
3. Pull tasks completadas y en progreso del mes desde los sprint lists (901213056238, 901215046511, 901213056239, 901213056236)
4. Pull Initiatives donde DS & AI está involucrado (list 901213053436)
5. Calcula métricas de delivery: Say/Do Ratio, Carry-over, Bug Rate, Cycle Time approx, Completion Rate por Epic
6. Construye el reporte con las 4 secciones de la agenda: Wins & Learnings, Metrics, Initiatives & Epics Review, Recap
7. Crea un Google Doc con el reporte en la carpeta 1M7cqCebNXSJ-kcALWC3CVS44C6sAKcFo con nombre 'DS & AI Monthly Review — [Mes] [Año]'

Usa formato estructurado con tablas, indicadores de status (🟢🟡🔴), y los colores de PropHero." \
  2>&1 | tee -a "$LOG_FILE"

echo "$(date '+%Y-%m-%d %H:%M:%S') - Monthly DS & AI report completed." >> "$LOG_FILE"
