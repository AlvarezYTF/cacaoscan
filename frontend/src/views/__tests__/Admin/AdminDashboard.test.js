import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Swal from 'sweetalert2'
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
  user: { id: 1, email: 'admin@example.com', role: 'admin', first_name: 'Admin', last_name: 'User', username: 'admin' },
  userRole: 'admin',
  userFullName: 'Admin User',
  accessToken: 'test-token',
  getCurrentUser: vi.fn(),
  clearAll: vi.fn(),
  updateLastActivity: vi.fn(),
  checkSessionTimeout: vi.fn(() => false),
  logout: vi.fn().mockResolvedValue(undefined)
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
const mockWebSocket = {
  connect: vi.fn().mockResolvedValue(undefined),
  disconnect: vi.fn(),
  send: vi.fn(),
  on: vi.fn(),
  off: vi.fn(),
  hasAnyConnection: { value: false }
}

vi.mock('@/composables/useWebSocket', () => ({
  useWebSocket: vi.fn(() => mockWebSocket)
}))

// Mock sweetalert2 - define mock inside factory to avoid hoisting issues
vi.mock('sweetalert2', () => {
  const mockSwal = {
    fire: vi.fn().mockResolvedValue({ isConfirmed: false })
  }
  return {
    default: mockSwal
  }
})

// Create mocks for use in tests
const mocks = {
  adminStore: mockAdminStore,
  authStore: mockAuthStore,
  websocket: mockWebSocket,
  get swal() {
    // Access Swal dynamically to ensure it's the mocked version
    return Swal
  }
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
      plugins: [createPinia()],
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
    // Don't use fake timers as tests use real setTimeout
    // vi.useFakeTimers()
    // Setup localStorage mock with actual storage implementation
    const storage = {}
    localStorage.getItem = vi.fn((key) => storage[key] || null)
    localStorage.setItem = vi.fn((key, value) => {
      storage[key] = String(value)
    })
    localStorage.removeItem = vi.fn((key) => {
      delete storage[key]
    })
    localStorage.clear = vi.fn(() => {
      for (const key of Object.keys(storage)) {
        delete storage[key]
      }
    })
    localStorage.setItem('sidebarCollapsed', 'false')
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    // Clean up any intervals that might be running
    vi.clearAllTimers()
    vi.useRealTimers()
  })

  it('should render dashboard components', () => {
    wrapper = mountWithDefaults()
    expect(wrapper.exists()).toBe(true)
  })

  it('should redirect non-admin users', async () => {
    mockAuthStore.isAdmin = false
    wrapper = mountWithDefaults()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    
    expect(mockRouter.push).toHaveBeenCalledWith('/acceso-denegado')
    mockAuthStore.isAdmin = true
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

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(mocks.adminStore.getGeneralStats).toHaveBeenCalled()
    expect(mocks.adminStore.getRecentUsers).toHaveBeenCalled()
    expect(mocks.adminStore.getRecentActivities).toHaveBeenCalled()
    expect(mocks.adminStore.getSystemAlerts).toHaveBeenCalled()
    expect(mocks.adminStore.getReportStats).toHaveBeenCalled()
    expect(mocks.adminStore.getQualityDistribution).toHaveBeenCalled()
  })

  it('should handle loadDashboardData error', async () => {
    mocks.adminStore.getGeneralStats.mockRejectedValue(new Error('Network error'))
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))

    expect(mocks.swal.fire).toHaveBeenCalledWith(
      expect.objectContaining({
        icon: 'error',
        title: 'Error',
        text: 'No se pudieron cargar los datos del dashboard'
      })
    )
  })

  it('should load stats with complete data', async () => {
    const statsData = {
      users: { total: 100, this_week: 10, this_month: 30 },
      fincas: { total: 50, this_week: 5, this_month: 15 },
      images: { total: 1000, this_week: 100, this_month: 300 },
      predictions: { average_confidence: 0.85 },
      activity_by_day: { labels: ['Mon', 'Tue'], data: [10, 20] },
      quality_distribution: { excelente: 30, buena: 40, regular: 20, baja: 10 }
    }
    
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: statsData })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.stats.users.total).toBe(100)
    expect(wrapper.vm.stats.fincas.total).toBe(50)
  })

  it('should handle loadStats error', async () => {
    mocks.adminStore.getGeneralStats.mockRejectedValue(new Error('Stats error'))
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.stats.users.total).toBe(0)
  })

  it('should process user data correctly', async () => {
    const usersData = [
      { id: 1, username: 'user1', email: 'user1@test.com', first_name: 'User', last_name: 'One', role: 'farmer', is_active: true, date_joined: '2024-01-01' },
      { id: 2, email: 'user2@test.com', first_name: 'User', last_name: 'Two', role: 'analyst', created_at: '2024-01-02' }
    ]
    
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: usersData })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.recentUsers.length).toBe(2)
    expect(wrapper.vm.recentUsers[0].username).toBe('user1')
  })

  it('should handle loadRecentUsers with array response', async () => {
    const usersArray = [{ id: 1, username: 'user1' }]
    
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: usersArray })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.recentUsers.length).toBe(1)
  })

  it('should handle loadRecentUsers error', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockRejectedValue(new Error('Users error'))
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.recentUsers).toEqual([])
  })

  it('should process activity data correctly', async () => {
    const activitiesData = [
      { id: 1, usuario: 'user1', accion: 'create', accion_display: 'Crear', modelo: 'Finca', timestamp: '2024-01-01', descripcion: 'Test', ip_address: '127.0.0.1' },
      { id: 2, action: 'update', model: 'Lote', created_at: '2024-01-02' }
    ]
    
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: activitiesData })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.recentActivities.length).toBe(2)
    expect(wrapper.vm.recentActivities[0].accion_display).toBe('Crear')
  })

  it('should handle loadRecentActivities error', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockRejectedValue(new Error('Activities error'))
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.recentActivities).toEqual([])
  })

  it('should process alert data correctly', async () => {
    const alertsData = [
      { id: 1, titulo: 'Alert 1', mensaje: 'Message 1', tipo: 'warning', fecha_creacion: '2024-01-01', leida: false },
      { id: 2, title: 'Alert 2', message: 'Message 2', tipo: 'error', created_at: '2024-01-02' }
    ]
    
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: alertsData })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.alerts.length).toBe(2)
    expect(wrapper.vm.alerts[0].type).toBe('warning')
  })

  it('should handle loadAlerts error', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockRejectedValue(new Error('Alerts error'))
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.alerts).toEqual([])
  })

  it('should load report stats correctly', async () => {
    const reportStatsData = {
      total_reportes: 100,
      reportes_completados: 80,
      reportes_generando: 15,
      reportes_fallidos: 5
    }
    
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: reportStatsData })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.reportStats.total_reportes).toBe(100)
  })

  it('should handle loadReportStats error', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockRejectedValue(new Error('Report stats error'))
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.reportStats.total_reportes).toBe(0)
  })

  it('should update quality chart from stats', async () => {
    const statsData = {
      quality_distribution: { excelente: 30, buena: 40, regular: 20, baja: 10 }
    }
    
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: statsData })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 400))
    await wrapper.vm.$nextTick()
    await flushPromises()
    await wrapper.vm.$nextTick()

    // Wait for loadStats to complete and update stats.value
    // Due to race condition between loadStats() and loadQualityData() running in parallel,
    // we need to ensure stats are set and then manually trigger the update
    expect(wrapper.vm.stats.quality_distribution).toBeDefined()
    expect(wrapper.vm.stats.quality_distribution.excelente).toBe(30)
    
    // Manually trigger update to ensure qualityData is set correctly
    wrapper.vm.updateQualityChartFromStats()
    await wrapper.vm.$nextTick()
    
    // Verify qualityData was updated from stats
    expect(wrapper.vm.qualityData.labels).toContain('Excelente')
    expect(wrapper.vm.qualityData.datasets).toBeDefined()
    expect(wrapper.vm.qualityData.datasets[0]).toBeDefined()
    expect(wrapper.vm.qualityData.datasets[0].data).toBeDefined()
    expect(wrapper.vm.qualityData.datasets[0].data[0]).toBe(30)
  })

  it('should load quality data when not in stats', async () => {
    const qualityData = { excelente: 25, buena: 35, regular: 25, baja: 15 }
    
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: qualityData })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.qualityData.datasets[0].data[0]).toBe(25)
  })

  it('should handle loadQualityData error', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockRejectedValue(new Error('Quality error'))
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.qualityData.labels).toContain('Excelente')
  })

  it('should update activity chart from stats', async () => {
    const statsData = {
      activity_by_day: { labels: ['Mon', 'Tue', 'Wed'], data: [10, 20, 30] }
    }
    
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: statsData })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.activityData.labels).toEqual(['Mon', 'Tue', 'Wed'])
    expect(wrapper.vm.activityData.datasets[0].data).toEqual([10, 20, 30])
  })

  it('should handle updateActivityChart error', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockRejectedValue(new Error('Activity error'))
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.activityData.labels).toEqual([])
  })

  it('should compute kpiCards with empty stats', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.kpiCards.length).toBe(4)
    expect(wrapper.vm.kpiCards[0].value).toBe(0)
  })

  it('should compute kpiCards with stats data', async () => {
    const statsData = {
      users: { total: 100, this_week: 10 },
      fincas: { total: 50, this_week: 5 },
      images: { total: 1000, this_week: 100 },
      predictions: { average_confidence: 0.85 }
    }
    
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: statsData })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.kpiCards[0].value).toBe(100)
    expect(wrapper.vm.kpiCards[1].value).toBe(50)
    expect(wrapper.vm.kpiCards[2].value).toBe(1000)
    expect(wrapper.vm.kpiCards[3].value).toBe(85)
  })

  it('should compute kpiCards with avg_quality fallback', async () => {
    const statsData = {
      users: { total: 100 },
      fincas: { total: 50 },
      images: { total: 1000 },
      avg_quality: 75,
      // Don't include predictions to test fallback
      predictions: undefined
    }
    
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: statsData })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 400))
    await wrapper.vm.$nextTick()
    await flushPromises()
    await wrapper.vm.$nextTick()
    await flushPromises()

    // Wait for loadStats to complete and update stats.value
    expect(wrapper.vm.stats.avg_quality).toBe(75)
    // Force recompute by accessing kpiCards
    const kpiCards = wrapper.vm.kpiCards
    expect(kpiCards[3].value).toBe(75)
  })

  it('should compute userName correctly', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.userName).toBe('Admin User')
  })

  it('should compute userName with username fallback', async () => {
    mockAuthStore.user = { id: 1, username: 'testuser' }
    
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    // When user only has username, it should use username as fallback
    expect(wrapper.vm.userName).toBe('testuser')
    
    // Restore original user
    mockAuthStore.user = { id: 1, email: 'admin@example.com', role: 'admin', first_name: 'Admin', last_name: 'User', username: 'admin' }
  })

  it('should compute userRole correctly', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.userRole).toBe('admin')
  })

  it('should compute userRole for farmer', async () => {
    mockAuthStore.userRole = 'farmer'
    
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.userRole).toBe('agricultor')
    mockAuthStore.userRole = 'admin'
  })

  it('should format last update time correctly', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    wrapper.vm.lastUpdateTime = new Date()
    const formatted = wrapper.vm.formatLastUpdate(wrapper.vm.lastUpdateTime)
    expect(formatted).toBe('Ahora')
  })

  it('should format last update time for seconds', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    const date = new Date(Date.now() - 10000)
    const formatted = wrapper.vm.formatLastUpdate(date)
    expect(formatted).toContain('s')
  })

  it('should format last update time for minutes', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    const date = new Date(Date.now() - 120000)
    const formatted = wrapper.vm.formatLastUpdate(date)
    expect(formatted).toContain('m')
  })

  it('should format last update time for null', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    const formatted = wrapper.vm.formatLastUpdate(null)
    expect(formatted).toBe('Nunca')
  })

  it('should handle refreshData', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    vi.clearAllMocks()
    await wrapper.vm.refreshData()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))

    expect(mocks.adminStore.getGeneralStats).toHaveBeenCalled()
  })

  it('should handle menu click', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    wrapper.vm.handleMenuClick({ route: '/admin/users' })
    expect(mockRouter.push).toHaveBeenCalledWith('/admin/users')
  })

  it('should handle logout', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    await wrapper.vm.handleLogout()
    expect(mocks.authStore.logout).toHaveBeenCalled()
  })

  it('should handle logout error', async () => {
    mocks.authStore.logout.mockRejectedValue(new Error('Logout error'))
    
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    await wrapper.vm.handleLogout()
    expect(mocks.swal.fire).toHaveBeenCalledWith(
      expect.objectContaining({
        icon: 'error',
        title: 'Error',
        text: 'No se pudo cerrar la sesión'
      })
    )
  })

  it('should handle activity chart type change', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    wrapper.vm.handleActivityChartTypeChange('bar')
    expect(wrapper.vm.activityChartType).toBe('bar')
  })

  it('should handle activity refresh', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    // Ensure stats.value.activity_by_day is not set so getActivityData is called
    if (wrapper.vm.stats) {
      wrapper.vm.stats.activity_by_day = undefined
    } else {
      wrapper.vm.stats = {}
    }
    vi.clearAllMocks()
    
    wrapper.vm.handleActivityRefresh()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 100))
    await wrapper.vm.$nextTick()

    expect(mocks.adminStore.getActivityData).toHaveBeenCalled()
  })

  it('should handle quality refresh', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    // Clear quality_distribution from stats to ensure getQualityDistribution is called
    if (wrapper.vm.stats?.quality_distribution) {
      delete wrapper.vm.stats.quality_distribution
    }
    
    vi.clearAllMocks()
    wrapper.vm.handleQualityRefresh()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 100))
    await wrapper.vm.$nextTick()

    expect(mocks.adminStore.getQualityDistribution).toHaveBeenCalled()
  })

  it('should handle activity click', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
    wrapper.vm.handleActivityClick({})
    expect(consoleSpy).toHaveBeenCalled()
    consoleSpy.mockRestore()
  })

  it('should handle quality click', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
    wrapper.vm.handleQualityClick({})
    expect(consoleSpy).toHaveBeenCalled()
    consoleSpy.mockRestore()
  })

  it('should handle view user', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    wrapper.vm.handleViewUser(123)
    expect(mockRouter.push).toHaveBeenCalledWith('/admin/users/123')
  })

  it('should handle edit user', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    wrapper.vm.handleEditUser(456)
    expect(mockRouter.push).toHaveBeenCalledWith('/admin/users/456/edit')
  })

  it('should handle dismiss alert', async () => {
    mocks.swal.fire.mockResolvedValue({ isConfirmed: true })
    
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    await wrapper.vm.handleDismissAlert(1)
    expect(mocks.swal.fire).toHaveBeenCalled()
  })

  it('should handle dismiss alert cancellation', async () => {
    mocks.swal.fire.mockResolvedValue({ isConfirmed: false })
    
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    await wrapper.vm.handleDismissAlert(1)
    expect(mocks.swal.fire).toHaveBeenCalled()
  })

  it('should toggle sidebar collapse', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.isSidebarCollapsed).toBe(false)
    wrapper.vm.toggleSidebarCollapse()
    await wrapper.vm.$nextTick()
    await flushPromises()
    expect(wrapper.vm.isSidebarCollapsed).toBe(true)
    // localStorage.setItem converts boolean to string, so 'true' or 'false'
    // Wait a bit to ensure localStorage is updated
    await new Promise(resolve => setTimeout(resolve, 10))
    expect(localStorage.getItem('sidebarCollapsed')).toBe('true')
  })

  it('should setup websocket listeners when websocket is available', async () => {
    mockWebSocket.hasAnyConnection = { value: true }
    
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(mockWebSocket.on).toHaveBeenCalled()
    mockWebSocket.hasAnyConnection = { value: false }
  })

  it('should start polling updates', async () => {
    // Use fake timers for this test
    vi.useFakeTimers()
    
    mockWebSocket.hasAnyConnection = { value: false }
    
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    // Use fake timers instead of real setTimeout
    vi.advanceTimersByTime(200)
    await wrapper.vm.$nextTick()

    vi.advanceTimersByTime(3000)
    await flushPromises()
    vi.advanceTimersByTime(100)

    expect(mocks.adminStore.getSystemAlerts).toHaveBeenCalled()
    
    // Restore real timers
    vi.useRealTimers()
  })

  it('should stop auto refresh on unmount', async () => {
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    wrapper.unmount()
    await flushPromises()

    expect(mockWebSocket.off).toHaveBeenCalled()
  })

  it('should handle websocket connection error', async () => {
    mockWebSocket.connect.mockRejectedValue(new Error('Connection error'))
    
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(consoleWarnSpy).toHaveBeenCalled()
    consoleWarnSpy.mockRestore()
    mockWebSocket.connect.mockResolvedValue(undefined)
  })

  it('should watch stats changes', async () => {
    const consoleLogSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
    
    mocks.adminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mocks.adminStore.getReportStats.mockResolvedValue({ data: {} })
    mocks.adminStore.getActivityData.mockResolvedValue({ data: { labels: [], data: [] } })
    mocks.adminStore.getQualityDistribution.mockResolvedValue({ data: {} })
    
    wrapper = mountWithDefaults()

    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    // Change stats to trigger watcher
    wrapper.vm.stats = { users: { total: 200 } }
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // The watcher should log when stats change
    // We check if console.log was called (the watcher logs '🔄 Stats cambiaron:')
    expect(consoleLogSpy).toHaveBeenCalled()
    consoleLogSpy.mockRestore()
  }, 10000) // Add timeout to prevent hanging
})

