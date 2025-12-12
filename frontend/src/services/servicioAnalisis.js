/**
 * Servicio de API para análisis en CacaoScan
 * Maneja todas las llamadas HTTP relacionadas con análisis
 */

import api from './api'
import { normalizeResponse } from '@/utils/apiResponse'

const servicioAnalisis = {
  /**
   * Obtener lista de análisis
   */
  async getAnalisis(params = {}) {
    try {
      const response = await api.get('/analisis/', { params })
      return normalizeResponse(response.data)
    } catch (error) {
      throw error
    }
  },

  /**
   * Crear un nuevo análisis
   */
  async createAnalisis(analisisData) {
    try {
      const response = await api.post('/analisis/', analisisData)
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * Obtener un análisis específico por ID
   */
  async getAnalisisById(analisisId) {
    try {
      const response = await api.get(`/analisis/${analisisId}/`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * Actualizar un análisis
   */
  async updateAnalisis(analisisId, analisisData) {
    try {
      const response = await api.put(`/analisis/${analisisId}/`, analisisData)
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * Eliminar un análisis
   */
  async deleteAnalisis(analisisId) {
    try {
      const response = await api.delete(`/analisis/${analisisId}/`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * Obtener estadísticas de análisis
   */
  async getAnalisisStats() {
    try {
      const response = await api.get('/analisis/stats/')
      return response.data
    } catch (error) {
      throw error
    }
  }
}

export default servicioAnalisis
