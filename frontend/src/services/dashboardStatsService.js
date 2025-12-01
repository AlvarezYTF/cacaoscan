/**
 * Servicio API para estadísticas del dashboard
 * Usa apiClient para reducir duplicación de código
 */
import { apiGet, apiPost } from './apiClient'

const DASHBOARD_BASE = '/api/dashboard'

class DashboardStatsService {
  constructor() {
    try {
      this.client = axios.create({
        baseURL: `${API_BASE_URL}/dashboard`,
        headers: {
          'Content-Type': 'application/json',
        }
      })

      // Verificar que el cliente se creó correctamente
      if (!this.client || !this.client.interceptors) {
        throw new Error('Failed to create axios instance')
      }

      // Interceptor para agregar token de autenticación
      this.client.interceptors.request.use((config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      })

      // Interceptor para manejar errores
      this.client.interceptors.response.use(
        (response) => response,
        (error) => {
          if (error.response?.status === 401) {
            localStorage.removeItem('access_token')
            if (typeof globalThis !== 'undefined' && globalThis.location) {
              globalThis.location.href = '/login'
            }
          }
          return Promise.reject(error)
        }
      )
    } catch (error) {
      console.error('Error initializing DashboardStatsService:', error)
      // Crear un cliente mock para evitar errores en tests
      this.client = {
        get: () => Promise.reject(new Error('Service not initialized')),
        post: () => Promise.reject(new Error('Service not initialized')),
        interceptors: {
          request: { use: () => {} },
          response: { use: () => {} }
        }
      }
    }
  }

  /**
   * Obtiene estadísticas generales del dashboard
   */
  async getGeneralStats() {
    return await apiGet(`${DASHBOARD_BASE}/stats/`)
  }

  /**
   * Obtiene datos de actividad por período
   */
  async getActivityData(period = '30') {
    return await apiGet(`${DASHBOARD_BASE}/activity/`, { period })
  }

  /**
   * Obtiene distribución de calidad
   */
  async getQualityDistribution() {
    return await apiGet(`${DASHBOARD_BASE}/quality-distribution/`)
  }

  /**
   * Obtiene estadísticas por región
   */
  async getRegionStats() {
    return await apiGet(`${DASHBOARD_BASE}/region-stats/`)
  }

  /**
   * Obtiene datos de tendencias
   */
  async getTrendsData(period = '30', metric = 'quality') {
    return await apiGet(`${DASHBOARD_BASE}/trends/`, { period, metric })
  }

  /**
   * Obtiene usuarios más activos
   */
  async getActiveUsers(limit = 10) {
    return await apiGet(`${DASHBOARD_BASE}/active-users/`, { limit })
  }

  /**
   * Obtiene fincas con mejor calidad
   */
  async getTopFincas(limit = 10) {
    return await apiGet(`${DASHBOARD_BASE}/top-fincas/`, { limit })
  }

  /**
   * Obtiene usuarios recientes
   */
  async getRecentUsers(limit = 10) {
    return await apiGet(`${DASHBOARD_BASE}/recent-users/`, { limit })
  }

  /**
   * Obtiene actividad reciente
   */
  async getRecentActivities(limit = 10) {
    return await apiGet(`${DASHBOARD_BASE}/recent-activities/`, { limit })
  }

  /**
   * Obtiene alertas del sistema
   */
  async getSystemAlerts() {
    return await apiGet(`${DASHBOARD_BASE}/alerts/`)
  }

  /**
   * Obtiene estadísticas de reportes
   */
  async getReportStats() {
    return await apiGet(`${DASHBOARD_BASE}/report-stats/`)
  }

  /**
   * Descarta una alerta
   */
  async dismissAlert(alertId) {
    return await apiPost(`${DASHBOARD_BASE}/alerts/${alertId}/dismiss/`)
  }

  /**
   * Obtiene métricas en tiempo real
   */
  async getRealtimeMetrics() {
    return await apiGet(`${DASHBOARD_BASE}/realtime-metrics/`)
  }

  /**
   * Exporta datos del dashboard
   */
  async exportDashboardData(format = 'json', period = '30') {
    return await apiGet(`${DASHBOARD_BASE}/export/`, { format, period }, { responseType: 'blob' })
  }
}

// Crear instancia singleton
const dashboardStatsService = new DashboardStatsService()

export default dashboardStatsService
