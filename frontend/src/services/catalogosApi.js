/**
 * Servicio de API para catálogos (Tema-Parámetro) y ubicaciones
 */
import { getApiBaseUrlWithPath } from '@/utils/apiConfig'

const catalogosApi = {
  /**
   * Obtiene los parámetros de un tema específico
   * @param {string} codigoTema - Código del tema (ej: 'TIPO_DOC', 'SEXO')
   * @returns {Promise<Array>} - Lista de parámetros del tema
   */
  async getParametrosPorTema(codigoTema) {
    try {
      // Ruta principal: query por tema
      const baseUrl = getApiBaseUrlWithPath()
      const url = `${baseUrl}/parametros/?tema=${codigoTema}`
      console.log('[catalogosApi] getParametrosPorTema - URL:', url)
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      console.log('[catalogosApi] getParametrosPorTema - Response status:', response.status)
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('[catalogosApi] getParametrosPorTema - Error response:', errorText)
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }
      
      const data = await response.json()
      console.log('[catalogosApi] getParametrosPorTema - Data recibida:', data)
      
      // Si es paginado, retornar results, sino retornar directamente
      const result = Array.isArray(data) ? data : (data.results || data)
      console.log('[catalogosApi] getParametrosPorTema - Resultado final:', result)
      return result
    } catch (error_) {
      try {
        // Fallback 1: endpoint REST por tema
        const baseUrl = getApiBaseUrlWithPath()
        const response = await fetch(`${baseUrl}/parametros/tema/${codigoTema}/`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }
        const data = await response.json()
        return data.parametros || data
      } catch (error_) {
        try {
          // Fallback 2: parámetros anidados bajo tema (necesita buscar tema por código primero)
          const baseUrl = getApiBaseUrlWithPath()
          const temasResponse = await fetch(`${baseUrl}/temas/`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json'
            }
          })
          if (!temasResponse.ok) {
            throw new Error(`HTTP ${temasResponse.status}`)
          }
          const temas = await temasResponse.json()
          const temasArray = Array.isArray(temas) ? temas : (temas.results || [])
          const tema = temasArray.find(t => t.codigo === codigoTema)
          if (!tema) {
            throw new Error(`Tema ${codigoTema} no encontrado`)
          }
          const response = await fetch(`${baseUrl}/temas/${tema.id}/parametros/`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json'
            }
          })
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}`)
          }
          const data = await response.json()
          return Array.isArray(data) ? data : (data.results || data)
        } catch (error_) {
          throw error_
        }
      }
    }
  },

  /**
   * Obtiene todos los temas del sistema
   * @returns {Promise<Array>} - Lista de temas
   */
  async getTemas() {
    try {
      const baseUrl = getApiBaseUrlWithPath()
      const response = await fetch(`${baseUrl}/temas/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const data = await response.json()
      return Array.isArray(data) ? data : (data.results || data)
    } catch (error) {
      throw error
    }
  },

  /**
   * Obtiene todos los departamentos de Colombia
   * @returns {Promise<Array>} - Lista de departamentos
   */
  async getDepartamentos() {
    try {
      const baseUrl = getApiBaseUrlWithPath()
      const url = `${baseUrl}/departamentos/`
      console.log('[catalogosApi] getDepartamentos - URL:', url)
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      console.log('[catalogosApi] getDepartamentos - Response status:', response.status)
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('[catalogosApi] getDepartamentos - Error response:', errorText)
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }
      
      const data = await response.json()
      console.log('[catalogosApi] getDepartamentos - Data recibida:', data)
      
      const result = Array.isArray(data) ? data : (data.results || data)
      console.log('[catalogosApi] getDepartamentos - Resultado final:', result?.length || 0, 'departamentos')
      return result
    } catch (error) {
      console.error('[catalogosApi] getDepartamentos - Error:', error)
      throw error
    }
  },

  /**
   * Obtiene los municipios de un departamento específico
   * @param {string} codigoDepartamento - Código del departamento (ej: '05' para Antioquia)
   * @returns {Promise<Array>} - Lista de municipios
   */
  async getMunicipiosPorDepartamento(codigoDepartamento) {
    try {
      const baseUrl = getApiBaseUrlWithPath()
      const response = await fetch(`${baseUrl}/municipios/?departamento=${codigoDepartamento}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const data = await response.json()
      return Array.isArray(data) ? data : (data.results || data)
    } catch (error) {
      throw error
    }
  },

  /**
   * Obtiene un departamento por su código
   * @param {string} codigo - Código del departamento
   * @returns {Promise<Object>} - Departamento
   */
  async getDepartamentoPorCodigo(codigo) {
    try {
      const baseUrl = getApiBaseUrlWithPath()
      const response = await fetch(`${baseUrl}/departamentos/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const data = await response.json()
      const departamentos = Array.isArray(data) ? data : (data.results || data)
      return departamentos.find(dept => dept.codigo === codigo)
    } catch (error) {
      throw error
    }
  },

  /**
   * Obtiene los municipios de un departamento por ID
   * @param {number} idDepartamento - ID del departamento
   * @returns {Promise<Array>} - Lista de municipios
   */
  async getMunicipiosByDepartamento(idDepartamento) {
    try {
      const baseUrl = getApiBaseUrlWithPath()
      const response = await fetch(`${baseUrl}/municipios/?departamento=${idDepartamento}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const data = await response.json()
      return Array.isArray(data) ? data : (data.results || data)
    } catch (error) {
      throw error
    }
  },

  // Alias para compatibilidad
  getParametrosByTema(codigoTema) {
    return this.getParametrosPorTema(codigoTema)
  }
}

export default catalogosApi
