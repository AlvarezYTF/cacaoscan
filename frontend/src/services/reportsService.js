/**
 * Servicio para gestión de reportes
 * Usa apiClient para reducir duplicación de código
 * Normaliza DTOs para consistencia en el frontend
 */
import { fetchGet, fetchPost, fetchDelete } from './apiClient'
import {
  normalizeReportDTO,
  normalizeReportListResponse,
  normalizeReportStatsResponse,
  buildReportRequestPayload
} from './reports/reportDTOs'

class ReportsService {
  baseURL = '/api/v1/reportes'

  /**
   * Listar reportes con filtros y paginación
   * @param {Object} filters - Filter parameters
   * @param {number} page - Page number
   * @param {number} pageSize - Items per page
   * @returns {Promise<Object>} Normalized report list with pagination
   */
  async getReports(filters = {}, page = 1, pageSize = 20) {
    const params = {
      page,
      page_size: pageSize,
      ...filters
    }
    const response = await fetchGet(`${this.baseURL}/`, params)
    return normalizeReportListResponse(response)
  }

  /**
   * Obtener detalles de un reporte específico
   * @param {number} reportId - Report ID
   * @returns {Promise<Object>} Normalized report DTO
   */
  async getReportDetails(reportId) {
    const response = await fetchGet(`${this.baseURL}/${reportId}/`)
    return normalizeReportDTO(response)
  }

  /**
   * Crear un nuevo reporte
   * @param {Object} reportData - Report data from form
   * @returns {Promise<Object>} Normalized report DTO
   */
  async createReport(reportData) {
    const payload = buildReportRequestPayload(reportData)
    const response = await fetchPost(`${this.baseURL}/`, payload)
    return normalizeReportDTO(response)
  }

  /**
   * Descargar un reporte
   */
  async downloadReport(reportId) {
    // Para descargas de archivos, necesitamos usar fetch directamente
    // ya que apiClient devuelve JSON por defecto
    const token = localStorage.getItem('access_token') || localStorage.getItem('token')
    const url = `${this.baseURL}/${reportId}/download/`
    const fullUrl = url.startsWith('http') ? url : `${globalThis.location.origin}${url}`
    
    const response = await fetch(fullUrl, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': '*/*' // Accept any content type for file downloads
      }
    })

    if (!response.ok) {
      // Try to get error message from response
      let errorMessage = `Error al descargar el reporte (${response.status})`
      try {
        const contentType = response.headers.get('content-type')
        if (contentType && contentType.includes('application/json')) {
          const errorData = await response.json()
          errorMessage = errorData.error || errorData.detail || errorMessage
        } else {
          const text = await response.text()
          if (text) {
            errorMessage = text.substring(0, 200) // Limit error message length
          }
        }
      } catch (e) {
        // If we can't parse the error, use the default message
        console.warn('Could not parse error response:', e)
      }
      throw new Error(errorMessage)
    }

    return response
  }

  /**
   * Eliminar un reporte
   */
  async deleteReport(reportId) {
    await fetchDelete(`${this.baseURL}/${reportId}/delete/`)
    return true
  }

  /**
   * Obtener estadísticas de reportes
   * @returns {Promise<Object>} Normalized report stats
   */
  async getReportsStats() {
    const response = await fetchGet(`${this.baseURL}/stats/`)
    return normalizeReportStatsResponse(response)
  }

  /**
   * Limpiar reportes expirados (solo administradores)
   */
  async cleanupExpiredReports() {
    return await fetchPost(`${this.baseURL}/cleanup/`)
  }

  /**
   * Generar reporte de calidad
   * @param {string} title - Report title
   * @param {string} description - Report description
   * @param {Object} filters - Filter parameters
   * @returns {Promise<Object>} Normalized report DTO
   */
  async generateQualityReport(title, description = '', filters = {}) {
    return this.createReport({
      tipo_reporte: 'CALIDAD',
      formato: 'EXCEL',
      titulo: title,
      descripcion: description,
      filtros: filters
    })
  }

  /**
   * Generar reporte de finca
   * @param {number} fincaId - Finca ID
   * @param {string} title - Report title
   * @param {string} description - Report description
   * @param {Object} filters - Filter parameters
   * @returns {Promise<Object>} Normalized report DTO
   */
  async generateFincaReport(fincaId, title, description = '', filters = {}) {
    return this.createReport({
      tipo_reporte: 'FINCA',
      formato: 'EXCEL',
      titulo: title,
      descripcion: description,
      parametros: { finca_id: fincaId },
      filtros: filters
    })
  }

  /**
   * Generar reporte de auditoría
   * @param {string} title - Report title
   * @param {string} description - Report description
   * @param {Object} filters - Filter parameters
   * @returns {Promise<Object>} Normalized report DTO
   */
  async generateAuditReport(title, description = '', filters = {}) {
    return this.createReport({
      tipo_reporte: 'AUDITORIA',
      formato: 'EXCEL',
      titulo: title,
      descripcion: description,
      filtros: filters
    })
  }

  /**
   * Generar reporte personalizado
   * @param {string} tipoReporte - Report type
   * @param {string} formato - Report format
   * @param {string} title - Report title
   * @param {Object} parametros - Custom parameters
   * @param {Object} filtros - Filter parameters
   * @returns {Promise<Object>} Normalized report DTO
   */
  async generateCustomReport(tipoReporte, formato, title, parametros = {}, filtros = {}) {
    return this.createReport({
      tipo_reporte: 'PERSONALIZADO',
      formato: formato.toUpperCase(),
      titulo: title,
      parametros: {
        tipo_reporte: tipoReporte.toUpperCase(),
        ...parametros
      },
      filtros: filtros
    })
  }

  /**
   * Descargar archivo de reporte
   */
  async downloadReportFile(reportId, filename = null) {
    try {
      const response = await this.downloadReport(reportId)
      
      // Obtener el nombre del archivo del header Content-Disposition
      const contentDisposition = response.headers.get('Content-Disposition')
      let downloadFilename = filename || `reporte_${reportId}`
      
      if (contentDisposition) {
        const filenameRegex = /filename="(.+)"/
        const filenameMatch = filenameRegex.exec(contentDisposition)
        if (filenameMatch) {
          downloadFilename = filenameMatch[1]
        }
      }
      
      // Crear blob y descargar
      const blob = await response.blob()
      const url = globalThis.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = downloadFilename
      document.body.appendChild(link)
      link.click()
      link.remove()
      globalThis.URL.revokeObjectURL(url)
      
      return true
    } catch (error) {
      throw error
    }
  }

  /**
   * Verificar estado de un reporte
   * @param {number} reportId - Report ID
   * @returns {Promise<Object>} Status information
   */
  async checkReportStatus(reportId) {
    try {
      const report = await this.getReportDetails(reportId)
      return {
        id: report.id,
        estado: report.estado,
        esta_expirado: report.esta_expirado,
        fecha_generacion: report.fecha_generacion,
        mensaje_error: report.mensaje_error
      }
    } catch (error) {
      throw error
    }
  }

  /**
   * Obtener tipos de reporte disponibles
   */
  getReportTypes() {
    return [
      { value: 'CALIDAD', label: 'Reporte de Calidad', description: 'Análisis de calidad de granos de cacao' },
      { value: 'FINCA', label: 'Reporte de Finca', description: 'Análisis específico de una finca' },
      { value: 'AUDITORIA', label: 'Reporte de Auditoría', description: 'Actividad y logs del sistema' },
      { value: 'PERSONALIZADO', label: 'Reporte Personalizado', description: 'Reporte con parámetros específicos' }
    ]
  }

  /**
   * Obtener formatos disponibles
   */
  getReportFormats() {
    return [
      { value: 'EXCEL', label: 'Excel', description: 'Hoja de cálculo Excel con datos detallados' },
      { value: 'PDF', label: 'PDF', description: 'Documento PDF con gráficos y tablas' },
      { value: 'CSV', label: 'CSV', description: 'Archivo CSV con datos tabulares' },
      { value: 'JSON', label: 'JSON', description: 'Datos en formato JSON' }
    ]
  }

  /**
   * Obtener estados de reporte
   */
  getReportStates() {
    return [
      { value: 'COMPLETADO', label: 'Completado', color: 'success' },
      { value: 'GENERANDO', label: 'Generando', color: 'warning' },
      { value: 'PENDIENTE', label: 'Pendiente', color: 'info' },
      { value: 'FALLIDO', label: 'Fallido', color: 'danger' }
    ]
  }
}

// Crear instancia singleton
const reportsService = new ReportsService()

export default reportsService
export { ReportsService }
