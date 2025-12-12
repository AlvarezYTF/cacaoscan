/**
 * Servicio de API para reportes en CacaoScan
 * Maneja la descarga de reportes Excel
 */
import api from './api'

/**
 * Parse error response from blob JSON
 * @param {Blob} errorBlob - The error response blob
 * @returns {Promise<string>} The error message from the JSON
 * @throws {Error} If parsing fails or error message cannot be extracted
 */
const parseErrorBlob = async (errorBlob) => {
  try {
    const errorText = await errorBlob.text()
    const errorJson = JSON.parse(errorText)
    return errorJson.error || errorJson.message || 'Error al generar el reporte'
  } catch (parseError) {
    // Handle JSON parsing errors when reading error response
    // If parsing fails, we can't extract the server error message
    // Log the parse error for debugging and throw a descriptive error
    const parseErrorMessage = parseError instanceof Error ? parseError.message : String(parseError)
    const parseErrorStack = parseError instanceof Error ? parseError.stack : undefined
    
    // Log the parsing error for debugging
    console.error('Error parsing error response blob:', parseError)
    
    // Throw error with parse error context
    const reportError = new Error(`Error al generar el reporte Excel: no se pudo parsear la respuesta de error del servidor (${parseErrorMessage})`)
    if (parseError instanceof Error) {
      reportError.cause = parseError
    }
    throw reportError
  }
}

const reportsApi = {
  /**
   * Descargar reporte Excel de cacaocultores con sus fincas
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
        throw new TypeError('La respuesta del servidor no es un archivo válido')
      }
      
      // Intentar obtener el nombre del archivo desde el Content-Disposition header
      let filename = `reporte_cacaocultores_${new Date().toISOString().slice(0, 10)}.xlsx`
      const contentDisposition = response.headers['content-disposition']
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
        if (filenameMatch?.[1]) {
          filename = filenameMatch[1].replaceAll(/['"]/g, '')
        }
      }
      
      // Crear URL del objeto blob
      const url = globalThis.URL.createObjectURL(response.data)
      
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
        link.remove()
      globalThis.URL.revokeObjectURL(url)
      }, 100)
      
      return { success: true }
    } catch (error) {
      // Si el error tiene respuesta, intentar mostrar el mensaje del servidor
      if (error.response) {
        // Si la respuesta es un blob con un JSON de error, leerlo
        if (error.response.data instanceof Blob && error.response.data.type === 'application/json') {
          const errorMessage = await parseErrorBlob(error.response.data)
          throw new Error(errorMessage)
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
      const url = globalThis.URL.createObjectURL(new Blob([response.data]))
      
      // Crear elemento link y configurarlo
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `reporte_usuarios_${Date.now()}.xlsx`)
      
      // Agregar al DOM, hacer click y remover
      document.body.appendChild(link)
      link.click()
      link.remove()
      
      // Limpiar el URL del objeto
      globalThis.URL.revokeObjectURL(url)
      
      return { success: true }
    } catch (error) {
      throw error
    }
  }
}

export default reportsApi
