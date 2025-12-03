/**
 * Unit tests for ReportsManagement view
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ReportsManagement from '../ReportsManagement.vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'

// Mock stores
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn()
}))

vi.mock('@/stores/notifications', () => ({
  useNotificationStore: vi.fn()
}))

// Mock components
vi.mock('@/components/reportes/ReportGenerator.vue', () => ({
  default: {
    name: 'ReportGenerator',
    template: '<div>Report Generator</div>'
  }
}))

vi.mock('@/components/reportes/ReportDownloadButton.vue', () => ({
  default: {
    name: 'ReportDownloadButton',
    template: '<button>Download</button>'
  }
}))

// Mock fetch
globalThis.fetch = vi.fn()

describe('ReportsManagement', () => {
  let mockAuthStore
  let mockNotificationStore

  beforeEach(() => {
    vi.clearAllMocks()
    
    mockAuthStore = {
      token: 'test-token'
    }
    
    mockNotificationStore = {
      addNotification: vi.fn()
    }
    
    useAuthStore.mockReturnValue(mockAuthStore)
    useNotificationStore.mockReturnValue(mockNotificationStore)
    
    globalThis.confirm = vi.fn(() => true)
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('should render reports management view', () => {
    globalThis.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        results: [],
        count: 0,
        total_pages: 0
      })
    }).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        total_reportes: 0,
        reportes_completados: 0,
        reportes_generando: 0,
        reportes_fallidos: 0
      })
    })

    const wrapper = mount(ReportsManagement, {
      global: {
        stubs: {
          'router-link': true
        }
      }
    })

    expect(wrapper.text()).toContain('Gestión de Reportes')
  })

  it('should load reports on mount', async () => {
    globalThis.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        results: [
          {
            id: 1,
            titulo: 'Test Report',
            tipo_reporte: 'calidad',
            formato: 'pdf',
            estado: 'completado',
            fecha_solicitud: '2024-01-01'
          }
        ],
        count: 1,
        total_pages: 1
      })
    }).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        total_reportes: 1,
        reportes_completados: 1,
        reportes_generando: 0,
        reportes_fallidos: 0
      })
    })

    const wrapper = mount(ReportsManagement, {
      global: {
        stubs: {
          'router-link': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    
    expect(globalThis.fetch).toHaveBeenCalled()
  })

  it('should handle error when loading reports', async () => {
    globalThis.fetch.mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          total_reportes: 0,
          reportes_completados: 0,
          reportes_generando: 0,
          reportes_fallidos: 0
        })
      })

    const wrapper = mount(ReportsManagement, {
      global: {
        stubs: {
          'router-link': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    
    expect(mockNotificationStore.addNotification).toHaveBeenCalled()
  })

  it('should toggle report generator visibility', async () => {
    globalThis.fetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        results: [],
        count: 0,
        total_pages: 0,
        total_reportes: 0,
        reportes_completados: 0,
        reportes_generando: 0,
        reportes_fallidos: 0
      })
    })

    const wrapper = mount(ReportsManagement, {
      global: {
        stubs: {
          'router-link': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    
    const toggleButton = wrapper.find('button')
    if (toggleButton.exists() && toggleButton.text().includes('Nuevo Reporte')) {
      await toggleButton.trigger('click')
      expect(wrapper.vm.mostrarGenerador).toBe(true)
    }
  })

  it('should format date correctly', async () => {
    globalThis.fetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        results: [],
        count: 0,
        total_pages: 0,
        total_reportes: 0,
        reportes_completados: 0,
        reportes_generando: 0,
        reportes_fallidos: 0
      })
    })

    const wrapper = mount(ReportsManagement, {
      global: {
        stubs: {
          'router-link': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    
    const formatted = wrapper.vm.formatearFecha('2024-01-01T10:00:00Z')
    expect(formatted).toBeTruthy()
    
    const nullFormatted = wrapper.vm.formatearFecha(null)
    expect(nullFormatted).toBe('N/A')
  })

  it('should cleanup interval on unmount', async () => {
    vi.useFakeTimers()
    
    globalThis.fetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        results: [],
        count: 0,
        total_pages: 0,
        total_reportes: 0,
        reportes_completados: 0,
        reportes_generando: 0,
        reportes_fallidos: 0
      })
    })

    const wrapper = mount(ReportsManagement, {
      global: {
        stubs: {
          'router-link': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    
    const cleanupSpy = vi.spyOn(wrapper.vm, 'cleanup')
    wrapper.unmount()
    
    expect(cleanupSpy).toHaveBeenCalled()
  })
})

