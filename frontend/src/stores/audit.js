import { defineStore } from 'pinia'
import api from '@/services/api'
import { downloadFileFromResponse } from '@/utils/fileExportUtils'

export const useAuditStore = defineStore('audit', {
  state: () => ({
    activityLogs: [],
    loginHistory: [],
    stats: {
      activity_log: {
        total_activities: 0,
        activities_today: 0,
        activities_by_action: {},
        activities_by_model: {},
        top_active_users: []
      },
      login_history: {
        total_logins: 0,
        successful_logins: 0,
        failed_logins: 0,
        success_rate: 0,
        login_stats_by_day: [],
        top_ips: [],
        avg_session_duration_minutes: 0
      }
    },
    pagination: {
      currentPage: 1,
      totalPages: 1,
      totalItems: 0,
      itemsPerPage: 50
    },
    loading: false,
    error: null
  }),

  getters: {
    getActivityLogById: (state) => (id) => {
      return state.activityLogs.find(log => log.id === id)
    },

    getLoginHistoryById: (state) => (id) => {
      return state.loginHistory.find(login => login.id === id)
    },

    getRecentActivityLogs: (state) => (limit = 10) => {
      const sorted = [...state.activityLogs].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      return sorted.slice(0, limit)
    },

    getRecentLogins: (state) => (limit = 10) => {
      const sorted = [...state.loginHistory].sort((a, b) => new Date(b.login_time) - new Date(a.login_time))
      return sorted.slice(0, limit)
    },

    getFailedLogins: (state) => {
      return state.loginHistory.filter(login => !login.success)
    },

    getSuccessfulLogins: (state) => {
      return state.loginHistory.filter(login => login.success)
    },

    getActivityLogsByUser: (state) => (username) => {
      return state.activityLogs.filter(log => log.usuario === username)
    },

    getLoginsByUser: (state) => (username) => {
      return state.loginHistory.filter(login => login.usuario === username)
    },

    getActivityLogsByAction: (state) => (action) => {
      return state.activityLogs.filter(log => log.accion === action)
    },

    getActivityLogsByModel: (state) => (model) => {
      return state.activityLogs.filter(log => log.modelo === model)
    },

    getLoginsByIP: (state) => (ip) => {
      return state.loginHistory.filter(login => login.ip_address === ip)
    }
  },

  actions: {
    async fetchActivityLogs(params = {}) {
      try {
        this.loading = true
        this.error = null

        const response = await api.get('/audit/activity-logs/', { params })
        
        this.activityLogs = response.data.results || response.data
        this.pagination = {
          currentPage: response.data.page || 1,
          totalPages: response.data.total_pages || 1,
          totalItems: response.data.count || 0,
          itemsPerPage: response.data.page_size || 50
        }

        return response
      } catch (error) {
        this.error = error.response?.data?.detail || 'Error al cargar logs de actividad'
        console.error('Error fetching activity logs:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchLoginHistory(params = {}) {
      try {
        this.loading = true
        this.error = null

        const response = await api.get('/audit/login-history/', { params })
        
        this.loginHistory = response.data.results || response.data
        this.pagination = {
          currentPage: response.data.page || 1,
          totalPages: response.data.total_pages || 1,
          totalItems: response.data.count || 0,
          itemsPerPage: response.data.page_size || 50
        }

        return response
      } catch (error) {
        this.error = error.response?.data?.detail || 'Error al cargar historial de logins'
        console.error('Error fetching login history:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchStats() {
      try {
        const response = await api.get('/audit/stats/')
        this.stats = response.data
        return response
      } catch (error) {
        console.error('Error fetching audit stats:', error)
        throw error
      }
    },

    async exportAuditData(params) {
      try {
        this.loading = true
        this.error = null

        const response = await api.post('/audit/export/', params, {
          responseType: 'blob'
        })

        downloadFileFromResponse(response, 'auditoria_exportada.xlsx')

        return true
      } catch (error) {
        this.error = error.response?.data?.detail || 'Error al exportar datos de auditoría'
        console.error('Error exporting audit data:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async getActivityLogDetails(id) {
      try {
        const response = await api.get(`/audit/activity-logs/${id}/`)
        return response
      } catch (error) {
        console.error('Error getting activity log details:', error)
        throw error
      }
    },

    async getLoginHistoryDetails(id) {
      try {
        const response = await api.get(`/audit/login-history/${id}/`)
        return response
      } catch (error) {
        console.error('Error getting login history details:', error)
        throw error
      }
    },

    async getAuditSummary(params = {}) {
      try {
        const response = await api.get('/audit/summary/', { params })
        return response
      } catch (error) {
        console.error('Error getting audit summary:', error)
        throw error
      }
    },

    async getSecurityAlerts() {
      try {
        const response = await api.get('/audit/security-alerts/')
        return response
      } catch (error) {
        console.error('Error getting security alerts:', error)
        throw error
      }
    },

    async getSuspiciousActivity() {
      try {
        const response = await api.get('/audit/suspicious-activity/')
        return response
      } catch (error) {
        console.error('Error getting suspicious activity:', error)
        throw error
      }
    },

    async getAuditReport(params = {}) {
      try {
        const response = await api.post('/audit/generate-report/', params)
        return response
      } catch (error) {
        console.error('Error generating audit report:', error)
        throw error
      }
    },

    async clearOldLogs(daysToKeep = 90) {
      try {
        const response = await api.post('/audit/clear-old-logs/', {
          days_to_keep: daysToKeep
        })
        return response
      } catch (error) {
        console.error('Error clearing old logs:', error)
        throw error
      }
    },

    async getAuditDashboard() {
      try {
        const response = await api.get('/audit/dashboard/')
        return response
      } catch (error) {
        console.error('Error getting audit dashboard:', error)
        throw error
      }
    },

    addActivityLog(log) {
      this.activityLogs.unshift(log)
    },

    addLoginHistory(login) {
      this.loginHistory.unshift(login)
    },

    updateActivityLog(log) {
      const index = this.activityLogs.findIndex(l => l.id === log.id)
      if (index !== -1) {
        this.activityLogs[index] = log
      }
    },

    updateLoginHistory(login) {
      const index = this.loginHistory.findIndex(l => l.id === login.id)
      if (index !== -1) {
        this.loginHistory[index] = login
      }
    },

    removeActivityLog(id) {
      this.activityLogs = this.activityLogs.filter(log => log.id !== id)
    },

    removeLoginHistory(id) {
      this.loginHistory = this.loginHistory.filter(login => login.id !== id)
    },

    clearError() {
      this.error = null
    },

    reset() {
      this.activityLogs = []
      this.loginHistory = []
      this.stats = {
        activity_log: {
          total_activities: 0,
          activities_today: 0,
          activities_by_action: {},
          activities_by_model: {},
          top_active_users: []
        },
        login_history: {
          total_logins: 0,
          successful_logins: 0,
          failed_logins: 0,
          success_rate: 0,
          login_stats_by_day: [],
          top_ips: [],
          avg_session_duration_minutes: 0
        }
      }
      this.pagination = {
        currentPage: 1,
        totalPages: 1,
        totalItems: 0,
        itemsPerPage: 50
      }
      this.loading = false
      this.error = null
    }
  }
})
