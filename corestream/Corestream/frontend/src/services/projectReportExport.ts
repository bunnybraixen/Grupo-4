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
