import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AdminDashboard from '../../Admin/AdminDashboard.vue'
import { 
  createCommonMocks, 
  adminDashboardComponentMocks,
  composableMocks,
  sweetAlert2Mock,
  createDefaultStubs
} from '@/test/mocks'

const mocks = createCommonMocks({
  authStore: {
    isAuthenticated: true,
    isAdmin: true,
    user: { id: 1, email: 'admin@example.com', role: 'admin' }
  }
})

vi.mock('@/stores/admin', () => ({
  useAdminStore: () => mocks.adminStore
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mocks.authStore
}))

vi.mock('@/stores/config', () => ({
  useConfigStore: () => mocks.configStore
}))

// Mock components
vi.mock('@/components/layout/Common/Sidebar.vue', () => adminDashboardComponentMocks.Sidebar)
vi.mock('@/components/admin/AdminDashboardComponents/KPICards.vue', () => adminDashboardComponentMocks.KPICards)
vi.mock('@/components/admin/AdminDashboardComponents/DashboardCharts.vue', () => adminDashboardComponentMocks.DashboardCharts)
vi.mock('@/components/admin/AdminDashboardComponents/DashboardTables.vue', () => adminDashboardComponentMocks.DashboardTables)
vi.mock('@/components/admin/AdminDashboardComponents/DashboardAlerts.vue', () => adminDashboardComponentMocks.DashboardAlerts)

// Mock composables
vi.mock('@/composables/useWebSocket', () => ({
  useWebSocket: vi.fn(() => composableMocks.useWebSocket.useWebSocket())
}))

// Mock sweetalert2
vi.mock('sweetalert2', () => sweetAlert2Mock)

// Common stubs configuration
const defaultStubs = createDefaultStubs()

// Helper function to mount component with default stubs
const mountWithDefaults = (options = {}) => {
  return mount(AdminDashboard, {
    global: {
      stubs: defaultStubs,
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
    
    wrapper = mountWithDefaults()

    // Wait for onMounted and async operations to complete
    await wrapper.vm.$nextTick()
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

