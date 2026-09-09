/**
 * Servicio de Exportación de Reportes
 * Genera y descarga reportes en PDF y CSV
 */

import type { AnalyticsReport } from '@/types/analytics'
import jsPDF from 'jspdf'

export async function exportToPDF(
  data: AnalyticsReport,
  period: string
): Promise<void> {
  const doc = new jsPDF({ orientation: 'portrait', format: 'a4' })
  const today = new Date().toISOString().split('T')[0]

  // ── HEADER ──────────────────────────────────────────────────
  doc.setFillColor(20, 39, 48) // #142730 dark-gray
  doc.rect(0, 0, 210, 40, 'F')

  doc.setFontSize(22)
  doc.setFont('helvetica', 'bold')
  doc.setTextColor(173, 234, 75) // #ADEA4B Lime Alloxentric
  doc.text('CORESTREAM', 15, 18)

  doc.setFontSize(11)
  doc.setFont('helvetica', 'normal')
  doc.setTextColor(231, 233, 234) // #E7E9EA light-gray
  doc.text('Reporte de Rendimiento del Equipo', 15, 27)

  doc.setFontSize(9)
  doc.setTextColor(161, 169, 172) // #A1A9AC medium-gray
  doc.text(`Período: ${period}   |   Generado: ${today}`, 15, 35)

  // ── KPIs ─────────────────────────────────────────────────────
  const kpis = [
    { label: 'Eficiencia del Equipo', value: `${data.teamKPIs.efficiencyIndex}%` },
    { label: 'Índice de Bloqueo', value: `${data.teamKPIs.blockRate}%` },
    { label: 'Índice de Redirección', value: `${data.teamKPIs.redirectRate}%` },
  ]
  let xKpi = 15
  kpis.forEach((kpi) => {
    doc.setFillColor(245, 245, 245) // #F5F5F5 light
    doc.roundedRect(xKpi, 48, 58, 24, 2, 2, 'F')
    doc.setFontSize(20)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(20, 39, 48) // #142730 dark
    doc.text(kpi.value, xKpi + 29, 62, { align: 'center' })
    doc.setFontSize(8)
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(90, 104, 110) // #5A686E gray
    doc.text(kpi.label, xKpi + 29, 69, { align: 'center' })
    xKpi += 64
  })

  // ── TABLA ────────────────────────────────────────────────────
  let y = 84
  doc.setFontSize(11)
  doc.setFont('helvetica', 'bold')
  doc.setTextColor(20, 39, 48)
  doc.text('Rendimiento Individual', 15, y)
  y += 6

  const cols = ['Desarrollador', 'Completadas', 'Editados', 'Preguntas', 'Derivaciones', 'T.Promedio']
  const colW = [55, 26, 24, 24, 30, 26]

  // Header tabla
  doc.setFillColor(20, 39, 48)
  doc.rect(15, y, 180, 8, 'F')
  doc.setFontSize(8)
  doc.setFont('helvetica', 'bold')
  doc.setTextColor(255, 255, 255)
  let xCol = 17
  cols.forEach((col, i) => {
    doc.text(col, xCol, y + 5.5)
    xCol += colW[i]
  })
  y += 8

  // Filas
  data.developers.forEach((dev, idx) => {
    const h = Math.floor((dev.avgTimeMinutes ?? dev.averageHoursPerTicket ?? 0) / 60)
    const m = Math.floor((dev.avgTimeMinutes ?? dev.averageHoursPerTicket ?? 0) % 60)
    const row = [
      dev.userName,
      String(dev.processedTickets ?? dev.completedTickets ?? 0),
      String(dev.editedTickets ?? 0),
      String(dev.questionsRaised ?? 0),
      String(dev.redirections ?? 0),
      `${h}h ${m}m`,
    ]
    doc.setFillColor(idx % 2 === 0 ? 255 : 247, 255, 255) // Alternating rows
    doc.rect(15, y, 180, 7, 'F')
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(20, 39, 48)
    xCol = 17
    row.forEach((cell, i) => {
      doc.text(cell, xCol, y + 5)
      xCol += colW[i]
    })
    y += 7
    // Nueva página si se acaba el espacio
    if (y > 270) {
      doc.addPage()
      y = 20
    }
  })

  // Footer
  const pageCount = doc.getNumberOfPages()
  for (let p = 1; p <= pageCount; p++) {
    doc.setPage(p)
    doc.setFontSize(8)
    doc.setTextColor(161, 169, 172)
    doc.text(`CoreStream — ${period}`, 15, 287)
    doc.text(`Pág. ${p} de ${pageCount}`, 195, 287, { align: 'right' })
  }

  doc.save(`corestream-reporte-${period}-${today}.pdf`)
}

export function exportToCSV(data: AnalyticsReport, period: string): void {
  const today = new Date().toISOString().split('T')[0]
  const BOM = '﻿' // UTF-8 BOM para Excel Chile

  const lines: string[] = [
    '"Métrica","Valor"',
    `"Eficiencia del Equipo","${data.teamKPIs.efficiencyIndex}%"`,
    `"Índice de Bloqueo","${data.teamKPIs.blockRate}%"`,
    `"Índice de Redirección","${data.teamKPIs.redirectRate}%"`,
    `"Período","${period}"`,
    '',
    '"Desarrollador","Completadas","Editados","Preguntas","Derivaciones","Tiempo Promedio (min)"',
    ...data.developers.map(
      (d) =>
        `"${d.userName}",${d.processedTickets ?? d.completedTickets ?? 0},${d.editedTickets ?? 0},${d.questionsRaised ?? 0},${d.redirections ?? 0},${d.avgTimeMinutes ?? Math.round((d.averageHoursPerTicket ?? 0) * 60)}`
    ),
  ]

  const csv = BOM + lines.join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `corestream-reporte-${period}-${today}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
