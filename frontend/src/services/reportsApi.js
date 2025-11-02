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
        responseType: 'blob', // Importante: especificar que esperamos un blob
        headers: {
          'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
      })
      
      // Verificar que la respuesta sea un blob
      if (!(response.data instanceof Blob)) {
        throw new Error('La respuesta del servidor no es un archivo válido')
      }
      
      // Intentar obtener el nombre del archivo desde el Content-Disposition header
      let filename = `reporte_agricultores_${new Date().toISOString().slice(0, 10)}.xlsx`
      const contentDisposition = response.headers['content-disposition']
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '')
        }
      }
      
      // Crear URL del objeto blob
      const url = window.URL.createObjectURL(response.data)
      
      // Crear elemento link y configurarlo
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', filename)
      link.style.display = 'none'
      
      // Agregar al DOM, hacer click y remover
      document.body.appendChild(link)
      link.click()
      
      // Esperar un momento antes de remover y limpiar
      setTimeout(() => {
        document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      }, 100)
      
      return { success: true }
    } catch (error) {
      console.error('Error descargando reporte de agricultores:', error)
      
      // Si el error tiene respuesta, intentar mostrar el mensaje del servidor
      if (error.response) {
        // Si la respuesta es un blob con un JSON de error, leerlo
        if (error.response.data instanceof Blob && error.response.data.type === 'application/json') {
          try {
            const errorText = await error.response.data.text()
            const errorJson = JSON.parse(errorText)
            throw new Error(errorJson.error || errorJson.message || 'Error al generar el reporte')
          } catch (parseError) {
            throw new Error('Error al generar el reporte Excel')
          }
        }
        
        throw new Error(error.response.data?.error || error.response.data?.message || 'Error al generar el reporte')
      }
      
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
