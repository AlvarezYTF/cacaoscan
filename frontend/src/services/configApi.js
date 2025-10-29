import api from './api'

const configApi = {
  // Obtener configuración general
  async getGeneralConfig() {
    try {
      const response = await api.get('/config/general/')
      return response.data
    } catch (error) {
      // Error 500 o 403 esperado - devolver objeto vacío en lugar de lanzar
      if (error.response?.status === 500 || error.response?.status === 403) {
        return null
      }
      console.error('Error obteniendo configuración general:', error)
      throw error
    }
  },

  // Guardar configuración general
  async saveGeneralConfig(data) {
    try {
      const response = await api.put('/config/general/', data)
      return response.data
    } catch (error) {
      console.error('Error guardando configuración general:', error)
      throw error
    }
  },

  // Obtener configuración de seguridad
  async getSecurityConfig() {
    try {
      const response = await api.get('/config/security/')
      return response.data
    } catch (error) {
      // Error 403 esperado - devolver objeto vacío en lugar de lanzar
      if (error.response?.status === 403 || error.response?.status === 500) {
        return null
      }
      console.error('Error obteniendo configuración de seguridad:', error)
      throw error
    }
  },

  // Guardar configuración de seguridad
  async saveSecurityConfig(data) {
    try {
      const response = await api.put('/config/security/', data)
      return response.data
    } catch (error) {
      console.error('Error guardando configuración de seguridad:', error)
      throw error
    }
  },

  // Obtener configuración de modelos ML
  async getMLConfig() {
    try {
      const response = await api.get('/config/ml/')
      return response.data
    } catch (error) {
      // Error 403 esperado - devolver objeto vacío en lugar de lanzar
      if (error.response?.status === 403 || error.response?.status === 500) {
        return null
      }
      console.error('Error obteniendo configuración ML:', error)
      throw error
    }
  },

  // Guardar configuración de modelos ML
  async saveMLConfig(data) {
    try {
      const response = await api.put('/config/ml/', data)
      return response.data
    } catch (error) {
      console.error('Error guardando configuración ML:', error)
      throw error
    }
  },

  // Obtener configuración del sistema
  async getSystemConfig() {
    try {
      const response = await api.get('/config/system/')
      return response.data
    } catch (error) {
      // Si falla, devolver valores por defecto en lugar de lanzar
      if (error.response?.status === 500 || error.response?.status === 403) {
        return {
          version: '1.0.0',
          server_status: 'online',
          backend_version: '4.2.7',
          frontend_version: '3.5.3',
          database: 'PostgreSQL 16'
        }
      }
      console.error('Error obteniendo configuración del sistema:', error)
      throw error
    }
  }
}

export default configApi

