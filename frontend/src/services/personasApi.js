/**
 * Servicio API para gestión de personas
 * Usa apiClient para reducir duplicación de código
 */
import { apiGet, apiPost, apiPatch } from './apiClient'

export const personasApi = {
  /**
   * Obtener el perfil de la persona del usuario autenticado
   */
  async getPerfil() {
    return await apiGet('/api/personas/perfil/')
  },

  /**
   * Crear el perfil de persona para un usuario existente
   * @param {Object} data - Datos de la persona
   */
  async crearPerfil(data) {
    return await apiPost('/api/personas/perfil/', data)
  },

  /**
   * Actualizar el perfil de la persona del usuario autenticado
   * @param {Object} data - Datos a actualizar (excepto email)
   */
  async actualizarPerfil(data) {
    return await apiPatch('/api/personas/perfil/', data)
  },

  // Admin: obtener persona por user_id
  async getPersonaByUserId(userId) {
    return await apiGet(`/personas/admin/${userId}/`)
  },

  // Admin: actualizar/crear persona por user_id
  async updatePersonaByUserId(userId, data) {
    return await apiPatch(`/personas/admin/${userId}/`, data)
  }
}

export default personasApi

