/**
 * Servicio de API para catálogos (Tema-Parámetro) y ubicaciones
 */
import { apiGet } from './apiClient'

const catalogosApi = {
  /**
   * Obtiene los parámetros de un tema específico
   * @param {string} codigoTema - Código del tema (ej: 'TIPO_DOC', 'SEXO')
   * @returns {Promise<Array>} - Lista de parámetros del tema
   */
  async getParametrosPorTema(codigoTema) {
    try {
      // Ruta principal: query por tema
      return await apiGet('/parametros/', { tema: codigoTema })
    } catch (error_) {
      try {
        // Fallback 1: endpoint REST por tema
        return await apiGet(`/parametros/tema/${codigoTema}/`)
      } catch (error_) {
        try {
          // Fallback 2: parámetros anidados bajo tema
          return await apiGet(`/temas/${codigoTema}/parametros/`)
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
      return await apiGet('/temas/')
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
      return await apiGet('/departamentos/')
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
      return await apiGet('/municipios/', { departamento: codigoDepartamento })
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
      const departamentos = await apiGet('/departamentos/')
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
      return await apiGet('/municipios/', { departamento: idDepartamento })
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
