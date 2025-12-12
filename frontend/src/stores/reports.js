/**
 * Pinia store for reports management
 * Simplified to use reportsService for API calls
 * Focuses on state management and caching
 */
import { defineStore } from 'pinia'
import reportsService from '@/services/reportsService'
import { downloadBlob } from '@/utils/fileExportUtils'
import { handleApiError } from '@/services/apiErrorHandler'

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
      const sorted = [...state.reports].sort((a, b) => {
        const dateA = new Date(a.fecha_solicitud || a.created_at || 0)
        const dateB = new Date(b.fecha_solicitud || b.created_at || 0)
        return dateB - dateA
      })
      return sorted.slice(0, limit)
    },

    getCompletedReports: (state) => {
      return state.reports.filter(report => report.estado === 'completado')
    },

    getPendingReports: (state) => {
      return state.reports.filter(report => report.estado === 'pendiente')
    },

    getProcessingReports: (state) => {
      return state.reports.filter(report => report.estado === 'procesando' || report.estado === 'generando')
    },

    getErrorReports: (state) => {
      return state.reports.filter(report => report.estado === 'error' || report.estado === 'fallido')
    }
  },

  actions: {
    /**
     * Fetch reports list with filters and pagination
     * @param {Object} params - Filter and pagination parameters
     */
    async fetchReports(params = {}) {
      try {
        this.loading = true
        this.error = null

        // Extract pagination and filters from params
        const { page: pageParam, page_size: pageSizeParam, itemsPerPage: itemsPerPageParam, ...filters } = params
        
        const page = pageParam || this.pagination.currentPage
        const pageSize = pageSizeParam || itemsPerPageParam || this.pagination.itemsPerPage
        
        const response = await reportsService.getReports(filters, page, pageSize)
        
        this.reports = response.results || []
        this.pagination = {
          currentPage: response.page || page,
          totalPages: response.total_pages || 1,
          totalItems: response.count || 0,
          itemsPerPage: response.page_size || pageSize
        }

        return response
      } catch (error) {
        const errorInfo = handleApiError(error, { logError: true })
        this.error = errorInfo.message
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Fetch reports statistics
     */
    async fetchStats() {
      try {
        const response = await reportsService.getReportsStats()
        this.stats = {
          totalReports: response.total_reports || 0,
          reportsChange: response.reports_change || 0,
          completedReports: response.completed_reports || 0,
          completedChange: response.completed_change || 0,
          inProgressReports: response.in_progress_reports || 0,
          inProgressChange: response.in_progress_change || 0,
          errorReports: response.error_reports || 0,
          errorChange: response.error_change || 0
        }
        return response
      } catch (error) {
        handleApiError(error, { logError: true })
        throw error
      }
    },

    /**
     * Create a new report
     * @param {Object} reportData - Report data from form
     */
    async createReport(reportData) {
      try {
        this.loading = true
        this.error = null

        const report = await reportsService.createReport(reportData)
        
        // Add new report to list
        this.reports.unshift(report)
        
        // Update statistics
        this.stats.totalReports += 1
        this.stats.reportsChange += 1

        return report
      } catch (error) {
        const errorInfo = handleApiError(error, { logError: true })
        this.error = errorInfo.message
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Update report (if supported by API)
     * @param {number} id - Report ID
     * @param {Object} reportData - Report data to update
     */
    async updateReport(id, reportData) {
      try {
        this.loading = true
        this.error = null

        // If update is not supported, just update in local state
        const index = this.reports.findIndex(report => report.id === id)
        if (index !== -1) {
          this.reports[index] = { ...this.reports[index], ...reportData }
        }

        return this.reports[index]
      } catch (error) {
        const errorInfo = handleApiError(error, { logError: true })
        this.error = errorInfo.message
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Delete a report
     * @param {number} id - Report ID
     */
    async deleteReport(id) {
      try {
        this.loading = true
        this.error = null

        await reportsService.deleteReport(id)
        
        // Remove report from list
        this.reports = this.reports.filter(report => report.id !== id)
        
        // Update statistics
        this.stats.totalReports -= 1
        this.stats.reportsChange -= 1

        return true
      } catch (error) {
        const errorInfo = handleApiError(error, { logError: true })
        this.error = errorInfo.message
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Bulk delete reports
     * @param {Array<number>} ids - Array of report IDs
     */
    async bulkDeleteReports(ids) {
      try {
        this.loading = true
        this.error = null

        // Delete reports one by one (or implement bulk endpoint if available)
        await Promise.all(ids.map(id => reportsService.deleteReport(id)))
        
        // Remove reports from list
        this.reports = this.reports.filter(report => !ids.includes(report.id))
        
        // Update statistics
        this.stats.totalReports -= ids.length
        this.stats.reportsChange -= ids.length

        return true
      } catch (error) {
        const errorInfo = handleApiError(error, { logError: true })
        this.error = errorInfo.message
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Download a report file
     * @param {number} id - Report ID
     */
    async downloadReport(id) {
      try {
        const response = await reportsService.downloadReport(id)
        
        // Get filename from Content-Disposition header or use default
        const contentDisposition = response.headers?.get('Content-Disposition')
        let filename = `reporte_${id}.pdf`
        
        if (contentDisposition) {
          // Try to extract filename from Content-Disposition header
          const filenameMatch = contentDisposition.match(/filename="(.+)"/) || contentDisposition.match(/filename=([^;]+)/)
          if (filenameMatch) {
            filename = filenameMatch[1].trim()
            // Remove quotes if present
            filename = filename.replace(/^["']|["']$/g, '')
          }
        }
        
        const blob = await response.blob()
        
        // Convert Headers object to plain object for downloadBlob
        const headersObj = {}
        if (response.headers) {
          response.headers.forEach((value, key) => {
            headersObj[key.toLowerCase()] = value
          })
        }
        
        downloadBlob(blob, filename, headersObj)

        return true
      } catch (error) {
        handleApiError(error, { logError: true })
        throw error
      }
    },

    /**
     * Get report details
     * @param {number} id - Report ID
     */
    async getReportDetails(id) {
      try {
        const report = await reportsService.getReportDetails(id)
        
        // Update report in list if exists
        const index = this.reports.findIndex(r => r.id === id)
        if (index >= 0) {
          this.reports[index] = report
        } else {
          this.reports.push(report)
        }
        
        return report
      } catch (error) {
        handleApiError(error, { logError: true })
        throw error
      }
    },

    /**
     * Get report types
     */
    getReportTypes() {
      return reportsService.getReportTypes()
    },

    /**
     * Get report formats
     */
    getReportFormats() {
      return reportsService.getReportFormats()
    },

    /**
     * Add report to list (utility method)
     * @param {Object} report - Report object
     */
    addReport(report) {
      this.reports.unshift(report)
      this.stats.totalReports += 1
      this.stats.reportsChange += 1
    },

    /**
     * Update report in list (utility method)
     * @param {Object} report - Report object
     */
    updateReportInList(report) {
      const index = this.reports.findIndex(r => r.id === report.id)
      if (index !== -1) {
        this.reports[index] = report
      }
    },

    /**
     * Remove report from list (utility method)
     * @param {number} id - Report ID
     */
    removeReport(id) {
      this.reports = this.reports.filter(report => report.id !== id)
      this.stats.totalReports = Math.max(0, this.stats.totalReports - 1)
      this.stats.reportsChange = Math.max(0, this.stats.reportsChange - 1)
    },

    /**
     * Clear error
     */
    clearError() {
      this.error = null
    },

    /**
     * Reset store state
     */
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
