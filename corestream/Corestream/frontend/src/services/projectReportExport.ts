/**
 * Servicio de exportación del Reporte General del Proyecto (WEB-06).
 *
 * Genera los archivos SIN dependencias externas:
 *  - PDF: construido directamente con el formato PDF (texto simple, A4).
 *  - Excel: SpreadsheetML 2003 (.xls), que Excel/LibreOffice abren nativamente.
 *
 * Ambos formatos incluyen la fecha de generación y el alcance del reporte
 * (proyecto, desarrollador y sprint aplicados en pantalla).
 */

// ── Modelo del reporte (lo arma la vista con los filtros en pantalla) ───────

export interface ProjectReportScope {
  projectName: string
  developerName: string
  sprintName: string
  generatedAt: string
}

export interface ProjectReportIndicator {
  label: string
  value: string
}

export interface ProjectReportTable {
  title: string
  headers: string[]
  rows: string[][]
}

export interface ProjectReportPayload {
  scope: ProjectReportScope
  indicators: ProjectReportIndicator[]
  tables: ProjectReportTable[]
}

// ── Utilidades comunes ──────────────────────────────────────────────────────

const scopeLines = (scope: ProjectReportScope): string[][] => [
  ['Proyecto', scope.projectName],
  ['Desarrollador', scope.developerName],
  ['Sprint', scope.sprintName],
  ['Generado', scope.generatedAt]
]

const fileStamp = (): string => new Date().toISOString().split('T')[0]

const downloadBlob = (blob: Blob, filename: string): void => {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

// ── PDF (sin librerías) ─────────────────────────────────────────────────────

/** Escapa el texto para un literal PDF (codificación WinAnsi = Latin-1). */
const pdfEscape = (text: string): string => {
  let out = ''
  for (const ch of String(text)) {
    const code = ch.codePointAt(0) ?? 63
    if (ch === '\\') out += '\\\\'
    else if (ch === '(') out += '\\('
    else if (ch === ')') out += '\\)'
    else if (code < 256) out += ch
    else out += '?'
  }
  return out
}

const PAGE_W = 595 // A4 en puntos
const PAGE_H = 842
const MARGIN = 45
const BOTTOM = PAGE_H - MARGIN

/** Generador mínimo de PDF multipágina con texto y tablas simples. */
class SimplePdf {
  private pages: string[] = []
  private current = ''
  /**_cursor vertical (px desde el borde superior); público para que la vista pueda ajustar saltos */
  y = MARGIN

  addPage(): void {
    if (this.current || !this.pages.length) this.pages.push(this.current)
    this.current = ''
    this.y = MARGIN
  }

  private ensureSpace(height: number): void {
    if (this.y + height > BOTTOM) this.addPage()
  }

  text(value: string, opts: { x?: number; size?: number; bold?: boolean; gap?: number } = {}): void {
    const { x = MARGIN, size = 10, bold = false, gap = size + 4 } = opts
    this.ensureSpace(gap)
    const font = bold ? '/F2' : '/F1'
    this.current += `BT ${font} ${size} Tf 1 0 0 1 ${x} ${PAGE_H - this.y} Tm (${pdfEscape(value)}) Tj ET\n`
    this.y += gap
  }

  rule(color: [number, number, number] = [0.85, 0.85, 0.85]): void {
    this.ensureSpace(6)
    const y = PAGE_H - this.y
    this.current += `${color.join(' ')} RG ${MARGIN} ${y} m ${PAGE_W - MARGIN} ${y} l S\n`
    this.y += 6
  }

  table(headers: string[], rows: string[][]): void {
    const size = 9
    const gap = size + 4
    // fila de encabezado con fondo; el bloque vive ENTRO del cursor (sin
    // sobresalir) y el texto se centra verticalmente dentro de él.
    this.ensureSpace(gap * 2)
    const rectY = PAGE_H - this.y - gap
    const textY = rectY + 4.5
    this.current += `0.08 0.15 0.19 rg ${MARGIN} ${rectY} ${PAGE_W - 2 * MARGIN} ${gap} re f\n`
    let x = MARGIN + 4
    for (const header of headers) {
      this.current += `1 1 1 rg BT /F2 ${size} Tf 1 0 0 1 ${x} ${textY} Tm (${pdfEscape(header)}) Tj ET\n`
      x += 110
    }
    this.current += '0 0 0 rg\n'
    // +15: las letras se dibujan HACIA ARRIBA desde la línea base (~9pt de
    // altura); con 15pt de respiro queda ~3pt de aire bajo el bloque azul.
    this.y += gap + 15
    for (const row of rows) {
      this.ensureSpace(gap)
      x = MARGIN + 4
      for (const cell of row) {
        this.current += `BT /F1 ${size} Tf 1 0 0 1 ${x} ${PAGE_H - this.y} Tm (${pdfEscape(cell)}) Tj ET\n`
        x += 110
      }
      this.y += gap
    }
    this.y += 6
  }

  save(filename: string): void {
    if (this.current) this.pages.push(this.current)
    if (!this.pages.length) this.pages.push('')
    const pageCount = this.pages.length

    const objects: string[] = []
    const addObject = (body: string): void => {
      objects.push(body)
    }

    // ids: 1 catálogo, 2 pages, pares (página, stream) desde 3, luego fuentes
    const fontId = 4 + pageCount * 2
    const kids = this.pages.map((_, i) => `${3 + i * 2} 0 R`).join(' ')
    addObject('<< /Type /Catalog /Pages 2 0 R >>')
    addObject(`<< /Type /Pages /Kids [${kids}] /Count ${pageCount} >>`)

    this.pages.forEach((content, i) => {
      addObject(
        `<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${PAGE_W} ${PAGE_H}] ` +
          `/Contents ${4 + i * 2} 0 R /Resources << /Font << /F1 ${fontId} 0 R /F2 ${fontId + 1} 0 R >> >> >>`
      )
      addObject(`<< /Length ${content.length} >>\nstream\n${content}endstream`)
    })
    addObject('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>')
    addObject('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>')

    let pdf = '%PDF-1.4\n'
    const offsets: number[] = []
    objects.forEach((body, i) => {
      offsets.push(pdf.length)
      pdf += `${i + 1} 0 obj\n${body}\nendobj\n`
    })
    const xrefStart = pdf.length
    pdf += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`
    offsets.forEach((off) => {
      pdf += `${String(off).padStart(10, '0')} 00000 n \n`
    })
    pdf += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefStart}\n%%EOF`

    // Latin-1: cada char = 1 byte (todos los códigos ya están acotados a 255)
    const bytes = new Uint8Array(pdf.length)
    for (let i = 0; i < pdf.length; i++) bytes[i] = pdf.charCodeAt(i) & 0xff
    downloadBlob(new Blob([bytes], { type: 'application/pdf' }), `corestream-reporte-${fileStamp()}.pdf`)
  }
}


// ── Excel (SpreadsheetML 2003, sin librerías) ───────────────────────────────

const xmlEscape = (value: string): string =>
  String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')

const xmlRow = (cells: string[], header = false): string =>
  `<Row>${cells
    .map(
      (cell) =>
        `<Cell${header ? ' ss:StyleID="hdr"' : ''}><Data ss:Type="String">${xmlEscape(cell)}</Data></Cell>`
    )
    .join('')}</Row>`

export function exportProjectReportExcel(payload: ProjectReportPayload): void {
  const rows: string[] = []

  rows.push(xmlRow(['Reporte General del Proyecto'], true))
  rows.push(xmlRow(['']))
  rows.push(xmlRow(['Alcance del reporte'], true))
  for (const [label, value] of scopeLines(payload.scope)) {
    rows.push(xmlRow([label, value]))
  }
  rows.push(xmlRow(['']))
  rows.push(xmlRow(['Indicadores'], true))
  rows.push(xmlRow(['Indicador', 'Valor'], true))
  for (const item of payload.indicators) {
    rows.push(xmlRow([item.label, item.value]))
  }
  for (const table of payload.tables) {
    rows.push(xmlRow(['']))
    rows.push(xmlRow([table.title], true))
    rows.push(xmlRow(table.headers, true))
    for (const row of table.rows) {
      rows.push(xmlRow(row))
    }
  }

  const xml =
    '<?xml version="1.0"?>\n<?mso-application progid="Excel.Sheet"?>\n' +
    '<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet" ' +
    'xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">' +
    '<Styles>' +
    '<Style ss:ID="hdr"><Font ss:Bold="1"/><Interior ss:Color="#D9EAD3" ss:Pattern="Solid"/></Style>' +
    '</Styles>' +
    '<Worksheet ss:Name="Reporte"><Table>' +
    rows.join('') +
    '</Table></Worksheet></Workbook>'

  const blob = new Blob(['﻿' + xml], { type: 'application/vnd.ms-excel' })
  downloadBlob(blob, `corestream-reporte-${fileStamp()}.xls`)
}

export function exportProjectReportPDF(payload: ProjectReportPayload): void {
  const doc = new SimplePdf()

  doc.text('CORESTREAM', { size: 20, bold: true, gap: 26 })
  doc.text('Reporte General del Proyecto', { size: 12, bold: true, gap: 20 })
  doc.rule([0.68, 0.85, 0.29])

  doc.text('Alcance del reporte', { size: 11, bold: true })
  for (const [label, value] of scopeLines(payload.scope)) {
    doc.text(`${label}: ${value}`, { size: 9 })
  }
  doc.y += 8

  doc.text('Indicadores', { size: 11, bold: true })
  doc.table(['Indicador', 'Valor'], payload.indicators.map((item) => [item.label, item.value]))
  doc.y += 4

  for (const table of payload.tables) {
    if (!table.rows.length) continue
    doc.text(table.title, { size: 11, bold: true })
    doc.table(table.headers, table.rows)
  }

  doc.save('reporte')
}
