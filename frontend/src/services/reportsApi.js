/**
 * Servicio de API para reportes en CacaoScan
 * Maneja la descarga de reportes Excel
 */
import api from './api'

const reportsApi = {
  /**
   * Descargar reporte Excel de agricultores con sus fincas
   */
  async downloadReporteAgricultores() {
    try {
      const response = await api.get('/reports/agricultores/', {
        responseType: 'blob' // Importante: especificar que esperamos un blob
      })
      
      // Crear URL del objeto blob
      const url = window.URL.createObjectURL(new Blob([response.data]))
      
      // Crear elemento link y configurarlo
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `reporte_agricultores_${new Date().getTime()}.xlsx`)
      
      // Agregar al DOM, hacer click y remover
      document.body.appendChild(link)
      link.click()
      link.remove()
      
      // Limpiar el URL del objeto
      window.URL.revokeObjectURL(url)
      
      return { success: true }
    } catch (error) {
      console.error('Error descargando reporte de agricultores:', error)
      throw error
    }
  },

  /**
   * Descargar reporte Excel de usuarios del sistema
   */
  async downloadReporteUsuarios() {
    try {
      const response = await api.get('/reports/usuarios/', {
        responseType: 'blob'
      })
      
      // Crear URL del objeto blob
      const url = window.URL.createObjectURL(new Blob([response.data]))
      
      // Crear elemento link y configurarlo
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `reporte_usuarios_${new Date().getTime()}.xlsx`)
      
      // Agregar al DOM, hacer click y remover
      document.body.appendChild(link)
      link.click()
      link.remove()
      
      // Limpiar el URL del objeto
      window.URL.revokeObjectURL(url)
      
      return { success: true }
    } catch (error) {
      console.error('Error descargando reporte de usuarios:', error)
      throw error
    }
  }
}

export default reportsApi
