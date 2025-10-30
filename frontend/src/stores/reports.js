import { defineStore } from 'pinia'
import api from '@/services/api'

export const useReportsStore = defineStore('reports', {
  state: () => ({
    reports: [],
    stats: {
      totalReports: 0,
      reportsChange: 0,
      completedReports: 0,
      completedChange: 0,
      inProgressReports: 0,
      inProgressChange: 0,
      errorReports: 0,
      errorChange: 0
    },
    pagination: {
      currentPage: 1,
      totalPages: 1,
      totalItems: 0,
      itemsPerPage: 20
    },
    loading: false,
    error: null
  }),

  getters: {
    getReportById: (state) => (id) => {
      return state.reports.find(report => report.id === id)
    },

    getReportsByType: (state) => (type) => {
      return state.reports.filter(report => report.tipo_reporte === type)
    },

    getReportsByStatus: (state) => (status) => {
      return state.reports.filter(report => report.estado === status)
    },

    getRecentReports: (state) => (limit = 5) => {
      return state.reports
        .sort((a, b) => new Date(b.fecha_solicitud) - new Date(a.fecha_solicitud))
        .slice(0, limit)
    },

    getCompletedReports: (state) => {
      return state.reports.filter(report => report.estado === 'completado')
    },

    getPendingReports: (state) => {
      return state.reports.filter(report => report.estado === 'pendiente')
    },

    getProcessingReports: (state) => {
      return state.reports.filter(report => report.estado === 'procesando')
    },

    getErrorReports: (state) => {
      return state.reports.filter(report => report.estado === 'error')
    }
  },

  actions: {
    async fetchReports(params = {}) {
      try {
        this.loading = true
        this.error = null

        const response = await api.get('/reports/', { params })
        
        this.reports = response.data.results || response.data
        this.pagination = {
          currentPage: response.data.current_page || 1,
          totalPages: response.data.total_pages || 1,
          totalItems: response.data.total_count || response.data.count || 0,
          itemsPerPage: response.data.page_size || 20
        }

        return response
      } catch (error) {
        this.error = error.response?.data?.detail || 'Error al cargar reportes'
        console.error('Error fetching reports:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchStats() {
      try {
        const response = await api.get('/reports/stats/')
        this.stats = response.data
        return response
      } catch (error) {
        console.error('Error fetching stats:', error)
        throw error
      }
    },

    async createReport(reportData) {
      try {
        this.loading = true
        this.error = null

        const response = await api.post('/reports/create/', reportData)
        
        // Agregar el nuevo reporte a la lista
        this.reports.unshift(response.data)
        
        // Actualizar estadísticas
        this.stats.totalReports += 1
        this.stats.reportsChange += 1

        return response
      } catch (error) {
        this.error = error.response?.data?.detail || 'Error al crear reporte'
        console.error('Error creating report:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateReport(id, reportData) {
      try {
        this.loading = true
        this.error = null

        const response = await api.put(`/reports/${id}/update/`, reportData)
        
        // Actualizar el reporte en la lista
        const index = this.reports.findIndex(report => report.id === id)
        if (index !== -1) {
          this.reports[index] = response.data
        }

        return response
      } catch (error) {
        this.error = error.response?.data?.detail || 'Error al actualizar reporte'
        console.error('Error updating report:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteReport(id) {
      try {
        this.loading = true
        this.error = null

        await api.delete(`/reports/${id}/delete/`)
        
        // Remover el reporte de la lista
        this.reports = this.reports.filter(report => report.id !== id)
        
        // Actualizar estadísticas
        this.stats.totalReports -= 1
        this.stats.reportsChange -= 1

        return true
      } catch (error) {
        this.error = error.response?.data?.detail || 'Error al eliminar reporte'
        console.error('Error deleting report:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async bulkDeleteReports(ids) {
      try {
        this.loading = true
        this.error = null

        await api.post('/reports/bulk-delete/', { report_ids: ids })
        
        // Remover los reportes de la lista
        this.reports = this.reports.filter(report => !ids.includes(report.id))
        
        // Actualizar estadísticas
        this.stats.totalReports -= ids.length
        this.stats.reportsChange -= ids.length

        return true
      } catch (error) {
        this.error = error.response?.data?.detail || 'Error al eliminar reportes'
        console.error('Error bulk deleting reports:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async downloadReport(id) {
      try {
        const response = await api.get(`/reports/${id}/download/`, {
          responseType: 'blob'
        })

        // Crear URL para descarga
        const blob = new Blob([response.data])
        const url = window.URL.createObjectURL(blob)
        
        // Crear enlace temporal para descarga
        const link = document.createElement('a')
        link.href = url
        
        // Obtener nombre del archivo del header
        const contentDisposition = response.headers['content-disposition']
        let filename = `reporte_${id}.pdf`
        
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="(.+)"/)
          if (filenameMatch) {
            filename = filenameMatch[1]
          }
        }
        
        link.download = filename
        document.body.appendChild(link)
        link.click()
        
        // Limpiar
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)

        return true
      } catch (error) {
        console.error('Error downloading report:', error)
        throw error
      }
    },

    async exportReports(params) {
      try {
        const response = await api.post('/reports/export/', params, {
          responseType: 'blob'
        })

        // Crear URL para descarga
        const blob = new Blob([response.data])
        const url = window.URL.createObjectURL(blob)
        
        // Crear enlace temporal para descarga
        const link = document.createElement('a')
        link.href = url
        
        // Obtener nombre del archivo del header
        const contentDisposition = response.headers['content-disposition']
        let filename = 'reportes_exportados.zip'
        
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="(.+)"/)
          if (filenameMatch) {
            filename = filenameMatch[1]
          }
        }
        
        link.download = filename
        document.body.appendChild(link)
        link.click()
        
        // Limpiar
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)

        return true
      } catch (error) {
        console.error('Error exporting reports:', error)
        throw error
      }
    },

    async getReportPreview(id) {
      try {
        const response = await api.get(`/reports/${id}/preview/`)
        return response
      } catch (error) {
        console.error('Error getting report preview:', error)
        throw error
      }
    },

    async fetchUsers() {
      try {
        const response = await api.get('/users/')
        return response
      } catch (error) {
        console.error('Error fetching users:', error)
        throw error
      }
    },

    async fetchFincas() {
      try {
        const response = await api.get('/api/v1/fincas/')
        return response
      } catch (error) {
        console.error('Error fetching fincas:', error)
        throw error
      }
    },

    async fetchLotesByFinca(fincaId) {
      try {
        const response = await api.get(`/api/v1/fincas/${fincaId}/lotes/`)
        return response
      } catch (error) {
        console.error('Error fetching lotes:', error)
        throw error
      }
    },

    async fetchReportTypes() {
      try {
        const response = await api.get('/reports/types/')
        return response
      } catch (error) {
        console.error('Error fetching report types:', error)
        throw error
      }
    },

    async fetchReportFormats() {
      try {
        const response = await api.get('/reports/formats/')
        return response
      } catch (error) {
        console.error('Error fetching report formats:', error)
        throw error
      }
    },

    async scheduleReport(id, scheduleData) {
      try {
        const response = await api.post(`/reports/${id}/schedule/`, scheduleData)
        
        // Actualizar el reporte en la lista
        const index = this.reports.findIndex(report => report.id === id)
        if (index !== -1) {
          this.reports[index] = { ...this.reports[index], ...response.data }
        }

        return response
      } catch (error) {
        console.error('Error scheduling report:', error)
        throw error
      }
    },

    async unscheduleReport(id) {
      try {
        const response = await api.delete(`/reports/${id}/schedule/`)
        
        // Actualizar el reporte en la lista
        const index = this.reports.findIndex(report => report.id === id)
        if (index !== -1) {
          this.reports[index] = { ...this.reports[index], ...response.data }
        }

        return response
      } catch (error) {
        console.error('Error unscheduling report:', error)
        throw error
      }
    },

    async regenerateReport(id) {
      try {
        this.loading = true
        this.error = null

        const response = await api.post(`/reports/${id}/regenerate/`)
        
        // Actualizar el reporte en la lista
        const index = this.reports.findIndex(report => report.id === id)
        if (index !== -1) {
          this.reports[index] = response.data
        }

        return response
      } catch (error) {
        this.error = error.response?.data?.detail || 'Error al regenerar reporte'
        console.error('Error regenerating report:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    addReport(report) {
      this.reports.unshift(report)
      this.stats.totalReports += 1
      this.stats.reportsChange += 1
    },

    updateReportInList(report) {
      const index = this.reports.findIndex(r => r.id === report.id)
      if (index !== -1) {
        this.reports[index] = report
      }
    },

    removeReport(id) {
      this.reports = this.reports.filter(report => report.id !== id)
      this.stats.totalReports -= 1
      this.stats.reportsChange -= 1
    },

    clearError() {
      this.error = null
    },

    reset() {
      this.reports = []
      this.stats = {
        totalReports: 0,
        reportsChange: 0,
        completedReports: 0,
        completedChange: 0,
        inProgressReports: 0,
        inProgressChange: 0,
        errorReports: 0,
        errorChange: 0
      }
      this.pagination = {
        currentPage: 1,
        totalPages: 1,
        totalItems: 0,
        itemsPerPage: 20
      }
      this.loading = false
      this.error = null
    }
  }
})
