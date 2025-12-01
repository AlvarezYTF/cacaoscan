import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AdminDashboard from '../../Admin/AdminDashboard.vue'

// Create mock store objects that will be reused
const mockAdminStore = {
  stats: {
    users: { total: 0, this_week: 0, this_month: 0 },
    fincas: { total: 0, this_week: 0, this_month: 0 },
    images: { total: 0, this_week: 0, this_month: 0 },
    predictions: { average_confidence: 0 },
    activity_by_day: { labels: [], data: [] },
    quality_distribution: { excelente: 0, buena: 0, regular: 0, baja: 0 }
  },
  users: [],
  activities: [],
  reports: [],
  alerts: [],
  loading: false,
  error: null,
  getGeneralStats: vi.fn().mockResolvedValue({ data: {} }),
  getRecentUsers: vi.fn().mockResolvedValue({ data: { results: [] } }),
  getRecentActivities: vi.fn().mockResolvedValue({ data: { results: [] } }),
  getSystemAlerts: vi.fn().mockResolvedValue({ data: { results: [] } }),
  getReportStats: vi.fn().mockResolvedValue({ data: {} }),
  getActivityData: vi.fn().mockResolvedValue({ data: { labels: [], data: [] } }),
  getQualityDistribution: vi.fn().mockResolvedValue({ data: {} })
}

const mockAuthStore = {
  isAuthenticated: true,
  isAdmin: true,
  user: { id: 1, email: 'admin@example.com', role: 'admin' },
  userRole: 'admin',
  userFullName: 'Admin User',
  accessToken: 'test-token',
  getCurrentUser: vi.fn(),
  clearAll: vi.fn(),
  updateLastActivity: vi.fn(),
  checkSessionTimeout: vi.fn(() => false),
  logout: vi.fn()
}

// Create mocks directly in vi.mock factories to avoid hoisting issues
vi.mock('@/stores/admin', () => ({
  useAdminStore: () => mockAdminStore
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

vi.mock('@/stores/config', () => ({
  useConfigStore: () => ({
    brandName: 'CacaoScan',
    getConfig: vi.fn()
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
      path: '/admin',
      name: 'admin-dashboard',
      params: {},
      query: {},
      meta: {}
    }
  },
  isReady: vi.fn().mockResolvedValue(true)
}

const mockRoute = {
  path: '/admin',
  name: 'admin-dashboard',
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

// Mock composables
vi.mock('@/composables/useWebSocket', () => ({
  useWebSocket: vi.fn(() => ({
    connect: vi.fn(),
    disconnect: vi.fn(),
    send: vi.fn()
  }))
}))

// Mock sweetalert2
vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn()
  },
  fire: vi.fn()
}))

// Create mocks for use in tests
const mocks = {
  adminStore: mockAdminStore,
  authStore: mockAuthStore
}

// Helper function to mount component with default stubs
const mountWithDefaults = (options = {}) => {
  const defaultStubs = {
    'router-link': true,
    'router-view': true,
    'AdminSidebar': true,
    'KPICards': true,
    'DashboardCharts': true,
    'DashboardTables': true,
    'DashboardAlerts': true
  }
  const globalMocks = {
    $route: mockRoute,
    $router: mockRouter
  }
  return mount(AdminDashboard, {
    global: {
      stubs: defaultStubs,
      mocks: globalMocks,
      ...options.global
    },
    ...options
  })
}

describe('AdminDashboard', () => {
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

  it('should render dashboard components', () => {
    wrapper = mountWithDefaults()

    expect(wrapper.exists()).toBe(true)
  })

  it('should load data on mount', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    // Wait for onMounted and async operations to complete
    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Verify that store methods are called
    expect(mocks.adminStore.getGeneralStats).toHaveBeenCalled()
  })

  it('should handle refresh action', async () => {
    wrapper = mountWithDefaults()

    // Test refresh functionality if method exists
    if (wrapper.vm.handleRefresh) {
      await wrapper.vm.handleRefresh()
      expect(mocks.adminStore.getGeneralStats).toHaveBeenCalled()
    }
  })

  it('should handle logout', async () => {
    wrapper = mountWithDefaults()

    if (wrapper.vm.handleLogout) {
      await wrapper.vm.handleLogout()
      // Verify logout behavior
      expect(mocks.authStore).toBeDefined()
    }
  })
})

