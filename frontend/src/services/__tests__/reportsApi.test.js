import { describe, it, expect, beforeEach, vi } from 'vitest'
import api from '../api'
import reportsApi from '../reportsApi'

vi.mock('../api', () => ({
  default: {
    get: vi.fn()
  }
}))

// Mock DOM methods
globalThis.URL.createObjectURL = vi.fn(() => 'blob:mock-url')
globalThis.URL.revokeObjectURL = vi.fn()
globalThis.document.createElement = vi.fn(() => {
  const link = {
    href: '',
    download: '',
    style: {},
    setAttribute: vi.fn(),
    click: vi.fn(),
    remove: vi.fn()
  }
  return link
})
globalThis.document.body.appendChild = vi.fn()
globalThis.setTimeout = vi.fn((fn) => {
  fn()
  return 1
})

describe('reportsApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('downloadReporteAgricultores', () => {
    it('should download agricultores report successfully', async () => {
      const mockBlob = new Blob(['excel content'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
      const mockResponse = {
        data: mockBlob,
        headers: {
          'content-disposition': 'attachment; filename="reporte_agricultores.xlsx"'
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await reportsApi.downloadReporteAgricultores()

      expect(api.get).toHaveBeenCalledWith('/reports/agricultores/', {
        responseType: 'blob',
        headers: {
          'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
      })
      expect(result.success).toBe(true)
      expect(globalThis.URL.createObjectURL).toHaveBeenCalledWith(mockBlob)
    })

    it('should handle error when downloading report', async () => {
      const error = {
        response: {
          data: new Blob([JSON.stringify({ error: 'Server error' })], { type: 'application/json' })
        }
      }
      api.get.mockRejectedValue(error)

      // Mock blob.text() method
      error.response.data.text = vi.fn().mockResolvedValue(JSON.stringify({ error: 'Server error' }))

      await expect(reportsApi.downloadReporteAgricultores()).rejects.toThrow('Server error')
    })

    it('should throw error if response is not a blob', async () => {
      const mockResponse = {
        data: 'not a blob'
      }
      api.get.mockResolvedValue(mockResponse)

      await expect(reportsApi.downloadReporteAgricultores()).rejects.toThrow('La respuesta del servidor no es un archivo válido')
    })
  })

  describe('downloadReporteUsuarios', () => {
    it('should download usuarios report successfully', async () => {
      const mockBlob = new Blob(['excel content'])
      const mockResponse = {
        data: mockBlob
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await reportsApi.downloadReporteUsuarios()

      expect(api.get).toHaveBeenCalledWith('/reports/usuarios/', {
        responseType: 'blob'
      })
      expect(result.success).toBe(true)
      expect(globalThis.URL.createObjectURL).toHaveBeenCalled()
    })

    it('should handle error when downloading usuarios report', async () => {
      const error = new Error('Network error')
      api.get.mockRejectedValue(error)

      await expect(reportsApi.downloadReporteUsuarios()).rejects.toThrow('Network error')
    })
  })

  describe('parseErrorBlob edge cases', () => {
    it('should handle error with JSON blob response', async () => {
      const errorBlob = new Blob([JSON.stringify({ error: 'Server error message' })], { 
        type: 'application/json' 
      })
      errorBlob.text = vi.fn().mockResolvedValue(JSON.stringify({ error: 'Server error message' }))
      
      const error = {
        response: {
          data: errorBlob
        }
      }
      api.get.mockRejectedValue(error)

      await expect(reportsApi.downloadReporteAgricultores()).rejects.toThrow('Server error message')
    })

    it('should handle error with message field in JSON', async () => {
      const errorBlob = new Blob([JSON.stringify({ message: 'Error message' })], { 
        type: 'application/json' 
      })
      errorBlob.text = vi.fn().mockResolvedValue(JSON.stringify({ message: 'Error message' }))
      
      const error = {
        response: {
          data: errorBlob
        }
      }
      api.get.mockRejectedValue(error)

      await expect(reportsApi.downloadReporteAgricultores()).rejects.toThrow('Error message')
    })

    it('should handle error with invalid JSON blob', async () => {
      const errorBlob = new Blob(['invalid json'], { type: 'application/json' })
      errorBlob.text = vi.fn().mockResolvedValue('invalid json')
      
      const error = {
        response: {
          data: errorBlob
        }
      }
      api.get.mockRejectedValue(error)
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})

      await expect(reportsApi.downloadReporteAgricultores()).rejects.toThrow()

      expect(consoleError).toHaveBeenCalled()
      consoleError.mockRestore()
    })

    it('should handle error with non-blob response data', async () => {
      const error = {
        response: {
          data: {
            error: 'Error message from server'
          }
        }
      }
      api.get.mockRejectedValue(error)

      await expect(reportsApi.downloadReporteAgricultores()).rejects.toThrow('Error message from server')
    })

    it('should handle error with message in response data', async () => {
      const error = {
        response: {
          data: {
            message: 'Error message'
          }
        }
      }
      api.get.mockRejectedValue(error)

      await expect(reportsApi.downloadReporteAgricultores()).rejects.toThrow('Error message')
    })

    it('should handle error without response', async () => {
      const error = new Error('Network error')
      api.get.mockRejectedValue(error)

      await expect(reportsApi.downloadReporteAgricultores()).rejects.toThrow('Network error')
    })

    it('should extract filename from Content-Disposition header', async () => {
      const mockBlob = new Blob(['excel content'], { 
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      })
      const mockResponse = {
        data: mockBlob,
        headers: {
          'content-disposition': 'attachment; filename="custom_report.xlsx"'
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const link = {
        href: '',
        download: '',
        style: {},
        setAttribute: vi.fn(),
        click: vi.fn(),
        remove: vi.fn()
      }
      globalThis.document.createElement.mockReturnValue(link)

      await reportsApi.downloadReporteAgricultores()

      expect(link.setAttribute).toHaveBeenCalledWith('download', 'custom_report.xlsx')
    })

    it('should handle filename with quotes in Content-Disposition', async () => {
      const mockBlob = new Blob(['excel content'], { 
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      })
      const mockResponse = {
        data: mockBlob,
        headers: {
          'content-disposition': 'attachment; filename=\'quoted_file.xlsx\''
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const link = {
        href: '',
        download: '',
        style: {},
        setAttribute: vi.fn(),
        click: vi.fn(),
        remove: vi.fn()
      }
      globalThis.document.createElement.mockReturnValue(link)

      await reportsApi.downloadReporteAgricultores()

      expect(link.setAttribute).toHaveBeenCalled()
    })

    it('should use default filename if no Content-Disposition', async () => {
      const mockBlob = new Blob(['excel content'], { 
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      })
      const mockResponse = {
        data: mockBlob,
        headers: {}
      }
      api.get.mockResolvedValue(mockResponse)

      const link = {
        href: '',
        download: '',
        style: {},
        setAttribute: vi.fn(),
        click: vi.fn(),
        remove: vi.fn()
      }
      globalThis.document.createElement.mockReturnValue(link)

      await reportsApi.downloadReporteAgricultores()

      expect(link.setAttribute).toHaveBeenCalled()
      const downloadCall = link.setAttribute.mock.calls.find(call => call[0] === 'download')
      expect(downloadCall[1]).toContain('reporte_agricultores')
    })
  })
})

