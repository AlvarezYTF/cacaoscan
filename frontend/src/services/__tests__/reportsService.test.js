import { describe, it, expect, beforeEach, vi } from 'vitest'
import { ReportsService } from '../reportsService.js'

// Mock apiConfig to return base URL for testing
const mockApiBaseUrl = 'https://cacaoscan-backend.onrender.com'
vi.mock('@/utils/apiConfig', () => ({
  getApiBaseUrl: vi.fn(() => 'https://cacaoscan-backend.onrender.com'),
  getApiBaseUrlWithoutPath: vi.fn(() => 'https://cacaoscan-backend.onrender.com'),
  getApiBaseUrlWithPath: vi.fn(() => 'https://cacaoscan-backend.onrender.com/api/v1')
}))

// Mock auth store
const mockAuthStore = {
  token: 'test-token'
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

// Mock fetch
globalThis.fetch = vi.fn()

// Mock localStorage
const mockLocalStorage = {
  getItem: vi.fn((key) => {
    if (key === 'access_token' || key === 'token') {
      return 'test-token'
    }
    return null
  }),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}
globalThis.localStorage = mockLocalStorage

// Mock location for downloadReport
globalThis.location = {
  origin: mockApiBaseUrl
}

// Mock URL.createObjectURL and related DOM APIs
globalThis.URL = {
  createObjectURL: vi.fn(() => 'blob:http://localhost/test'),
  revokeObjectURL: vi.fn()
}

globalThis.document = {
  createElement: vi.fn(() => ({
    href: '',
    download: '',
    click: vi.fn(),
    remove: vi.fn()
  })),
  body: {
    appendChild: vi.fn(),
    removeChild: vi.fn()
  }
}

describe('ReportsService', () => {
  let reportsService

  beforeEach(() => {
    vi.clearAllMocks()
    
    // Mock localStorage to provide token
    globalThis.localStorage = {
      getItem: vi.fn((key) => {
        if (key === 'access_token' || key === 'token') {
          return 'test-token'
        }
        return null
      }),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn()
    }
    
    reportsService = new ReportsService()
    mockAuthStore.token = 'test-token'
  })

  describe('getReports', () => {
    it('should fetch reports successfully', async () => {
      const mockApiResponse = {
        results: [
          { id: 1, tipo_reporte: 'calidad', estado: 'completado' },
          { id: 2, tipo_reporte: 'finca', estado: 'generando' }
        ],
        count: 2
      }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: new Headers({
          'content-type': 'application/json'
        }),
        json: vi.fn().mockResolvedValue(mockApiResponse)
      })

      const result = await reportsService.getReports()

      expect(globalThis.fetch).toHaveBeenCalledWith(
        `${mockApiBaseUrl}/api/reportes/?page=1&page_size=20`,
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token'
          })
        })
      )

      // Service normalizes the response to reports and pagination format
      expect(result).toHaveProperty('reports')
      expect(result).toHaveProperty('pagination')
      expect(result.reports).toHaveLength(2)
      expect(result.pagination.totalItems).toBe(2)
      expect(result.reports[0].id).toBe(1)
      expect(result.reports[0].tipo_reporte).toBe('calidad')
      expect(result.reports[0].estado).toBe('completado')
      expect(result.reports[1].id).toBe(2)
      expect(result.reports[1].tipo_reporte).toBe('finca')
      expect(result.reports[1].estado).toBe('generando')
    })

    it('should fetch reports with filters', async () => {
      const filters = { tipo_reporte: 'calidad', estado: 'completado' }
      const mockReports = { results: [], count: 0 }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: new Headers({
          'content-type': 'application/json'
        }),
        json: vi.fn().mockResolvedValue(mockReports)
      })

      await reportsService.getReports(filters, 2, 10)

      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('tipo_reporte=calidad'),
        expect.any(Object)
      )

      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('page=2'),
        expect.any(Object)
      )
    })

    it('should handle error when fetching reports', async () => {
      const errorResponse = {
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
        headers: new Headers({
          'content-type': 'application/json'
        }),
        json: vi.fn().mockResolvedValue({ error: 'Unauthorized' })
      }

      globalThis.fetch.mockResolvedValue(errorResponse)

      // The service throws the error from errorData.error if it exists
      await expect(reportsService.getReports()).rejects.toThrow('Unauthorized')
    })
  })

  describe('getReportDetails', () => {
    it('should fetch report details successfully', async () => {
      const reportId = 1
      const mockReport = {
        id: 1,
        tipo_reporte: 'calidad',
        estado: 'completado',
        fecha_generacion: '2024-01-01'
      }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: new Headers({
          'content-type': 'application/json'
        }),
        json: vi.fn().mockResolvedValue(mockReport)
      })

      const result = await reportsService.getReportDetails(reportId)

      expect(globalThis.fetch).toHaveBeenCalledWith(
        `${mockApiBaseUrl}/api/reportes/1/`,
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token'
          })
        })
      )

      // normalizeReportDTO adds default fields, so we check the important ones
      expect(result).toMatchObject({
        id: 1,
        tipo_reporte: 'calidad',
        estado: 'completado',
        fecha_generacion: '2024-01-01'
      })
      // Verify that normalization added expected fields
      expect(result).toHaveProperty('tipo_reporte_display')
      expect(result).toHaveProperty('estado_display')
      expect(result).toHaveProperty('formato')
      expect(result).toHaveProperty('titulo')
    })

    it('should handle error when fetching report details', async () => {
      const errorResponse = {
        ok: false,
        status: 404,
        statusText: 'Not Found',
        headers: new Headers({
          'content-type': 'application/json'
        }),
        json: vi.fn().mockResolvedValue({ error: 'Report not found' })
      }

      globalThis.fetch.mockResolvedValue(errorResponse)

      // The service throws the error from errorData.error if it exists
      await expect(reportsService.getReportDetails(999)).rejects.toThrow('Report not found')
    })
  })

  describe('createReport', () => {
    it('should create report successfully', async () => {
      const reportData = {
        tipo_reporte: 'calidad',
        formato: 'pdf',
        titulo: 'Test Report'
      }

      const mockCreatedReport = {
        id: 1,
        tipo_reporte: 'calidad',
        tipo_reporte_display: 'calidad',
        formato: 'pdf',
        formato_display: 'PDF',
        titulo: 'Test Report',
        descripcion: '',
        estado: 'generando',
        estado_display: 'generando',
        fecha_solicitud: null,
        fecha_generacion: null,
        fecha_expiracion: null,
        tiempo_generacion_segundos: 0,
        tamano_archivo_mb: 0,
        tamaño_archivo: 0,
        archivo_url: null,
        esta_expirado: false,
        mensaje_error: null,
        parametros: {},
        filtros_aplicados: {},
        usuario_nombre: '',
        usuario_id: null
      }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: {
          get: vi.fn((name) => {
            if (name === 'content-type') {
              return 'application/json'
            }
            return null
          })
        },
        json: vi.fn().mockResolvedValue(mockCreatedReport)
      })

      const result = await reportsService.createReport(reportData)

      expect(globalThis.fetch).toHaveBeenCalledWith(
        `${mockApiBaseUrl}/api/reportes`,
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token'
          }),
          body: JSON.stringify({
            tipo_reporte: 'calidad',
            formato: 'pdf',
            titulo: 'Test Report',
            descripcion: '',
            parametros: {},
            filtros: {}
          })
        })
      )

      expect(result).toEqual(mockCreatedReport)
    })

    it('should handle error when creating report', async () => {
      const reportData = { tipo_reporte: 'calidad' }

      const errorResponse = {
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        headers: {
          get: vi.fn((name) => {
            if (name === 'content-type') {
              return 'application/json'
            }
            return null
          })
        },
        json: vi.fn().mockResolvedValue({ error: 'Invalid data' })
      }

      globalThis.fetch.mockResolvedValue(errorResponse)

      // The service throws the error from errorData.error if it exists
      await expect(reportsService.createReport(reportData)).rejects.toThrow('Invalid data')
    })
  })

  describe('downloadReport', () => {
    it('should download report successfully', async () => {
      const reportId = 1

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: {
          get: vi.fn((header) => {
            if (header === 'Content-Disposition') {
              return 'attachment; filename="reporte_1.pdf"'
            }
            return null
          })
        }
      })

      const result = await reportsService.downloadReport(reportId)

      expect(globalThis.fetch).toHaveBeenCalledWith(
        `${mockApiBaseUrl}/api/reportes/1/download/`,
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token',
            'Accept': 'application/octet-stream'
          })
        })
      )

      expect(result.ok).toBe(true)
    })

    it('should handle error when downloading report', async () => {
      const errorResponse = {
        ok: false,
        status: 404,
        statusText: 'Not Found',
        headers: new Headers({
          'content-type': 'application/json'
        }),
        json: vi.fn().mockResolvedValue({ error: 'Report not found' })
      }

      globalThis.fetch.mockResolvedValue(errorResponse)

      // The service throws the error from errorData.error if it exists
      await expect(reportsService.downloadReport(999)).rejects.toThrow('Report not found')
    })
  })

  describe('deleteReport', () => {
    it('should delete report successfully', async () => {
      const reportId = 1

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: new Headers({
          'content-type': 'application/json'
        }),
        json: vi.fn().mockResolvedValue({})
      })

      const result = await reportsService.deleteReport(reportId)

      expect(globalThis.fetch).toHaveBeenCalledWith(
        `${mockApiBaseUrl}/api/reportes/1/delete/`,
        expect.objectContaining({
          method: 'DELETE',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token'
          })
        })
      )

      expect(result).toBe(true)
    })

    it('should handle error when deleting report', async () => {
      const errorResponse = {
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        headers: new Headers({
          'content-type': 'application/json'
        }),
        json: vi.fn().mockResolvedValue({ error: 'Cannot delete' })
      }

      globalThis.fetch.mockResolvedValue(errorResponse)

      // The service throws the error from errorData.error if it exists
      await expect(reportsService.deleteReport(1)).rejects.toThrow('Cannot delete')
    })
  })

  describe('getReportsStats', () => {
    it('should fetch reports stats successfully', async () => {
      const mockStats = {
        total_reportes: 100,
        reportes_completados: 80,
        reportes_generando: 15,
        reportes_fallidos: 5
      }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: new Headers({
          'content-type': 'application/json'
        }),
        json: vi.fn().mockResolvedValue(mockStats)
      })

      const result = await reportsService.getReportsStats()

      // fetchGet constructs the full URL using API_BASE_URL
      expect(globalThis.fetch).toHaveBeenCalledWith(
        `${mockApiBaseUrl}/api/reportes/stats/`,
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token'
          })
        })
      )

      expect(result).toEqual({
        totalReports: 100,
        reportsChange: 0,
        completedReports: 80,
        completedChange: 0,
        inProgressReports: 15,
        inProgressChange: 0,
        errorReports: 5,
        errorChange: 0,
        reportsByType: {},
        reportsByFormat: {},
        recentReports: []
      })
    })
  })

  describe('cleanupExpiredReports', () => {
    it('should cleanup expired reports successfully', async () => {
      const mockResult = {
        deleted: 5,
        message: 'Expired reports cleaned'
      }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: new Headers({
          'content-type': 'application/json'
        }),
        json: vi.fn().mockResolvedValue(mockResult)
      })

      const result = await reportsService.cleanupExpiredReports()

      // fetchPost constructs the full URL using API_BASE_URL
      expect(globalThis.fetch).toHaveBeenCalledWith(
        `${mockApiBaseUrl}/api/reportes/cleanup/`,
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token'
          }),
          body: '{}'
        })
      )

      expect(result).toEqual(mockResult)
    })
  })

  describe('generateQualityReport', () => {
    it('should generate quality report', async () => {
      const title = 'Quality Report'
      const description = 'Test description'
      const filters = { fecha_inicio: '2024-01-01' }

      const mockReport = {
        id: 1,
        tipo_reporte: 'calidad',
        titulo: title
      }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: new Headers({
          'content-type': 'application/json'
        }),
        json: vi.fn().mockResolvedValue(mockReport)
      })

      const result = await reportsService.generateQualityReport(title, description, filters)

      // fetchPost constructs the full URL using API_BASE_URL
      expect(globalThis.fetch).toHaveBeenCalledWith(
        `${mockApiBaseUrl}/api/reportes`,
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token'
          }),
          body: expect.stringContaining('"tipo_reporte":"calidad"')
        })
      )

      expect(result.tipo_reporte).toBe('calidad')
    })
  })

  describe('generateFincaReport', () => {
    it('should generate finca report', async () => {
      const fincaId = 1
      const title = 'Finca Report'

      const mockReport = {
        id: 1,
        tipo_reporte: 'finca'
      }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: new Headers({
          'content-type': 'application/json'
        }),
        json: vi.fn().mockResolvedValue(mockReport)
      })

      const result = await reportsService.generateFincaReport(fincaId, title)

      expect(globalThis.fetch).toHaveBeenCalled()
      expect(result.tipo_reporte).toBe('finca')
    })
  })

  describe('generateAuditReport', () => {
    it('should generate audit report', async () => {
      const title = 'Audit Report'

      const mockReport = {
        id: 1,
        tipo_reporte: 'auditoria'
      }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: new Headers({
          'content-type': 'application/json'
        }),
        json: vi.fn().mockResolvedValue(mockReport)
      })

      const result = await reportsService.generateAuditReport(title)

      expect(result.tipo_reporte).toBe('auditoria')
    })
  })

  describe('generateCustomReport', () => {
    it('should generate custom report', async () => {
      const tipoReporte = 'custom'
      const formato = 'excel'
      const title = 'Custom Report'
      const parametros = { custom_param: 'value' }
      const filtros = { date: '2024-01-01' }

      const mockReport = {
        id: 1,
        tipo_reporte: 'personalizado'
      }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: new Headers({
          'content-type': 'application/json'
        }),
        json: vi.fn().mockResolvedValue(mockReport)
      })

      const result = await reportsService.generateCustomReport(tipoReporte, formato, title, parametros, filtros)

      expect(result.tipo_reporte).toBe('personalizado')
    })
  })

  describe('downloadReportFile', () => {
    it('should download report file with filename from header', async () => {
      const reportId = 1
      const mockBlob = new Blob(['test'], { type: 'application/pdf' })

      const mockLink = {
        href: '',
        download: '',
        click: vi.fn(),
        remove: vi.fn()
      }

      globalThis.document.createElement.mockReturnValue(mockLink)

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: {
          get: vi.fn((header) => {
            if (header === 'Content-Disposition') {
              return 'attachment; filename="reporte_1.pdf"'
            }
            return null
          })
        },
        blob: vi.fn().mockResolvedValue(mockBlob)
      })

      const result = await reportsService.downloadReportFile(reportId)

      expect(globalThis.URL.createObjectURL).toHaveBeenCalled()
      expect(mockLink.click).toHaveBeenCalled()
      expect(result).toBe(true)
    })

    it('should download report file with custom filename', async () => {
      const reportId = 1
      const filename = 'custom_report.pdf'

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: {
          get: vi.fn(() => null)
        },
        blob: vi.fn().mockResolvedValue(new Blob())
      })

      globalThis.document.createElement.mockReturnValue({
        href: '',
        download: '',
        click: vi.fn(),
        remove: vi.fn()
      })

      await reportsService.downloadReportFile(reportId, filename)

      expect(globalThis.document.createElement).toHaveBeenCalledWith('a')
    })
  })

  describe('checkReportStatus', () => {
    it('should check report status successfully', async () => {
      const reportId = 1
      const mockReport = {
        id: 1,
        estado: 'completado',
        esta_expirado: false,
        fecha_generacion: '2024-01-01',
        mensaje_error: null
      }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: new Headers({
          'content-type': 'application/json'
        }),
        json: vi.fn().mockResolvedValue(mockReport)
      })

      const result = await reportsService.checkReportStatus(reportId)

      expect(result).toEqual({
        id: 1,
        estado: 'completado',
        esta_expirado: false,
        fecha_generacion: '2024-01-01',
        mensaje_error: null
      })
    })
  })

  describe('getReportTypes', () => {
    it('should return available report types', () => {
      const types = reportsService.getReportTypes()

      expect(types).toHaveLength(4)
      expect(types[0].value).toBe('calidad')
      expect(types[1].value).toBe('finca')
      expect(types[2].value).toBe('auditoria')
      expect(types[3].value).toBe('personalizado')
    })
  })

  describe('getReportFormats', () => {
    it('should return available report formats', () => {
      const formats = reportsService.getReportFormats()

      expect(formats).toHaveLength(4)
      expect(formats.map(f => f.value)).toContain('pdf')
      expect(formats.map(f => f.value)).toContain('excel')
      expect(formats.map(f => f.value)).toContain('csv')
      expect(formats.map(f => f.value)).toContain('json')
    })
  })

  describe('getReportStates', () => {
    it('should return available report states', () => {
      const states = reportsService.getReportStates()

      expect(states).toHaveLength(3)
      expect(states.map(s => s.value)).toContain('completado')
      expect(states.map(s => s.value)).toContain('generando')
      expect(states.map(s => s.value)).toContain('fallido')
    })
  })
})

