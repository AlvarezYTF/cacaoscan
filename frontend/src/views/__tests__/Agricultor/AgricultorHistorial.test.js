import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AgricultorHistorial from '../../Agricultor/AgricultorHistorial.vue'

// Mock vue-router composables to prevent router redefinition errors
const mockRouter = {
  push: vi.fn(),
  replace: vi.fn(),
  go: vi.fn(),
  back: vi.fn(),
  forward: vi.fn(),
  currentRoute: {
    value: {
      path: '/agricultor/historial',
      name: 'AgricultorHistorial',
      params: {},
      query: {},
      meta: {}
    }
  },
  isReady: vi.fn().mockResolvedValue(true)
}

const mockRoute = {
  path: '/agricultor/historial',
  name: 'AgricultorHistorial',
  params: {},
  query: {},
  meta: {}
}

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRoute: () => mockRoute,
    useRouter: () => mockRouter
  }
})

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
        }
      }
    })

    const text = wrapper.text()
    expect(text.includes('Historial') || text.includes('Análisis')).toBe(true)
  })
})

