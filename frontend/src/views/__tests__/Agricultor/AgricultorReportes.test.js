import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import AgricultorReportes from '../../Agricultor/AgricultorReportes.vue'

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

describe('AgricultorReportes', () => {
  let router
  let wrapper

  beforeEach(() => {
    setActivePinia(createPinia())
    router = createRouter({
      history: createWebHistory(),
      routes: [{ path: '/', component: AgricultorReportes }]
    })
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render reportes view', () => {
    wrapper = mount(AgricultorReportes, {
      global: {
        plugins: [router],
        stubs: {
          'router-link': true,
          'router-view': true,
          Sidebar: { template: '<div>Sidebar</div>' }
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display reportes title', () => {
    wrapper = mount(AgricultorReportes, {
      global: {
        plugins: [router],
        stubs: {
          'router-link': true,
          'router-view': true,
          Sidebar: { template: '<div>Sidebar</div>' }
        }
      }
    })

    const text = wrapper.text()
    expect(text.includes('Reportes') || text.includes('reportes')).toBe(true)
  })
})

