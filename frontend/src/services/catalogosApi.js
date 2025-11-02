/**
 * Servicio de API para catálogos (Tema-Parámetro) y ubicaciones
 */
import api from './api'

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
      return response.data
    } catch (errorPrimario) {
      console.warn(`[catalogosApi] Fallback 1 para tema ${codigoTema} tras error:`, errorPrimario?.response?.status)
      try {
        // Fallback 1: endpoint REST por tema
        const respAlt1 = await api.get(`/parametros/tema/${codigoTema}/`)
        return respAlt1.data
      } catch (errorSecundario) {
        console.warn(`[catalogosApi] Fallback 2 para tema ${codigoTema} tras error:`, errorSecundario?.response?.status)
        try {
          // Fallback 2: parámetros anidados bajo tema
          const respAlt2 = await api.get(`/temas/${codigoTema}/parametros/`)
          return respAlt2.data
        } catch (errorTerciario) {
          console.error(`Error obteniendo parámetros del tema ${codigoTema}:`, errorTerciario)
          throw errorTerciario
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
      const response = await api.get('/temas/')
      return response.data
    } catch (error) {
      console.error('Error obteniendo temas:', error)
      throw error
    }
  },

  /**
   * Obtiene todos los departamentos de Colombia
   * @returns {Promise<Array>} - Lista de departamentos
   */
  async getDepartamentos() {
    try {
      const response = await api.get('/departamentos/')
      return response.data
    } catch (error) {
      console.error('Error obteniendo departamentos:', error)
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
      const response = await api.get(`/municipios/`, { params: { departamento: codigoDepartamento } })
      return response.data
    } catch (error) {
      console.error(`Error obteniendo municipios del departamento ${codigoDepartamento}:`, error)
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
      const response = await api.get('/departamentos/')
      return response.data.find(dept => dept.codigo === codigo)
    } catch (error) {
      console.error(`Error obteniendo departamento ${codigo}:`, error)
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
      return response.data
    } catch (error) {
      console.error(`Error obteniendo municipios del departamento ${idDepartamento}:`, error)
      throw error
    }
  },

  // Alias para compatibilidad
  getParametrosByTema(codigoTema) {
    return this.getParametrosPorTema(codigoTema)
  }
}

export default catalogosApi
