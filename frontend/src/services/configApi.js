/**
 * Servicio API para gestión de configuración
 * Usa apiClient para reducir duplicación de código
 * Mantiene lógica especial de manejo de errores para códigos 403/500
 */
import { apiGet, apiPut } from './apiClient'

const CONFIG_BASE = '/config'

/**
 * Helper para manejar errores esperados (403/500) devolviendo null
 */
const handleExpectedError = (error, defaultReturn = null) => {
  if (error.response?.status === 500 || error.response?.status === 403) {
    return defaultReturn
  }
  console.error('Error en configuración:', error)
  throw error
}

const configApi = {
  // Obtener configuración general
  async getGeneralConfig() {
    try {
      return await apiGet(`${CONFIG_BASE}/general/`)
    } catch (error) {
      return handleExpectedError(error, null)
    }
  },

  // Guardar configuración general
  async saveGeneralConfig(data) {
    return await apiPut(`${CONFIG_BASE}/general/`, data)
  },

  // Obtener configuración de seguridad
  async getSecurityConfig() {
    try {
      return await apiGet(`${CONFIG_BASE}/security/`)
    } catch (error) {
      return handleExpectedError(error, null)
    }
  },

  // Guardar configuración de seguridad
  async saveSecurityConfig(data) {
    return await apiPut(`${CONFIG_BASE}/security/`, data)
  },

  // Obtener configuración de modelos ML
  async getMLConfig() {
    try {
      return await apiGet(`${CONFIG_BASE}/ml/`)
    } catch (error) {
      return handleExpectedError(error, null)
    }
  },

  // Guardar configuración de modelos ML
  async saveMLConfig(data) {
    return await apiPut(`${CONFIG_BASE}/ml/`, data)
  },

  // Obtener configuración del sistema
  async getSystemConfig() {
    try {
      return await apiGet(`${CONFIG_BASE}/system/`)
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

