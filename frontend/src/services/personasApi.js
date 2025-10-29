import api from './api'

export const personasApi = {
  /**
   * Obtener el perfil de la persona del usuario autenticado
   */
  async getPerfil() {
    try {
      const response = await api.get('/api/personas/perfil/')
      return response.data
    } catch (error) {
      console.error('Error obteniendo perfil:', error)
      throw error
    }
  },

  /**
   * Crear el perfil de persona para un usuario existente
   * @param {Object} data - Datos de la persona
   */
  async crearPerfil(data) {
    try {
      const response = await api.post('/api/personas/perfil/', data)
      return response.data
    } catch (error) {
      console.error('Error creando perfil:', error)
      throw error
    }
  },

  /**
   * Actualizar el perfil de la persona del usuario autenticado
   * @param {Object} data - Datos a actualizar (excepto email)
   */
  async actualizarPerfil(data) {
    try {
      const response = await api.patch('/api/personas/perfil/', data)
      return response.data
    } catch (error) {
      console.error('Error actualizando perfil:', error)
      throw error
    }
  }
}

export default personasApi

