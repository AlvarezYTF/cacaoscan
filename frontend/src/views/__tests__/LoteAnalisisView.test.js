import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import LoteAnalisisView from '../LoteAnalisisView.vue'

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    accessToken: 'mock-token'
  })
}))

vi.mock('@/stores/notifications', () => ({
  useNotificationStore: () => ({
    showNotification: vi.fn()
  })
}))

globalThis.fetch = vi.fn()

describe('LoteAnalisisView', () => {
  let wrapper

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render loading state initially', () => {
    wrapper = mount(LoteAnalisisView, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    expect(wrapper.text()).toContain('Cargando')
  })

  it('should render error state when error occurs', async () => {
    globalThis.fetch.mockRejectedValueOnce(new Error('Network error'))
    
    wrapper = mount(LoteAnalisisView, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.text()).toContain('Error')
  })

  it('should render lote information when loaded', async () => {
    const mockLote = {
      id: 1,
      identificador: 'Lote A',
      variedad: 'Criollo',
      area_hectareas: 5.5,
      fecha_plantacion: '2024-01-01',
      finca: 1
    }

    globalThis.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockLote
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: [] })
      })

    wrapper = mount(LoteAnalisisView, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))

    expect(wrapper.text()).toContain('Lote A')
  })
})

