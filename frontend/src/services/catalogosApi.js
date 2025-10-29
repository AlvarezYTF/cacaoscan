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
      const response = await api.get(`/api/parametros/tema/${codigoTema}/`)
      // El backend devuelve {tema: {...}, parametros: [...]}
      // Retornamos solo el array de parámetros
      return response.data.parametros || response.data
    } catch (error) {
      console.error(`Error obteniendo parámetros del tema ${codigoTema}:`, error)
      throw error
    }
  },

  /**
   * Obtiene todos los temas del sistema
   * @returns {Promise<Array>} - Lista de temas
   */
  async getTemas() {
    try {
      const response = await api.get('/api/temas/')
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
      const response = await api.get('/api/departamentos/')
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
      const response = await api.get(`/api/municipios/departamento/${codigoDepartamento}/`)
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
      const response = await api.get('/api/departamentos/')
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
      const response = await api.get(`/api/municipios/?departamento=${idDepartamento}`)
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
