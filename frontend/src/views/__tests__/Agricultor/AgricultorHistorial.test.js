import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
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
  let router
  let wrapper

  beforeEach(() => {
    setActivePinia(createPinia())
    router = createRouter({
      history: createWebHistory(),
      routes: [{ path: '/', component: AgricultorHistorial }]
    })
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render historial view', () => {
    wrapper = mount(AgricultorHistorial, {
      global: {
        plugins: [router],
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
        plugins: [router],
        stubs: {
          'router-link': true,
          'router-view': true,
          Sidebar: { template: '<div>Sidebar</div>' },
          ImageHistoryCard: { template: '<div>ImageHistoryCard</div>' }
        }
      }
    })

    const text = wrapper.text()
    expect(text.includes('Historial') || text.includes('Análisis')).toBe(true)
  })
})

