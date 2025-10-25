/**
 * Servicio API para estadísticas del dashboard
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

class DashboardStatsService {
  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/dashboard`,
      headers: {
        'Content-Type': 'application/json',
      }
    })

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
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  /**
   * Obtiene estadísticas generales del dashboard
   */
  async getGeneralStats() {
    try {
      const response = await this.client.get('/stats/')
      return response.data
    } catch (error) {
      console.error('Error fetching general stats:', error)
      throw error
    }
  }

  /**
   * Obtiene datos de actividad por período
   */
  async getActivityData(period = '30') {
    try {
      const response = await this.client.get(`/activity/?period=${period}`)
      return response.data
    } catch (error) {
      console.error('Error fetching activity data:', error)
      throw error
    }
  }

  /**
   * Obtiene distribución de calidad
   */
  async getQualityDistribution() {
    try {
      const response = await this.client.get('/quality-distribution/')
      return response.data
    } catch (error) {
      console.error('Error fetching quality distribution:', error)
      throw error
    }
  }

  /**
   * Obtiene estadísticas por región
   */
  async getRegionStats() {
    try {
      const response = await this.client.get('/region-stats/')
      return response.data
    } catch (error) {
      console.error('Error fetching region stats:', error)
      throw error
    }
  }

  /**
   * Obtiene datos de tendencias
   */
  async getTrendsData(period = '30', metric = 'quality') {
    try {
      const response = await this.client.get(`/trends/?period=${period}&metric=${metric}`)
      return response.data
    } catch (error) {
      console.error('Error fetching trends data:', error)
      throw error
    }
  }

  /**
   * Obtiene usuarios más activos
   */
  async getActiveUsers(limit = 10) {
    try {
      const response = await this.client.get(`/active-users/?limit=${limit}`)
      return response.data
    } catch (error) {
      console.error('Error fetching active users:', error)
      throw error
    }
  }

  /**
   * Obtiene fincas con mejor calidad
   */
  async getTopFincas(limit = 10) {
    try {
      const response = await this.client.get(`/top-fincas/?limit=${limit}`)
      return response.data
    } catch (error) {
      console.error('Error fetching top fincas:', error)
      throw error
    }
  }

  /**
   * Obtiene usuarios recientes
   */
  async getRecentUsers(limit = 10) {
    try {
      const response = await this.client.get(`/recent-users/?limit=${limit}`)
      return response.data
    } catch (error) {
      console.error('Error fetching recent users:', error)
      throw error
    }
  }

  /**
   * Obtiene actividad reciente
   */
  async getRecentActivities(limit = 10) {
    try {
      const response = await this.client.get(`/recent-activities/?limit=${limit}`)
      return response.data
    } catch (error) {
      console.error('Error fetching recent activities:', error)
      throw error
    }
  }

  /**
   * Obtiene alertas del sistema
   */
  async getSystemAlerts() {
    try {
      const response = await this.client.get('/alerts/')
      return response.data
    } catch (error) {
      console.error('Error fetching system alerts:', error)
      throw error
    }
  }

  /**
   * Obtiene estadísticas de reportes
   */
  async getReportStats() {
    try {
      const response = await this.client.get('/report-stats/')
      return response.data
    } catch (error) {
      console.error('Error fetching report stats:', error)
      throw error
    }
  }

  /**
   * Descarta una alerta
   */
  async dismissAlert(alertId) {
    try {
      const response = await this.client.post(`/alerts/${alertId}/dismiss/`)
      return response.data
    } catch (error) {
      console.error('Error dismissing alert:', error)
      throw error
    }
  }

  /**
   * Obtiene métricas en tiempo real
   */
  async getRealtimeMetrics() {
    try {
      const response = await this.client.get('/realtime-metrics/')
      return response.data
    } catch (error) {
      console.error('Error fetching realtime metrics:', error)
      throw error
    }
  }

  /**
   * Exporta datos del dashboard
   */
  async exportDashboardData(format = 'json', period = '30') {
    try {
      const response = await this.client.get(`/export/?format=${format}&period=${period}`, {
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      console.error('Error exporting dashboard data:', error)
      throw error
    }
  }
}

// Crear instancia singleton
const dashboardStatsService = new DashboardStatsService()

export default dashboardStatsService
