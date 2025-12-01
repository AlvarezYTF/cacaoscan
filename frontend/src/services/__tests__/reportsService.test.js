import { describe, it, expect, beforeEach, vi } from 'vitest'
import { ReportsService } from '../reportsService.js'

// Mock apiConfig to return base URL for testing
const mockApiBaseUrl = 'https://cacaoscan-backend.onrender.com'
vi.mock('@/utils/apiConfig', () => ({
  getApiBaseUrlWithoutPath: vi.fn(() => 'https://cacaoscan-backend.onrender.com'),
  getApiBaseUrlWithPath: vi.fn(() => 'https://cacaoscan-backend.onrender.com/api/v1'),
  getApiBaseUrl: vi.fn(() => 'https://cacaoscan-backend.onrender.com/api/v1')
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
        headers: {
          get: vi.fn((header) => {
            if (header === 'content-type') {
              return 'application/json'
            }
            return null
          })
        },
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

      // The normalizeReportListResponse function transforms the API response
      // So we check the normalized structure instead of the raw API response
      expect(result).toHaveProperty('reports')
      expect(result).toHaveProperty('pagination')
      expect(result.reports).toHaveLength(2)
      expect(result.pagination).toMatchObject({
        currentPage: 1,
        totalItems: 2,
        itemsPerPage: 20
      })
      // Verify that reports are normalized
      expect(result.reports[0]).toMatchObject({
        id: 1,
        tipo_reporte: 'calidad',
        estado: 'completado'
      })
      expect(result.reports[1]).toMatchObject({
        id: 2,
        tipo_reporte: 'finca',
        estado: 'generando'
      })
    })

    it('should fetch reports with filters', async () => {
      const filters = { tipo_reporte: 'calidad', estado: 'completado' }
      const mockReports = { results: [], count: 0 }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: {
          get: vi.fn((header) => {
            if (header === 'content-type') {
              return 'application/json'
            }
            return null
          })
        },
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
        headers: {
          get: vi.fn((header) => {
            if (header === 'content-type') {
              return 'application/json'
            }
            return null
          })
        },
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
        headers: {
          get: vi.fn((header) => {
            if (header === 'content-type') {
              return 'application/json'
            }
            return null
          })
        },
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

      // The normalizeReportDTO function adds additional fields with default values
      // So we check that the important fields match instead of exact equality
      expect(result).toMatchObject({
        id: 1,
        tipo_reporte: 'calidad',
        estado: 'completado',
        fecha_generacion: '2024-01-01'
      })
      // Verify that normalized fields exist
      expect(result).toHaveProperty('tipo_reporte_display')
      expect(result).toHaveProperty('estado_display')
      expect(result).toHaveProperty('formato')
      expect(result).toHaveProperty('formato_display')
    })

    it('should handle error when fetching report details', async () => {
      const errorResponse = {
        ok: false,
        status: 404,
        statusText: 'Not Found',
        headers: {
          get: vi.fn((header) => {
            if (header === 'content-type') {
              return 'application/json'
            }
            return null
          })
        },
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
        ...reportData,
        estado: 'generando'
      }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: new Headers({
          'content-type': 'application/json'
        }),
        json: vi.fn().mockResolvedValue(mockCreatedReport)
      })

      const result = await reportsService.createReport(reportData)

      // buildReportRequestPayload always includes descripcion, parametros, and filtros with defaults
      const expectedPayload = {
        tipo_reporte: reportData.tipo_reporte || '',
        formato: reportData.formato || '',
        titulo: reportData.titulo || '',
        descripcion: reportData.descripcion || '',
        parametros: reportData.parametros || {},
        filtros: reportData.filtros || reportData.filtros_aplicados || {}
      }

      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/reportes'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token'
          }),
          body: JSON.stringify(expectedPayload)
        })
      )

      // normalizeReportDTO adds many default fields, so we check the important ones
      expect(result).toMatchObject({
        id: 1,
        tipo_reporte: 'calidad',
        formato: 'pdf',
        titulo: 'Test Report',
        estado: 'generando'
      })
      expect(result.tipo_reporte_display).toBe('calidad')
      expect(result.formato_display).toBe('PDF')
      expect(result.estado_display).toBe('generando')
    })

    it('should handle error when creating report', async () => {
      const reportData = { tipo_reporte: 'calidad' }

      const errorResponse = {
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        headers: {
          get: vi.fn((header) => {
            if (header === 'content-type') {
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
        headers: {
          get: vi.fn((header) => {
            if (header === 'content-type') {
              return 'application/json'
            }
            return null
          })
        },
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
        headers: {
          get: vi.fn((header) => {
            if (header === 'content-type') {
              return 'application/json'
            }
            return null
          })
        },
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
        headers: {
          get: vi.fn((header) => {
            if (header === 'content-type') {
              return 'application/json'
            }
            return null
          })
        },
        json: vi.fn().mockResolvedValue({ error: 'Cannot delete' })
      }

      globalThis.fetch.mockResolvedValue(errorResponse)

      // The service throws the error from errorData.error if it exists
      await expect(reportsService.deleteReport(1)).rejects.toThrow('Cannot delete')
    })
  })

  describe('getReportsStats', () => {
    it('should fetch reports stats successfully', async () => {
      // Mock API response with properties that normalizeReportStatsResponse expects
      const mockApiResponse = {
        total_reportes: 100,
        reportes_completados: 80,
        reportes_generando: 15,
        reportes_fallidos: 5,
        reportsChange: 10,
        completedChange: 5,
        inProgressChange: 2,
        errorChange: 1,
        reportes_por_tipo: {},
        reportes_por_formato: {},
        reportes_recientes: []
      }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: {
          get: vi.fn((header) => {
            if (header === 'content-type') {
              return 'application/json'
            }
            return null
          })
        },
        json: vi.fn().mockResolvedValue(mockApiResponse)
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

      // The normalizeReportStatsResponse function transforms the API response
      expect(result).toMatchObject({
        totalReports: 100,
        completedReports: 80,
        inProgressReports: 15,
        errorReports: 5,
        reportsChange: 10,
        completedChange: 5,
        inProgressChange: 2,
        errorChange: 1
      })
      expect(result).toHaveProperty('reportsByType')
      expect(result).toHaveProperty('reportsByFormat')
      expect(result).toHaveProperty('recentReports')
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
        headers: {
          get: vi.fn((header) => {
            if (header === 'content-type') {
              return 'application/json'
            }
            return null
          })
        },
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
        headers: {
          get: vi.fn((header) => {
            if (header === 'content-type') {
              return 'application/json'
            }
            return null
          })
        },
        json: vi.fn().mockResolvedValue(mockReport)
      })

      const result = await reportsService.generateQualityReport(title, description, filters)

      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/reportes'),
        expect.objectContaining({
          method: 'POST',
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
        headers: {
          get: vi.fn((header) => {
            if (header === 'content-type') {
              return 'application/json'
            }
            return null
          })
        },
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
        headers: {
          get: vi.fn((header) => {
            if (header === 'content-type') {
              return 'application/json'
            }
            return null
          })
        },
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
        headers: {
          get: vi.fn((header) => {
            if (header === 'content-type') {
              return 'application/json'
            }
            return null
          })
        },
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
        headers: {
          get: vi.fn((header) => {
            if (header === 'content-type') {
              return 'application/json'
            }
            return null
          })
        },
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

