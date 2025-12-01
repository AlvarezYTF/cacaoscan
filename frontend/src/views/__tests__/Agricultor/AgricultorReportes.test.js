import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
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

// Mock vue-router
const mockRouter = {
  push: vi.fn(),
  replace: vi.fn(),
  go: vi.fn(),
  back: vi.fn(),
  forward: vi.fn(),
  currentRoute: {
    value: {
      path: '/agricultor/reportes',
      name: 'agricultor-reportes',
      params: {},
      query: {},
      meta: {}
    }
  },
  isReady: vi.fn().mockResolvedValue(true)
}

const mockRoute = {
  path: '/agricultor/reportes',
  name: 'agricultor-reportes',
  params: {},
  query: {},
  meta: {}
}

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRouter: () => mockRouter,
    useRoute: () => mockRoute
  }
})

describe('AgricultorReportes', () => {
  let wrapper

  const globalMocks = {
    $route: mockRoute,
    $router: mockRouter
  }

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
  })

  it('should render reportes view', () => {
    wrapper = mount(AgricultorReportes, {
      global: {
        stubs: {
          'router-link': true,
          'router-view': true,
          Sidebar: { template: '<div>Sidebar</div>' }
        },
        mocks: globalMocks
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display reportes title', () => {
    wrapper = mount(AgricultorReportes, {
      global: {
        stubs: {
          'router-link': true,
          'router-view': true,
          Sidebar: { template: '<div>Sidebar</div>' }
        },
        mocks: globalMocks
      }
    })

    const text = wrapper.text()
    expect(text.includes('Reportes') || text.includes('reportes')).toBe(true)
  })
})

