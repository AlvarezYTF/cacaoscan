import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useReportsStore } from '../reports.js'
import api from '@/services/api'

// Mock api service
vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

// Mock fileExportUtils
vi.mock('@/utils/fileExportUtils', () => ({
  downloadFileFromResponse: vi.fn()
}))

describe('Reports Store', () => {
  let store

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useReportsStore()
    vi.clearAllMocks()
  })

  describe('State and Getters', () => {
    it('should have initial state', () => {
      expect(store.reports).toEqual([])
      expect(store.stats.totalReports).toBe(0)
      expect(store.pagination.currentPage).toBe(1)
      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
    })

    it('should get report by id', () => {
      store.reports = [
        { id: 1, tipo_reporte: 'anual' },
        { id: 2, tipo_reporte: 'mensual' }
      ]

      const report = store.getReportById(1)
      expect(report).toEqual({ id: 1, tipo_reporte: 'anual' })
    })

    it('should get reports by type', () => {
      store.reports = [
        { id: 1, tipo_reporte: 'anual' },
        { id: 2, tipo_reporte: 'mensual' },
        { id: 3, tipo_reporte: 'anual' }
      ]

      const anualReports = store.getReportsByType('anual')
      expect(anualReports).toHaveLength(2)
    })

    it('should get reports by status', () => {
      store.reports = [
        { id: 1, estado: 'completado' },
        { id: 2, estado: 'pendiente' },
        { id: 3, estado: 'completado' }
      ]

      const completedReports = store.getReportsByStatus('completado')
      expect(completedReports).toHaveLength(2)
    })

    it('should get recent reports', () => {
      const now = new Date()
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000)

      store.reports = [
        { id: 1, fecha_solicitud: now.toISOString() },
        { id: 2, fecha_solicitud: yesterday.toISOString() },
        { id: 3, fecha_solicitud: now.toISOString() }
      ]

      const recent = store.getRecentReports(2)
      expect(recent).toHaveLength(2)
    })

    it('should get completed reports', () => {
      store.reports = [
        { id: 1, estado: 'completado' },
        { id: 2, estado: 'pendiente' },
        { id: 3, estado: 'completado' }
      ]

      const completed = store.getCompletedReports
      expect(completed).toHaveLength(2)
    })

    it('should get pending reports', () => {
      store.reports = [
        { id: 1, estado: 'pendiente' },
        { id: 2, estado: 'completado' },
        { id: 3, estado: 'pendiente' }
      ]

      const pending = store.getPendingReports
      expect(pending).toHaveLength(2)
    })

    it('should get processing reports', () => {
      store.reports = [
        { id: 1, estado: 'procesando' },
        { id: 2, estado: 'pendiente' },
        { id: 3, estado: 'procesando' }
      ]

      const processing = store.getProcessingReports
      expect(processing).toHaveLength(2)
    })

    it('should get error reports', () => {
      store.reports = [
        { id: 1, estado: 'error' },
        { id: 2, estado: 'completado' },
        { id: 3, estado: 'error' }
      ]

      const error = store.getErrorReports
      expect(error).toHaveLength(2)
    })
  })

  describe('fetchReports', () => {
    it('should fetch reports successfully', async () => {
      const mockResponse = {
        data: {
          results: [
            { id: 1, tipo_reporte: 'anual', estado: 'completado' },
            { id: 2, tipo_reporte: 'mensual', estado: 'pendiente' }
          ],
          current_page: 1,
          total_pages: 1,
          total_count: 2,
          page_size: 20
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await store.fetchReports({ page: 1 })

      expect(api.get).toHaveBeenCalledWith('/reports/', {
        params: { page: 1 }
      })
      expect(store.reports).toEqual(mockResponse.data.results)
      expect(store.pagination.currentPage).toBe(1)
      expect(store.pagination.totalPages).toBe(1)
      expect(store.pagination.totalItems).toBe(2)
      expect(store.loading).toBe(false)
    })

    it('should handle errors when fetching reports', async () => {
      const mockError = {
        response: {
          data: { detail: 'Error fetching reports' }
        }
      }

      vi.mocked(api.get).mockRejectedValue(mockError)

      await expect(store.fetchReports()).rejects.toThrow()
      expect(store.error).toBe('Error fetching reports')
      expect(store.loading).toBe(false)
    })
  })

  describe('fetchStats', () => {
    it('should fetch stats successfully', async () => {
      const mockResponse = {
        data: {
          totalReports: 50,
          completedReports: 40,
          inProgressReports: 5,
          errorReports: 5
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await store.fetchStats()

      expect(api.get).toHaveBeenCalledWith('/reports/stats/')
      expect(store.stats).toEqual(mockResponse.data)
    })
  })

  describe('createReport', () => {
    it('should create report successfully', async () => {
      const reportData = {
        tipo_reporte: 'anual',
        fecha_inicio: '2024-01-01',
        fecha_fin: '2024-12-31'
      }

      const mockResponse = {
        data: {
          id: 1,
          ...reportData,
          estado: 'pendiente'
        }
      }

      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const result = await store.createReport(reportData)

      expect(api.post).toHaveBeenCalledWith('/reports/create/', reportData)
      expect(store.reports).toContainEqual(mockResponse.data)
      expect(store.stats.totalReports).toBe(1)
      expect(store.stats.reportsChange).toBe(1)
    })

    it('should handle errors when creating report', async () => {
      const mockError = {
        response: {
          data: { detail: 'Error creating report' }
        }
      }

      vi.mocked(api.post).mockRejectedValue(mockError)

      await expect(store.createReport({})).rejects.toThrow()
      expect(store.error).toBe('Error creating report')
    })
  })

  describe('updateReport', () => {
    it('should update report successfully', async () => {
      const reportId = 1
      const updateData = {
        estado: 'completado'
      }

      store.reports = [
        { id: 1, tipo_reporte: 'anual', estado: 'pendiente' }
      ]

      const mockResponse = {
        data: {
          id: 1,
          tipo_reporte: 'anual',
          estado: 'completado'
        }
      }

      vi.mocked(api.put).mockResolvedValue(mockResponse)

      const result = await store.updateReport(reportId, updateData)

      expect(api.put).toHaveBeenCalledWith(`/reports/${reportId}/update/`, updateData)
      expect(store.reports[0].estado).toBe('completado')
    })
  })

  describe('deleteReport', () => {
    it('should delete report successfully', async () => {
      const reportId = 1

      store.reports = [
        { id: 1, tipo_reporte: 'anual' },
        { id: 2, tipo_reporte: 'mensual' }
      ]
      store.stats.totalReports = 2

      vi.mocked(api.delete).mockResolvedValue({})

      const result = await store.deleteReport(reportId)

      expect(api.delete).toHaveBeenCalledWith(`/reports/${reportId}/delete/`)
      expect(store.reports).toHaveLength(1)
      expect(store.stats.totalReports).toBe(1)
      expect(store.stats.reportsChange).toBe(-1)
    })
  })

  describe('bulkDeleteReports', () => {
    it('should bulk delete reports successfully', async () => {
      const reportIds = [1, 2]

      store.reports = [
        { id: 1, tipo_reporte: 'anual' },
        { id: 2, tipo_reporte: 'mensual' },
        { id: 3, tipo_reporte: 'trimestral' }
      ]
      store.stats.totalReports = 3

      vi.mocked(api.post).mockResolvedValue({})

      const result = await store.bulkDeleteReports(reportIds)

      expect(api.post).toHaveBeenCalledWith('/reports/bulk-delete/', {
        report_ids: reportIds
      })
      expect(store.reports).toHaveLength(1)
      expect(store.stats.totalReports).toBe(1)
    })
  })

  describe('downloadReport', () => {
    it('should download report successfully', async () => {
      const reportId = 1
      const blob = new Blob(['pdf content'], { type: 'application/pdf' })

      const mockResponse = {
        data: blob,
        headers: { 'content-disposition': 'attachment; filename="report.pdf"' }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const { downloadFileFromResponse } = await import('@/utils/fileExportUtils')

      const result = await store.downloadReport(reportId)

      expect(api.get).toHaveBeenCalledWith(`/reports/${reportId}/download/`, {
        responseType: 'blob'
      })
      expect(downloadFileFromResponse).toHaveBeenCalled()
    })
  })

  describe('exportReports', () => {
    it('should export reports successfully', async () => {
      const params = {
        format: 'excel',
        date_from: '2024-01-01'
      }

      const blob = new Blob(['zip content'], { type: 'application/zip' })
      const mockResponse = {
        data: blob
      }

      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const { downloadFileFromResponse } = await import('@/utils/fileExportUtils')

      const result = await store.exportReports(params)

      expect(api.post).toHaveBeenCalledWith('/reports/export/', params, {
        responseType: 'blob'
      })
      expect(downloadFileFromResponse).toHaveBeenCalled()
    })
  })

  describe('getReportPreview', () => {
    it('should get report preview successfully', async () => {
      const reportId = 1
      const mockResponse = {
        data: {
          preview_url: 'https://example.com/preview'
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await store.getReportPreview(reportId)

      expect(api.get).toHaveBeenCalledWith(`/reports/${reportId}/preview/`)
      expect(result).toEqual(mockResponse)
    })
  })

  describe('regenerateReport', () => {
    it('should regenerate report successfully', async () => {
      const reportId = 1

      store.reports = [
        { id: 1, estado: 'error' }
      ]

      const mockResponse = {
        data: {
          id: 1,
          estado: 'pendiente'
        }
      }

      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const result = await store.regenerateReport(reportId)

      expect(api.post).toHaveBeenCalledWith(`/reports/${reportId}/regenerate/`)
      expect(store.reports[0].estado).toBe('pendiente')
    })
  })

  describe('Helper Actions', () => {
    it('should add report to list', () => {
      const report = { id: 1, tipo_reporte: 'anual' }
      store.stats.totalReports = 0

      store.addReport(report)

      expect(store.reports).toContainEqual(report)
      expect(store.stats.totalReports).toBe(1)
    })

    it('should update report in list', () => {
      store.reports = [
        { id: 1, estado: 'pendiente' }
      ]

      const updatedReport = { id: 1, estado: 'completado' }

      store.updateReportInList(updatedReport)

      expect(store.reports[0].estado).toBe('completado')
    })

    it('should remove report from list', () => {
      store.reports = [
        { id: 1, tipo_reporte: 'anual' },
        { id: 2, tipo_reporte: 'mensual' }
      ]
      store.stats.totalReports = 2

      store.removeReport(1)

      expect(store.reports).toHaveLength(1)
      expect(store.stats.totalReports).toBe(1)
    })

    it('should clear error', () => {
      store.error = 'Some error'
      store.clearError()
      expect(store.error).toBe(null)
    })

    it('should reset store', () => {
      store.reports = [{ id: 1 }]
      store.stats.totalReports = 1
      store.pagination.currentPage = 2
      store.loading = true
      store.error = 'Error'

      store.reset()

      expect(store.reports).toEqual([])
      expect(store.stats.totalReports).toBe(0)
      expect(store.pagination.currentPage).toBe(1)
      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
    })
  })
})

