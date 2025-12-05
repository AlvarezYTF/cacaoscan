/**
 * Unit tests for useReports composable
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { nextTick } from 'vue'
import {
  formatReportType,
  formatReportStatus,
  getReportStatusClass,
  getReportStatusIcon,
  formatFileSize,
  formatDuration,
  useReports
} from '../useReports.js'
import reportsService from '@/services/reportsService'
import { useNotificationStore } from '@/stores/notifications'

// Mock dependencies
vi.mock('@/services/reportsService', () => ({
  default: {
    createReport: vi.fn(),
    downloadReportFile: vi.fn(),
    getReportDetails: vi.fn(),
    checkReportStatus: vi.fn(),
    getReportTypes: vi.fn(() => [
      { value: 'calidad', label: 'Calidad' },
      { value: 'finca', label: 'Finca' }
    ]),
    getReportFormats: vi.fn(() => [
      { value: 'pdf', label: 'PDF' },
      { value: 'excel', label: 'Excel' }
    ]),
    getReportStates: vi.fn(() => [
      { value: 'completado', label: 'Completado' },
      { value: 'generando', label: 'Generando' }
    ])
  }
}))

vi.mock('@/stores/notifications', () => ({
  useNotificationStore: vi.fn(() => ({
    addNotification: vi.fn()
  }))
}))

vi.mock('../useDateFormatting', () => ({
  useDateFormatting: vi.fn(() => ({
    formatDate: vi.fn((date) => date || 'N/A')
  }))
}))

describe('useReports utility functions', () => {
  describe('formatReportType', () => {
    it('should format known report types', () => {
      expect(formatReportType('calidad')).toBe('Calidad')
      expect(formatReportType('finca')).toBe('Finca')
      expect(formatReportType('auditoria')).toBe('Auditoría')
      expect(formatReportType('lote')).toBe('Lote')
      expect(formatReportType('usuario')).toBe('Usuario')
      expect(formatReportType('personalizado')).toBe('Personalizado')
      expect(formatReportType('metricas')).toBe('Métricas')
      expect(formatReportType('entrenamiento')).toBe('Entrenamiento')
    })

    it('should return original value for unknown type', () => {
      expect(formatReportType('unknown')).toBe('unknown')
    })
  })

  describe('formatReportStatus', () => {
    it('should format known report statuses', () => {
      expect(formatReportStatus('completado')).toBe('Completado')
      expect(formatReportStatus('generando')).toBe('Generando')
      expect(formatReportStatus('fallido')).toBe('Fallido')
      expect(formatReportStatus('pendiente')).toBe('Pendiente')
      expect(formatReportStatus('procesando')).toBe('Procesando')
      expect(formatReportStatus('error')).toBe('Error')
    })

    it('should return original value for unknown status', () => {
      expect(formatReportStatus('unknown')).toBe('unknown')
    })
  })

  describe('getReportStatusClass', () => {
    it('should return CSS class for status', () => {
      expect(getReportStatusClass('completado')).toBe('status-completed')
      expect(getReportStatusClass('error')).toBe('status-error')
      expect(getReportStatusClass('fallido')).toBe('status-error')
      expect(getReportStatusClass('pendiente')).toBe('status-pending')
      expect(getReportStatusClass('procesando')).toBe('status-processing')
      expect(getReportStatusClass('generando')).toBe('status-processing')
    })

    it('should return default class for unknown status', () => {
      expect(getReportStatusClass('unknown')).toBe('status-pending')
    })
  })

  describe('getReportStatusIcon', () => {
    it('should return icon class for status', () => {
      expect(getReportStatusIcon('completado')).toContain('check-circle')
      expect(getReportStatusIcon('error')).toContain('exclamation-circle')
      expect(getReportStatusIcon('fallido')).toContain('exclamation-circle')
      expect(getReportStatusIcon('procesando')).toContain('spinner')
      expect(getReportStatusIcon('generando')).toContain('spinner')
      expect(getReportStatusIcon('pendiente')).toContain('clock')
    })

    it('should return default icon for unknown status', () => {
      expect(getReportStatusIcon('unknown')).toContain('clock')
    })
  })

  describe('formatFileSize', () => {
    it('should format bytes', () => {
      const result = formatFileSize(512)
      expect(result).toContain('B')
      expect(result).toContain('512')
    })

    it('should format KB', () => {
      const result = formatFileSize(1024)
      expect(result).toContain('KB')
    })

    it('should format MB', () => {
      const result = formatFileSize(1024 * 1024)
      expect(result).toContain('MB')
    })

    it('should format GB', () => {
      const result = formatFileSize(1024 * 1024 * 1024)
      expect(result).toContain('GB')
    })

    it('should return N/A for zero', () => {
      expect(formatFileSize(0)).toBe('N/A')
    })

    it('should return N/A for null/undefined', () => {
      expect(formatFileSize(null)).toBe('N/A')
      expect(formatFileSize(undefined)).toBe('N/A')
    })
  })

  describe('formatDuration', () => {
    it('should format seconds correctly', () => {
      expect(formatDuration(65)).toContain('1')
      expect(formatDuration(65)).toContain('5')
      expect(formatDuration(30)).toContain('30')
    })

    it('should format minutes and seconds', () => {
      const result = formatDuration(125)
      expect(result).toContain('2')
      expect(result).toContain('5')
    })

    it('should return N/A for zero/null', () => {
      expect(formatDuration(0)).toBe('N/A')
      expect(formatDuration(null)).toBe('N/A')
      expect(formatDuration(undefined)).toBe('N/A')
    })
  })
})

describe('useReports composable', () => {
  let notificationStore
  let mockAddNotification

  beforeEach(() => {
    vi.clearAllMocks()
    mockAddNotification = vi.fn()
    notificationStore = {
      addNotification: mockAddNotification
    }
    useNotificationStore.mockReturnValue(notificationStore)
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('initialization', () => {
    it('should initialize with default state', () => {
      const { loading, error, generating, reports, filters, formData } = useReports()

      expect(loading.value).toBe(false)
      expect(error.value).toBe(null)
      expect(generating.value).toBe(false)
      expect(reports.value).toEqual([])
      expect(filters.tipo_reporte).toBe('')
      expect(formData.tipo_reporte).toBe('')
    })

    it('should initialize computed properties', () => {
      const { hasFilters, reportTypes, reportFormats, reportStates } = useReports()

      expect(hasFilters.value).toBe(false)
      expect(reportTypes.value).toBeDefined()
      expect(reportFormats.value).toBeDefined()
      expect(reportStates.value).toBeDefined()
    })
  })

  describe('hasFilters computed', () => {
    it('should return false when no filters are set', () => {
      const { hasFilters } = useReports()
      expect(hasFilters.value).toBe(false)
    })

    it('should return true when any filter is set', () => {
      const { hasFilters, filters } = useReports()
      filters.tipo_reporte = 'calidad'
      expect(hasFilters.value).toBe(true)
    })
  })

  describe('buildReportData', () => {
    it('should build report data from form', () => {
      const { buildReportData, formData } = useReports()
      
      formData.tipo_reporte = 'calidad'
      formData.formato = 'pdf'
      formData.titulo = 'Test Report'
      formData.descripcion = 'Test Description'
      formData.parametros.finca_id = '123'
      formData.filtros.fecha_desde = '2024-01-01'

      const data = buildReportData()

      expect(data.tipo_reporte).toBe('calidad')
      expect(data.formato).toBe('pdf')
      expect(data.titulo).toBe('Test Report')
      expect(data.descripcion).toBe('Test Description')
      expect(data.parametros.finca_id).toBe('123')
      expect(data.filtros.fecha_desde).toBe('2024-01-01')
    })

    it('should handle empty parameters and filters', () => {
      const { buildReportData, formData } = useReports()
      
      formData.tipo_reporte = 'calidad'
      formData.formato = 'pdf'
      formData.titulo = 'Test Report'
      formData.parametros = {}
      formData.filtros = {}

      const data = buildReportData()

      expect(data.parametros).toEqual({})
      expect(data.filtros).toEqual({})
    })
  })

  describe('validateReportForm', () => {
    it('should validate form with all required fields', () => {
      const { validateReportForm, formData } = useReports()
      
      formData.tipo_reporte = 'calidad'
      formData.formato = 'pdf'
      formData.titulo = 'Test Report'

      const result = validateReportForm()

      expect(result.valid).toBe(true)
      expect(Object.keys(result.errors)).toHaveLength(0)
    })

    it('should return errors for missing required fields', () => {
      const { validateReportForm, formData } = useReports()
      
      formData.tipo_reporte = ''
      formData.formato = ''
      formData.titulo = ''

      const result = validateReportForm()

      expect(result.valid).toBe(false)
      expect(result.errors.tipo_reporte).toBeDefined()
      expect(result.errors.formato).toBeDefined()
      expect(result.errors.titulo).toBeDefined()
    })

    it('should validate finca_id for finca report type', () => {
      const { validateReportForm, formData } = useReports()
      
      formData.tipo_reporte = 'finca'
      formData.formato = 'pdf'
      formData.titulo = 'Test Report'
      formData.parametros.finca_id = ''

      const result = validateReportForm()

      expect(result.valid).toBe(false)
      expect(result.errors.finca_id).toBeDefined()
    })

    it('should accept empty title with only whitespace as invalid', () => {
      const { validateReportForm, formData } = useReports()
      
      formData.tipo_reporte = 'calidad'
      formData.formato = 'pdf'
      formData.titulo = '   '

      const result = validateReportForm()

      expect(result.valid).toBe(false)
      expect(result.errors.titulo).toBeDefined()
    })
  })

  describe('generateReport', () => {
    it('should generate report successfully', async () => {
      const mockReport = { id: 1, titulo: 'Test Report', estado: 'generando' }
      reportsService.createReport.mockResolvedValue(mockReport)

      const { generateReport, formData, generating, error } = useReports()
      
      formData.tipo_reporte = 'calidad'
      formData.formato = 'pdf'
      formData.titulo = 'Test Report'

      const result = await generateReport()

      expect(result).toEqual(mockReport)
      expect(generating.value).toBe(false)
      expect(error.value).toBe(null)
      expect(mockAddNotification).toHaveBeenCalledWith({
        type: 'success',
        title: 'Reporte generado',
        message: expect.stringContaining('Test Report')
      })
    })

    it('should handle validation errors', async () => {
      const { generateReport, formData, generating } = useReports()
      
      formData.tipo_reporte = ''
      formData.formato = 'pdf'
      formData.titulo = 'Test Report'

      await expect(generateReport()).rejects.toThrow()
      expect(generating.value).toBe(false)
    })

    it('should handle API errors', async () => {
      const apiError = {
        response: {
          data: { detail: 'API Error' }
        },
        message: 'Network Error'
      }
      reportsService.createReport.mockRejectedValue(apiError)

      const { generateReport, formData, generating, error } = useReports()
      
      formData.tipo_reporte = 'calidad'
      formData.formato = 'pdf'
      formData.titulo = 'Test Report'

      await expect(generateReport()).rejects.toThrow()
      expect(generating.value).toBe(false)
      expect(error.value).toBe('API Error')
      expect(mockAddNotification).toHaveBeenCalledWith({
        type: 'error',
        title: 'Error al generar reporte',
        message: 'API Error'
      })
    })
  })

  describe('applyFilters', () => {
    it('should apply filters', () => {
      const { applyFilters, filters } = useReports()
      
      applyFilters({ tipo_reporte: 'calidad', estado: 'completado' })

      expect(filters.tipo_reporte).toBe('calidad')
      expect(filters.estado).toBe('completado')
    })

    it('should merge with existing filters', () => {
      const { applyFilters, filters } = useReports()
      
      filters.tipo_reporte = 'finca'
      applyFilters({ estado: 'completado' })

      expect(filters.tipo_reporte).toBe('finca')
      expect(filters.estado).toBe('completado')
    })
  })

  describe('clearFilters', () => {
    it('should clear all filters', () => {
      const { clearFilters, filters } = useReports()
      
      filters.tipo_reporte = 'calidad'
      filters.estado = 'completado'
      filters.fecha_desde = '2024-01-01'

      clearFilters()

      expect(filters.tipo_reporte).toBe('')
      expect(filters.estado).toBe('')
      expect(filters.fecha_desde).toBe('')
    })
  })

  describe('downloadReport', () => {
    it('should download report successfully', async () => {
      reportsService.downloadReportFile.mockResolvedValue(true)

      const { downloadReport, loading, error } = useReports()

      await downloadReport(1, 'test.pdf')

      expect(loading.value).toBe(false)
      expect(error.value).toBe(null)
      expect(mockAddNotification).toHaveBeenCalledWith({
        type: 'success',
        title: 'Descarga iniciada',
        message: 'El archivo se está descargando'
      })
    })

    it('should handle download errors', async () => {
      const downloadError = new Error('Download failed')
      reportsService.downloadReportFile.mockRejectedValue(downloadError)

      const { downloadReport, loading, error } = useReports()

      await expect(downloadReport(1)).rejects.toThrow()
      expect(loading.value).toBe(false)
      expect(error.value).toBe('Download failed')
      expect(mockAddNotification).toHaveBeenCalledWith({
        type: 'error',
        title: 'Error al descargar',
        message: 'Download failed'
      })
    })
  })

  describe('previewReport', () => {
    it('should preview report successfully', async () => {
      const mockReport = { id: 1, titulo: 'Test Report' }
      reportsService.getReportDetails.mockResolvedValue(mockReport)

      const { previewReport, loading, error } = useReports()

      const result = await previewReport(1)

      expect(result).toEqual(mockReport)
      expect(loading.value).toBe(false)
      expect(error.value).toBe(null)
    })

    it('should handle preview errors', async () => {
      const previewError = {
        response: {
          data: { detail: 'Preview Error' }
        },
        message: 'Error'
      }
      reportsService.getReportDetails.mockRejectedValue(previewError)

      const { previewReport, loading, error } = useReports()

      await expect(previewReport(1)).rejects.toThrow()
      expect(loading.value).toBe(false)
      expect(error.value).toBe('Preview Error')
    })
  })

  describe('checkReportStatus', () => {
    it('should check report status successfully', async () => {
      const mockStatus = { estado: 'completado', id: 1 }
      reportsService.checkReportStatus.mockResolvedValue(mockStatus)

      const { checkReportStatus } = useReports()

      const result = await checkReportStatus(1)

      expect(result).toEqual(mockStatus)
    })

    it('should handle status check errors', async () => {
      const statusError = new Error('Status check failed')
      reportsService.checkReportStatus.mockRejectedValue(statusError)

      const { checkReportStatus } = useReports()

      await expect(checkReportStatus(1)).rejects.toThrow()
    })
  })

  describe('pollForCompletion', () => {
    let unhandledRejections = []

    beforeEach(() => {
      vi.useFakeTimers()
      unhandledRejections = []
      // Capture unhandled rejections
      process.listeners('unhandledRejection')
      process.on('unhandledRejection', (reason) => {
        unhandledRejections.push(reason)
      })
    })

    afterEach(() => {
      // Clear all timers before switching back to real timers
      vi.clearAllTimers()
      vi.useRealTimers()
      // Verify no unhandled rejections occurred
      expect(unhandledRejections).toHaveLength(0)
      unhandledRejections = []
    })

    it('should poll until completion', async () => {
      const mockCompletedReport = { id: 1, estado: 'completado' }
      
      reportsService.checkReportStatus
        .mockResolvedValueOnce({ estado: 'generando' })
        .mockResolvedValueOnce({ estado: 'generando' })
        .mockResolvedValueOnce({ estado: 'completado' })
      reportsService.getReportDetails.mockResolvedValue(mockCompletedReport)

      const { pollForCompletion } = useReports()

      const pollPromise = pollForCompletion(1, 100, 10)

      await vi.advanceTimersByTimeAsync(300)

      const result = await pollPromise

      expect(result).toEqual(mockCompletedReport)
    })

    it('should reject on error status', async () => {
      reportsService.checkReportStatus.mockResolvedValue({
        estado: 'error',
        mensaje_error: 'Generation failed'
      })

      const { pollForCompletion } = useReports()

      const pollPromise = pollForCompletion(1, 100, 10)

      // Start the polling
      await vi.advanceTimersByTimeAsync(0)
      
      // Wait for the promise to reject
      await expect(pollPromise).rejects.toThrow('Generation failed')
      
      // Clear all timers immediately after rejection
      vi.clearAllTimers()
      
      // Wait for any pending async operations
      await nextTick()
      await vi.advanceTimersByTimeAsync(0)
    })

    it('should reject on timeout', async () => {
      reportsService.checkReportStatus.mockResolvedValue({ estado: 'generando' })

      const { pollForCompletion } = useReports()

      const pollPromise = pollForCompletion(1, 100, 2)

      // Start the polling (first attempt)
      await vi.advanceTimersByTimeAsync(0)
      
      // Advance to trigger the second attempt (maxAttempts = 2)
      await vi.advanceTimersByTimeAsync(100)
      
      // Wait for the promise to reject
      await expect(pollPromise).rejects.toThrow('Tiempo de espera agotado')
      
      // Clear all timers immediately after rejection
      vi.clearAllTimers()
      
      // Wait for any pending async operations
      await nextTick()
      await vi.advanceTimersByTimeAsync(0)
    })
  })

  describe('watchStatus', () => {
    beforeEach(() => {
      vi.useFakeTimers()
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('should watch status changes', async () => {
      const onStatusChange = vi.fn()
      reportsService.checkReportStatus
        .mockResolvedValueOnce({ estado: 'generando' })
        .mockResolvedValueOnce({ estado: 'completado' })

      const { watchStatus } = useReports()

      const stopWatching = watchStatus(1, onStatusChange)

      await vi.advanceTimersByTimeAsync(6000)

      expect(onStatusChange).toHaveBeenCalled()
      
      stopWatching()
    })

    it('should stop watching on completion', async () => {
      const onStatusChange = vi.fn()
      reportsService.checkReportStatus.mockResolvedValue({ estado: 'completado' })

      const { watchStatus } = useReports()

      watchStatus(1, onStatusChange)

      await vi.advanceTimersByTimeAsync(3000)

      expect(onStatusChange).toHaveBeenCalled()
    })

    it('should stop watching on error', async () => {
      const onStatusChange = vi.fn()
      reportsService.checkReportStatus.mockRejectedValue(new Error('Status check failed'))

      const { watchStatus } = useReports()

      watchStatus(1, onStatusChange)

      await vi.advanceTimersByTimeAsync(3000)

      expect(onStatusChange).not.toHaveBeenCalled()
    })
  })

  describe('resetForm', () => {
    it('should reset form to initial state', () => {
      const { resetForm, formData, error } = useReports()
      
      formData.tipo_reporte = 'calidad'
      formData.formato = 'pdf'
      formData.titulo = 'Test'
      formData.descripcion = 'Description'
      formData.parametros.finca_id = '123'
      formData.filtros.fecha_desde = '2024-01-01'
      error.value = 'Some error'

      resetForm()

      expect(formData.tipo_reporte).toBe('')
      expect(formData.formato).toBe('')
      expect(formData.titulo).toBe('')
      expect(formData.descripcion).toBe('')
      expect(formData.parametros.finca_id).toBe('')
      expect(formData.filtros.fecha_desde).toBe('')
      expect(error.value).toBe(null)
    })
  })
})

