import { describe, it, expect, beforeEach, vi } from 'vitest'
import api from '../api'
import {
  getActivityLogs,
  getLoginHistory,
  getAuditStats,
  generateAuditReport,
  getUserActivitySummary,
  formatActivityLog,
  formatLoginHistory,
  validateDateFilters,
  AUDIT_ACTION_TYPES,
  AUDIT_SEVERITY_LEVELS,
  AUDIT_CONFIG
} from '../auditApi'

vi.mock('../api', () => ({
  default: {
    get: vi.fn()
  }
}))

describe('auditApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getActivityLogs', () => {
    it('should fetch activity logs successfully', async () => {
      const mockResponse = {
        data: {
          results: [
            { id: 1, usuario: 'user1', accion: 'CREATE', fecha: '2024-01-01T10:00:00Z' },
            { id: 2, usuario: 'user2', accion: 'UPDATE', fecha: '2024-01-02T10:00:00Z' }
          ],
          count: 2
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await getActivityLogs({ page: 1, page_size: 50 })

      expect(api.get).toHaveBeenCalledWith('/audit/activity-logs/', { params: { page: 1, page_size: 50 } })
      expect(result.success).toBe(true)
      expect(result.data.results).toHaveLength(2)
    })

    it('should handle error when fetching activity logs', async () => {
      const error = {
        response: {
          data: {
            detail: 'Error message'
          }
        }
      }
      api.get.mockRejectedValue(error)

      const result = await getActivityLogs()

      expect(result.success).toBe(false)
      expect(result.error).toBe('Error message')
    })

    it('should handle error without response', async () => {
      const error = new Error('Network error')
      api.get.mockRejectedValue(error)

      const result = await getActivityLogs()

      expect(result.success).toBe(false)
      expect(result.error).toBe('Network error')
    })
  })

  describe('getLoginHistory', () => {
    it('should fetch login history successfully', async () => {
      const mockResponse = {
        data: {
          results: [
            { id: 1, usuario: 'user1', exitoso: true, fecha: '2024-01-01T10:00:00Z' },
            { id: 2, usuario: 'user2', exitoso: false, fecha: '2024-01-02T10:00:00Z' }
          ],
          count: 2
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await getLoginHistory({ page: 1 })

      expect(api.get).toHaveBeenCalledWith('/audit/login-history/', { params: { page: 1 } })
      expect(result.success).toBe(true)
      expect(result.data.results).toHaveLength(2)
    })

    it('should handle error when fetching login history', async () => {
      const error = {
        response: {
          data: {
            error: 'Error message'
          }
        }
      }
      api.get.mockRejectedValue(error)

      const result = await getLoginHistory()

      expect(result.success).toBe(false)
      expect(result.error).toBe('Error message')
    })
  })

  describe('getAuditStats', () => {
    it('should fetch audit stats successfully', async () => {
      const mockResponse = {
        data: {
          total_activities: 100,
          total_logins: 50
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await getAuditStats({ fecha_desde: '2024-01-01' })

      expect(api.get).toHaveBeenCalledWith('/audit/stats/', { params: { fecha_desde: '2024-01-01' } })
      expect(result.success).toBe(true)
      expect(result.data.total_activities).toBe(100)
    })

    it('should handle error when fetching stats', async () => {
      const error = {
        response: {
          data: {
            detail: 'Error message'
          }
        }
      }
      api.get.mockRejectedValue(error)

      const result = await getAuditStats()

      expect(result.success).toBe(false)
      expect(result.error).toBe('Error message')
    })
  })

  describe('generateAuditReport', () => {
    it('should generate PDF report successfully', async () => {
      const mockBlob = new Blob(['pdf content'], { type: 'application/pdf' })
      const mockResponse = {
        data: mockBlob,
        headers: {}
      }
      api.get.mockResolvedValue(mockResponse)

      // Mock URL.createObjectURL
      globalThis.URL.createObjectURL = vi.fn(() => 'blob:mock-url')

      const result = await generateAuditReport({
        tipo: 'activity',
        formato: 'pdf',
        fecha_desde: '2024-01-01',
        fecha_hasta: '2024-01-31'
      })

      expect(api.get).toHaveBeenCalledWith('/audit/activity-logs/export/', {
        params: {
          formato: 'pdf',
          fecha_desde: '2024-01-01',
          fecha_hasta: '2024-01-31'
        },
        responseType: 'blob'
      })
      expect(result.success).toBe(true)
      expect(result.data.url).toBe('blob:mock-url')
      expect(result.data.filename).toContain('auditoria_activity')
    })

    it('should generate JSON report successfully', async () => {
      const mockResponse = {
        data: { results: [] }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await generateAuditReport({
        tipo: 'login',
        formato: 'json',
        fecha_desde: '2024-01-01'
      })

      expect(api.get).toHaveBeenCalledWith('/audit/login-history/export/', {
        params: {
          formato: 'json',
          fecha_desde: '2024-01-01',
          fecha_hasta: undefined
        },
        responseType: 'json'
      })
      expect(result.success).toBe(true)
    })

    it('should handle error when generating report', async () => {
      const error = {
        response: {
          data: {
            detail: 'Error message'
          }
        }
      }
      api.get.mockRejectedValue(error)

      const result = await generateAuditReport({ tipo: 'activity', formato: 'pdf' })

      expect(result.success).toBe(false)
      expect(result.error).toBe('Error message')
    })
  })

  describe('getUserActivitySummary', () => {
    it('should fetch user activity summary successfully', async () => {
      const mockResponse = {
        data: {
          total_activities: 10,
          last_activity: '2024-01-01T10:00:00Z'
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await getUserActivitySummary(1, { fecha_desde: '2024-01-01' })

      expect(api.get).toHaveBeenCalledWith('/audit/users/1/summary/', { params: { fecha_desde: '2024-01-01' } })
      expect(result.success).toBe(true)
      expect(result.data.total_activities).toBe(10)
    })

    it('should throw error if userId is not provided', async () => {
      await expect(getUserActivitySummary(null)).rejects.toThrow('ID de usuario requerido')
    })

    it('should handle error when fetching user summary', async () => {
      const error = {
        response: {
          data: {
            detail: 'Error message'
          }
        }
      }
      api.get.mockRejectedValue(error)

      const result = await getUserActivitySummary(1)

      expect(result.success).toBe(false)
      expect(result.error).toBe('Error message')
    })
  })

  describe('formatActivityLog', () => {
    // Use TEST-NET-1 reserved IP (192.0.2.x) - safe for testing
    const TEST_IP = '192.0.2.10'

    it('should format activity log correctly', () => {
      const log = {
        id: 1,
        usuario: 'user1',
        accion: 'CREATE',
        descripcion: 'Created item',
        direccion_ip: TEST_IP,
        user_agent: 'Mozilla/5.0',
        fecha: '2024-01-01T10:00:00Z',
        metadata: { key: 'value' }
      }

      const formatted = formatActivityLog(log)

      expect(formatted.id).toBe(1)
      expect(formatted.usuario).toBe('user1')
      expect(formatted.fecha_formateada).toBeDefined()
      expect(formatted.es_reciente).toBeDefined()
      expect(formatted.metadata).toEqual({ key: 'value' })
    })

    it('should use default usuario_nombre when not provided', () => {
      const log = {
        id: 1,
        usuario: 'user1',
        accion: 'CREATE',
        fecha: '2024-01-01T10:00:00Z'
      }

      const formatted = formatActivityLog(log)

      expect(formatted.usuario_nombre).toBe('Usuario desconocido')
    })

    it('should handle recent log correctly', () => {
      const recentDate = new Date(Date.now() - 30 * 60 * 1000).toISOString()
      const log = {
        id: 1,
        usuario: 'user1',
        accion: 'CREATE',
        fecha: recentDate
      }

      const formatted = formatActivityLog(log)

      expect(formatted.es_reciente).toBe(true)
    })
  })

  describe('formatLoginHistory', () => {
    // Use TEST-NET-1 reserved IP (192.0.2.x) - safe for testing
    const TEST_IP = '192.0.2.10'

    it('should format login history correctly for successful login', () => {
      const login = {
        id: 1,
        usuario: 'user1',
        exitoso: true,
        direccion_ip: TEST_IP,
        fecha: '2024-01-01T10:00:00Z'
      }

      const formatted = formatLoginHistory(login)

      expect(formatted.id).toBe(1)
      expect(formatted.estado_visual).toBe('success')
      expect(formatted.icono).toBe('check-circle')
      expect(formatted.fecha_formateada).toBeDefined()
    })

    it('should format login history correctly for failed login', () => {
      const login = {
        id: 1,
        usuario: 'user1',
        exitoso: false,
        razon_falla: 'Invalid credentials',
        fecha: '2024-01-01T10:00:00Z'
      }

      const formatted = formatLoginHistory(login)

      expect(formatted.estado_visual).toBe('danger')
      expect(formatted.icono).toBe('times-circle')
      expect(formatted.razon_falla).toBe('Invalid credentials')
    })
  })

  describe('validateDateFilters', () => {
    it('should validate correct date range', () => {
      const params = {
        fecha_desde: '2024-01-01',
        fecha_hasta: '2024-01-31'
      }

      const result = validateDateFilters(params)

      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })

    it('should reject invalid date range (start after end)', () => {
      const params = {
        fecha_desde: '2024-01-31',
        fecha_hasta: '2024-01-01'
      }

      const result = validateDateFilters(params)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('La fecha de inicio no puede ser posterior a la fecha de fin')
    })

    it('should reject date range exceeding 1 year', () => {
      const params = {
        fecha_desde: '2024-01-01',
        fecha_hasta: '2025-02-01'
      }

      const result = validateDateFilters(params)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('El rango de fechas no puede exceder 1 año')
    })

    it('should validate when only one date is provided', () => {
      const params = {
        fecha_desde: '2024-01-01'
      }

      const result = validateDateFilters(params)

      expect(result.isValid).toBe(true)
    })

    it('should validate when no dates are provided', () => {
      const result = validateDateFilters({})

      expect(result.isValid).toBe(true)
    })
  })

  describe('Constants', () => {
    it('should export AUDIT_ACTION_TYPES', () => {
      expect(AUDIT_ACTION_TYPES.LOGIN).toBe('login')
      expect(AUDIT_ACTION_TYPES.CREATE).toBe('create')
      expect(AUDIT_ACTION_TYPES.DELETE).toBe('delete')
    })

    it('should export AUDIT_SEVERITY_LEVELS', () => {
      expect(AUDIT_SEVERITY_LEVELS.INFO).toBe('info')
      expect(AUDIT_SEVERITY_LEVELS.ERROR).toBe('error')
      expect(AUDIT_SEVERITY_LEVELS.CRITICAL).toBe('critical')
    })

    it('should export AUDIT_CONFIG', () => {
      expect(AUDIT_CONFIG.LOGS_REFRESH_INTERVAL).toBe(30000)
      expect(AUDIT_CONFIG.DEFAULT_PAGE_SIZE).toBe(50)
      expect(AUDIT_CONFIG.ACTION_COLORS).toBeDefined()
      expect(AUDIT_CONFIG.ACTION_ICONS).toBeDefined()
    })
  })
})

