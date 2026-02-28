# Weekly Bot Report

## Descripción
Reporte semanal automático del rendimiento del bot de WhatsApp. Se envía por email todos los lunes a las 9:00 AM.

## MCPs Utilizados
- **Google Sheets** - Lee datos del spreadsheet Full Funnel Performance
- **Gmail** - Envía el reporte por email

## Datos Fuente
- **Spreadsheet**: [Full Funnel Performance (Automated)](https://docs.google.com/spreadsheets/d/1PI2NnSzDhxCrb-NY18WgEiNpQyujgSG0RkPCw4c7IM8)
- **Sheets**: `Full Funnel metrics (ES) v2`, `Bot metrics`

## Métricas Incluidas
1. **Group Calls Booked por Bot** - Total y % vs No Booked, Total GC Booked, New Leads
2. **Show Up Rate (Cohorted)** - CR New Lead → GC Booked, GC Show Up, CR GC → 1:1
3. **No Booked Rate** - New Leads, No Booked, %
4. **Engagements del Bot** - GC y 1:1, totales, clients únicos
5. **Bot Activity** - CRM messages, success rate, reply rate, bot response rate

## Destinatarios
- ignacio.delacuba@prophero.com

## Schedule
- **Frecuencia**: Semanal
- **Día**: Lunes
- **Hora**: 9:00 AM
- **Cron**: `0 9 * * 1`

## Archivos
- **Script**: `scripts/weekly-bot-report.sh`
- **Logs**: `scripts/logs/weekly-bot-report.log`

## Ejecución Manual
```bash
./scripts/weekly-bot-report.sh
```

## Notas
- El script usa Claude Code CLI (`claude -p`) para generar y enviar el reporte
- Requiere que la Mac esté encendida el lunes a las 9am
- Los logs se guardan en `scripts/logs/`
- Para agregar destinatarios, editar el prompt en el script
