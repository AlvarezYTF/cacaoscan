/**
 * Servicio de API para catálogos (Tema-Parámetro) y ubicaciones
 */
import api from './api'
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
      const response = await api.get('/parametros/', { params: { tema: codigoTema } })
      const data = response.data
      // Si es paginado, retornar results, sino retornar directamente
      return Array.isArray(data) ? data : (data.results || data)
    } catch (error_) {
      try {
        // Fallback 1: endpoint REST por tema
        const response = await api.get(`/parametros/tema/${codigoTema}/`, { params: {} })
        const data = response.data
        return data.parametros || data
      } catch (error_) {
        try {
          // Fallback 2: parámetros anidados bajo tema (necesita buscar tema por código primero)
          const temasResponse = await api.get('/temas/', { params: {} })
          const temas = temasResponse.data
          const temasArray = Array.isArray(temas) ? temas : (temas.results || [])
          const tema = temasArray.find(t => t.codigo === codigoTema)
          if (!tema) {
            throw new Error(`Tema ${codigoTema} no encontrado`)
          }
          const response = await api.get(`/temas/${tema.id}/parametros/`, { params: {} })
          const data = response.data
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
      const response = await api.get('/temas/', { params: {} })
      const data = response.data
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
      const response = await api.get('/departamentos/', { params: {} })
      const data = response.data
      return Array.isArray(data) ? data : (data.results || data)
    } catch (error) {
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
      const response = await api.get('/municipios/', { params: { departamento: codigoDepartamento } })
      const data = response.data
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
      // Handle different response formats: array, {results: []}, or {data: []}
      let departamentos = null
      if (Array.isArray(data)) {
        departamentos = data
      } else if (Array.isArray(data.results)) {
        departamentos = data.results
      } else if (Array.isArray(data.data)) {
        departamentos = data.data
      } else {
        departamentos = []
      }
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
      const response = await api.get('/municipios/', { params: { departamento: idDepartamento } })
      const data = response.data
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
