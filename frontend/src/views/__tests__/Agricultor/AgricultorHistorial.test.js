import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, config } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AgricultorHistorial from '../../Agricultor/AgricultorHistorial.vue'

vi.mock('@/composables/useImageStats', () => ({
  useImageStats: () => ({
    fetchImages: vi.fn().mockResolvedValue({ data: { results: [] } })
  })
}))

vi.mock('@/composables/useSidebarNavigation', () => ({
  useSidebarNavigation: () => ({
    isSidebarCollapsed: false,
    userName: 'Test User',
    userRole: 'agricultor',
    handleMenuClick: vi.fn(),
    toggleSidebarCollapse: vi.fn(),
    handleLogout: vi.fn()
  })
}))

describe('AgricultorHistorial', () => {
  let wrapper
  const originalPlugins = config.global.plugins

  beforeEach(() => {
    setActivePinia(createPinia())
    config.global.plugins = []
    vi.clearAllMocks()
  })

  afterEach(() => {
    config.global.plugins = originalPlugins
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
  })

  it('should render historial view', () => {
    wrapper = mount(AgricultorHistorial, {
      global: {
        stubs: {
          'router-link': true,
          'router-view': true,
          Sidebar: { template: '<div>Sidebar</div>' },
          ImageHistoryCard: { template: '<div>ImageHistoryCard</div>' }
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display historial title', () => {
    wrapper = mount(AgricultorHistorial, {
      global: {
        stubs: {
          'router-link': true,
          'router-view': true,
          Sidebar: { template: '<div>Sidebar</div>' },
          ImageHistoryCard: { template: '<div>ImageHistoryCard</div>' }
        },
        mocks: globalMocks
      }
    })

    const text = wrapper.text()
    expect(text.includes('Historial') || text.includes('Análisis')).toBe(true)
  })
})

