/**
 * Servicio para gestión de reportes
 */
import { useAuthStore } from '@/stores/auth'

class ReportsService {
  constructor() {
    this.baseURL = '/api/reportes'
  }

  /**
   * Obtener headers de autenticación
   */
  getHeaders() {
    const authStore = useAuthStore()
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authStore.token}`
    }
  }

  /**
   * Listar reportes con filtros y paginación
   */
  async getReports(filters = {}, page = 1, pageSize = 20) {
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString()
      })

      // Agregar filtros
      Object.entries(filters).forEach(([key, value]) => {
        if (value) {
          params.append(key, value)
        }
      })

      const response = await fetch(`${this.baseURL}/?${params}`, {
        headers: this.getHeaders()
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Error al obtener reportes')
      }

      return await response.json()
    } catch (error) {
      console.error('Error obteniendo reportes:', error)
      throw error
    }
  }

  /**
   * Obtener detalles de un reporte específico
   */
  async getReportDetails(reportId) {
    try {
      const response = await fetch(`${this.baseURL}/${reportId}/`, {
        headers: this.getHeaders()
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Error al obtener detalles del reporte')
      }

      return await response.json()
    } catch (error) {
      console.error('Error obteniendo detalles del reporte:', error)
      throw error
    }
  }

  /**
   * Crear un nuevo reporte
   */
  async createReport(reportData) {
    try {
      const response = await fetch(this.baseURL, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(reportData)
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Error al crear el reporte')
      }

      return data
    } catch (error) {
      console.error('Error creando reporte:', error)
      throw error
    }
  }

  /**
   * Descargar un reporte
   */
  async downloadReport(reportId) {
    try {
      const response = await fetch(`${this.baseURL}/${reportId}/download/`, {
        headers: {
          'Authorization': this.getHeaders()['Authorization'],
          'Accept': 'application/octet-stream'
        }
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Error al descargar el reporte')
      }

      return response
    } catch (error) {
      console.error('Error descargando reporte:', error)
      throw error
    }
  }

  /**
   * Eliminar un reporte
   */
  async deleteReport(reportId) {
    try {
      const response = await fetch(`${this.baseURL}/${reportId}/delete/`, {
        method: 'DELETE',
        headers: this.getHeaders()
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Error al eliminar el reporte')
      }

      return true
    } catch (error) {
      console.error('Error eliminando reporte:', error)
      throw error
    }
  }

  /**
   * Obtener estadísticas de reportes
   */
  async getReportsStats() {
    try {
      const response = await fetch(`${this.baseURL}/stats/`, {
        headers: this.getHeaders()
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Error al obtener estadísticas')
      }

      return await response.json()
    } catch (error) {
      console.error('Error obteniendo estadísticas:', error)
      throw error
    }
  }

  /**
   * Limpiar reportes expirados (solo administradores)
   */
  async cleanupExpiredReports() {
    try {
      const response = await fetch(`${this.baseURL}/cleanup/`, {
        method: 'POST',
        headers: this.getHeaders()
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Error al limpiar reportes expirados')
      }

      return data
    } catch (error) {
      console.error('Error limpiando reportes expirados:', error)
      throw error
    }
  }

  /**
   * Generar reporte de calidad
   */
  async generateQualityReport(title, description = '', filters = {}) {
    return this.createReport({
      tipo_reporte: 'calidad',
      formato: 'pdf',
      titulo: title,
      descripcion: description,
      filtros: filters
    })
  }

  /**
   * Generar reporte de finca
   */
  async generateFincaReport(fincaId, title, description = '', filters = {}) {
    return this.createReport({
      tipo_reporte: 'finca',
      formato: 'pdf',
      titulo: title,
      descripcion: description,
      parametros: { finca_id: fincaId },
      filtros: filters
    })
  }

  /**
   * Generar reporte de auditoría
   */
  async generateAuditReport(title, description = '', filters = {}) {
    return this.createReport({
      tipo_reporte: 'auditoria',
      formato: 'pdf',
      titulo: title,
      descripcion: description,
      filtros: filters
    })
  }

  /**
   * Generar reporte personalizado
   */
  async generateCustomReport(tipoReporte, formato, title, parametros = {}, filtros = {}) {
    return this.createReport({
      tipo_reporte: 'personalizado',
      formato: formato,
      titulo: title,
      parametros: {
        tipo_reporte: tipoReporte,
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
        const filenameMatch = contentDisposition.match(/filename="(.+)"/)
        if (filenameMatch) {
          downloadFilename = filenameMatch[1]
        }
      }
      
      // Crear blob y descargar
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = downloadFilename
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      return true
    } catch (error) {
      console.error('Error descargando archivo de reporte:', error)
      throw error
    }
  }

  /**
   * Verificar estado de un reporte
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
      console.error('Error verificando estado del reporte:', error)
      throw error
    }
  }

  /**
   * Obtener tipos de reporte disponibles
   */
  getReportTypes() {
    return [
      { value: 'calidad', label: 'Reporte de Calidad', description: 'Análisis de calidad de granos de cacao' },
      { value: 'finca', label: 'Reporte de Finca', description: 'Análisis específico de una finca' },
      { value: 'auditoria', label: 'Reporte de Auditoría', description: 'Actividad y logs del sistema' },
      { value: 'personalizado', label: 'Reporte Personalizado', description: 'Reporte con parámetros específicos' }
    ]
  }

  /**
   * Obtener formatos disponibles
   */
  getReportFormats() {
    return [
      { value: 'pdf', label: 'PDF', description: 'Documento PDF con gráficos y tablas' },
      { value: 'excel', label: 'Excel', description: 'Hoja de cálculo Excel con datos detallados' },
      { value: 'csv', label: 'CSV', description: 'Archivo CSV con datos tabulares' },
      { value: 'json', label: 'JSON', description: 'Datos en formato JSON' }
    ]
  }

  /**
   * Obtener estados de reporte
   */
  getReportStates() {
    return [
      { value: 'completado', label: 'Completado', color: 'success' },
      { value: 'generando', label: 'Generando', color: 'warning' },
      { value: 'fallido', label: 'Fallido', color: 'danger' }
    ]
  }
}

// Crear instancia singleton
const reportsService = new ReportsService()

export default reportsService
export { ReportsService }
