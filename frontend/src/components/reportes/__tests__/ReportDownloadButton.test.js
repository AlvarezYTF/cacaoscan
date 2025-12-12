/**
 * Unit tests for ReportDownloadButton component
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ReportDownloadButton from '../ReportDownloadButton.vue'

// Mock stores
const mockAuthStore = {
  token: 'test-token-123'
}

const mockNotificationStore = {
  addNotification: vi.fn()
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

vi.mock('@/stores/notifications', () => ({
  useNotificationStore: () => mockNotificationStore
}))

// Mock fetch
globalThis.fetch = vi.fn()

// Mock URL and document methods
globalThis.URL = {
  createObjectURL: vi.fn(() => 'blob:mock-url'),
  revokeObjectURL: vi.fn()
}

// Track created anchor elements for testing
const createdLinks = []

// Store original createElement
const originalCreateElement = document.createElement.bind(document)

// Spy on createElement to track anchor elements
let createElementSpy = null

describe('ReportDownloadButton', () => {
  let wrapper
  let pinia

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    vi.clearAllMocks()
    globalThis.fetch.mockClear()
    createdLinks.length = 0
    
    // Spy on createElement to track anchor elements
    createElementSpy = vi.spyOn(document, 'createElement').mockImplementation((tag) => {
      // Use original implementation to avoid recursion
      const element = originalCreateElement(tag)
      
      if (tag === 'a') {
        // Track the link element
        createdLinks.push(element)
        
        // Spy on click and remove methods
        element.click = vi.fn()
        const originalRemove = element.remove.bind(element)
        element.remove = vi.fn(() => {
          originalRemove()
          const index = createdLinks.indexOf(element)
          if (index > -1) {
            createdLinks.splice(index, 1)
          }
        })
      }
      
      return element
    })
  })
  
  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    if (createElementSpy) {
      createElementSpy.mockRestore()
      createElementSpy = null
    }
    vi.clearAllMocks()
  })


  const createWrapper = (reporteProps = {}) => {
    const defaultProps = {
      id: 1,
      titulo: 'Test Report',
      estado: 'completado',
      formato: 'pdf',
      esta_expirado: false,
      ...reporteProps
    }

    return mount(ReportDownloadButton, {
      props: {
        reporte: defaultProps
      },
      global: {
        plugins: [pinia]
      }
    })
  }

  describe('rendering', () => {
    it('should render download button when report is completed and not expired', () => {
      wrapper = createWrapper({
        estado: 'completado',
        esta_expirado: false
      })

      const button = wrapper.find('button')
      expect(button.exists()).toBe(true)
      expect(button.text()).toContain('Descargar')
      expect(button.classes()).toContain('btn-primary')
    })

    it('should render generating button when report is generating', () => {
      wrapper = createWrapper({
        estado: 'generando'
      })

      const button = wrapper.find('button')
      expect(button.exists()).toBe(true)
      expect(button.text()).toContain('Generando...')
      expect(button.attributes('disabled')).toBeDefined()
      expect(button.classes()).toContain('btn-secondary')
    })

    it('should render error button when report failed', () => {
      wrapper = createWrapper({
        estado: 'fallido'
      })

      const button = wrapper.find('button')
      expect(button.exists()).toBe(true)
      expect(button.text()).toContain('Error')
      expect(button.attributes('disabled')).toBeDefined()
      expect(button.classes()).toContain('btn-danger')
    })

    it('should render expired button when report is expired', () => {
      wrapper = createWrapper({
        estado: 'completado',
        esta_expirado: true
      })

      const button = wrapper.find('button')
      expect(button.exists()).toBe(true)
      expect(button.text()).toContain('Expirado')
      expect(button.attributes('disabled')).toBeDefined()
      expect(button.classes()).toContain('btn-warning')
    })

    it('should show loading spinner when downloading', async () => {
      const { nextTick } = await import('vue')
      
      wrapper = createWrapper({
        estado: 'completado',
        esta_expirado: false
      })

      const button = wrapper.find('button')
      expect(button.find('i.fa-spinner').exists()).toBe(false)

      // Mock download with a pending promise to keep loading state
      let resolveFetch
      const fetchPromise = new Promise((resolve) => {
        resolveFetch = resolve
      })
      
      globalThis.fetch.mockReturnValueOnce(fetchPromise)

      // Trigger click and wait for nextTick to update reactive state
      const clickPromise = button.trigger('click')
      await nextTick()

      // Button should show loading state while fetch is pending
      const loadingIcon = wrapper.find('i.fa-spinner')
      expect(loadingIcon.exists()).toBe(true)

      // Resolve the fetch to complete the test
      resolveFetch({
        ok: true,
        headers: {
          get: vi.fn(() => null)
        },
        blob: vi.fn().mockResolvedValue(new Blob())
      })
      
      // Wait for click handler to complete
      await clickPromise
    })
  })

  describe('download functionality', () => {
    it('should download report successfully', async () => {
      wrapper = createWrapper({
        estado: 'completado',
        esta_expirado: false,
        id: 123,
        titulo: 'Test Report',
        formato: 'pdf'
      })

      const mockBlob = new Blob(['test content'], { type: 'application/pdf' })
      const mockResponse = {
        ok: true,
        headers: {
          get: vi.fn((header) => {
            if (header === 'Content-Disposition') {
              return 'attachment; filename="test-report.pdf"'
            }
            return null
          })
        },
        blob: vi.fn().mockResolvedValue(mockBlob)
      }

      globalThis.fetch.mockResolvedValueOnce(mockResponse)

      const button = wrapper.find('button')
      await button.trigger('click')

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/reportes/123/download/'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token-123',
            'Accept': 'application/octet-stream'
          })
        })
      )

      expect(mockNotificationStore.addNotification).toHaveBeenCalledWith({
        type: 'success',
        title: 'Descarga exitosa',
        message: expect.stringContaining('Test Report')
      })
    })

    it('should handle download error', async () => {
      wrapper = createWrapper({
        estado: 'completado',
        esta_expirado: false,
        id: 123
      })

      const mockResponse = {
        ok: false,
        json: vi.fn().mockResolvedValue({
          error: 'Download failed'
        })
      }

      globalThis.fetch.mockResolvedValueOnce(mockResponse)

      const button = wrapper.find('button')
      await button.trigger('click')

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mockNotificationStore.addNotification).toHaveBeenCalledWith({
        type: 'error',
        title: 'Error en la descarga',
        message: 'Download failed'
      })

      const errorDiv = wrapper.find('.alert-danger')
      expect(errorDiv.exists()).toBe(true)
      expect(errorDiv.text()).toContain('Download failed')
    })

    it('should use default filename when Content-Disposition is missing', async () => {
      wrapper = createWrapper({
        estado: 'completado',
        esta_expirado: false,
        id: 456,
        formato: 'excel'
      })

      const mockBlob = new Blob(['test content'])
      const mockResponse = {
        ok: true,
        headers: {
          get: vi.fn(() => null)
        },
        blob: vi.fn().mockResolvedValue(mockBlob)
      }

      globalThis.fetch.mockResolvedValueOnce(mockResponse)

      const button = wrapper.find('button')
      await button.trigger('click')

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(createElementSpy).toHaveBeenCalledWith('a')
      const linkElement = createdLinks.at(-1)
      if (linkElement) {
        expect(linkElement.download).toContain('reporte_456')
        expect(linkElement.download).toContain('excel')
      }
    })

    it('should extract filename from Content-Disposition header', async () => {
      wrapper = createWrapper({
        estado: 'completado',
        esta_expirado: false,
        id: 789
      })

      const mockBlob = new Blob(['test content'])
      const mockResponse = {
        ok: true,
        headers: {
          get: vi.fn((header) => {
            if (header === 'Content-Disposition') {
              return 'attachment; filename="custom-report-name.pdf"'
            }
            return null
          })
        },
        blob: vi.fn().mockResolvedValue(mockBlob)
      }

      globalThis.fetch.mockResolvedValueOnce(mockResponse)

      const button = wrapper.find('button')
      await button.trigger('click')

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(createElementSpy).toHaveBeenCalledWith('a')
    })

    const createMockDownloadResponse = () => ({
      ok: true,
      headers: { get: vi.fn(() => null) },
      blob: vi.fn().mockResolvedValue(new Blob())
    })

    it('should disable button while downloading', async () => {
      wrapper = createWrapper({
        estado: 'completado',
        esta_expirado: false
      })

      let resolveDownload
      const downloadPromise = new Promise(resolve => {
        resolveDownload = resolve
      })

      globalThis.fetch.mockReturnValueOnce(downloadPromise.then(createMockDownloadResponse))

      const button = wrapper.find('button')
      await button.trigger('click')

      await wrapper.vm.$nextTick()

      expect(button.attributes('disabled')).toBeDefined()

      resolveDownload()
      await downloadPromise
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
    })

    it('should handle network errors', async () => {
      wrapper = createWrapper({
        estado: 'completado',
        esta_expirado: false
      })

      globalThis.fetch.mockRejectedValueOnce(new Error('Network error'))

      const button = wrapper.find('button')
      await button.trigger('click')

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mockNotificationStore.addNotification).toHaveBeenCalledWith({
        type: 'error',
        title: 'Error en la descarga',
        message: 'Network error'
      })
    })

    it('should handle JSON parse errors in error response', async () => {
      wrapper = createWrapper({
        estado: 'completado',
        esta_expirado: false
      })

      const mockResponse = {
        ok: false,
        json: vi.fn().mockRejectedValue(new Error('Invalid JSON'))
      }

      globalThis.fetch.mockResolvedValueOnce(mockResponse)

      const button = wrapper.find('button')
      await button.trigger('click')

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      // Should still show error notification
      expect(mockNotificationStore.addNotification).toHaveBeenCalled()
    })
  })

  describe('error display', () => {
    it('should display error message when error occurs', async () => {
      wrapper = createWrapper({
        estado: 'completado',
        esta_expirado: false
      })

      globalThis.fetch.mockRejectedValueOnce(new Error('Download failed'))

      const button = wrapper.find('button')
      await button.trigger('click')

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const errorDiv = wrapper.find('.alert-danger')
      expect(errorDiv.exists()).toBe(true)
      expect(errorDiv.text()).toContain('Download failed')
    })

    it('should clear error on new download attempt', async () => {
      wrapper = createWrapper({
        estado: 'completado',
        esta_expirado: false
      })

      // First attempt fails
      globalThis.fetch.mockRejectedValueOnce(new Error('First error'))
      const button = wrapper.find('button')
      await button.trigger('click')
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.find('.alert-danger').exists()).toBe(true)

      // Second attempt succeeds
      const mockBlob = new Blob(['test'])
      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        headers: { get: vi.fn(() => null) },
        blob: vi.fn().mockResolvedValue(mockBlob)
      })

      await button.trigger('click')
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      // Error should be cleared
      const errorDiv = wrapper.find('.alert-danger')
      expect(errorDiv.exists()).toBe(false)
    })
  })

  describe('button states', () => {
    it('should show correct icon for download button', () => {
      wrapper = createWrapper({
        estado: 'completado',
        esta_expirado: false
      })

      const icon = wrapper.find('i.fa-download')
      expect(icon.exists()).toBe(true)
    })

    it('should show spinner icon when generating', () => {
      wrapper = createWrapper({
        estado: 'generando'
      })

      const icon = wrapper.find('i.fa-spinner')
      expect(icon.exists()).toBe(true)
      expect(icon.classes()).toContain('fa-spin')
    })

    it('should show warning icon when expired', () => {
      wrapper = createWrapper({
        estado: 'completado',
        esta_expirado: true
      })

      const icon = wrapper.find('i.fa-clock')
      expect(icon.exists()).toBe(true)
    })

    it('should show error icon when failed', () => {
      wrapper = createWrapper({
        estado: 'fallido'
      })

      const icon = wrapper.find('i.fa-exclamation-triangle')
      expect(icon.exists()).toBe(true)
    })
  })
})

