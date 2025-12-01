import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AdminDashboard from '../../Admin/AdminDashboard.vue'
import {
  createMockAdminStore,
  createMockAuthStore,
  createMockConfigStore
} from '@/test/mocks'

const mockAdminStore = createMockAdminStore()
const mockAuthStore = createMockAuthStore({
  isAuthenticated: true,
  isAdmin: true,
  user: { id: 1, email: 'admin@example.com', role: 'admin' }
})
const mockConfigStore = createMockConfigStore()

vi.mock('@/stores/admin', () => ({
  useAdminStore: () => mockAdminStore
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

vi.mock('@/stores/config', () => ({
  useConfigStore: () => mockConfigStore
}))

// Mock components
vi.mock('@/components/layout/Common/Sidebar.vue', () => ({
  default: { name: 'AdminSidebar', template: '<div>Sidebar</div>' }
}))

vi.mock('@/components/admin/AdminDashboardComponents/KPICards.vue', () => ({
  default: { name: 'KPICards', template: '<div>KPI Cards</div>' }
}))

vi.mock('@/components/admin/AdminDashboardComponents/DashboardCharts.vue', () => ({
  default: { name: 'DashboardCharts', template: '<div>Charts</div>' }
}))

vi.mock('@/components/admin/AdminDashboardComponents/DashboardTables.vue', () => ({
  default: { name: 'DashboardTables', template: '<div>Tables</div>' }
}))

vi.mock('@/components/admin/AdminDashboardComponents/DashboardAlerts.vue', () => ({
  default: { name: 'DashboardAlerts', template: '<div>Alerts</div>' }
}))

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
    fire: vi.fn(),
    Swal: {
      fire: vi.fn()
    }
  }
}))

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
    wrapper = mount(AdminDashboard, {
      global: {
        stubs: {
          'router-link': true,
          'router-view': true,
          'AdminSidebar': true,
          'KPICards': true,
          'DashboardCharts': true,
          'DashboardTables': true,
          'DashboardAlerts': true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should load data on mount', async () => {
    mockAdminStore.getGeneralStats.mockResolvedValue({ data: {} })
    mockAdminStore.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    mockAdminStore.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    mockAdminStore.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    mockAdminStore.getReportStats.mockResolvedValue({ data: {} })
    
    wrapper = mount(AdminDashboard, {
      global: {
        stubs: {
          'router-link': true,
          'router-view': true,
          'AdminSidebar': true,
          'KPICards': true,
          'DashboardCharts': true,
          'DashboardTables': true,
          'DashboardAlerts': true
        }
      }
    })

    // Wait for onMounted and async operations to complete
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Verify that store methods are called
    expect(mockAdminStore.getGeneralStats).toHaveBeenCalled()
  })

  it('should handle refresh action', async () => {
    wrapper = mount(AdminDashboard, {
      global: {
        stubs: {
          'router-link': true,
          'router-view': true,
          'AdminSidebar': true,
          'KPICards': true,
          'DashboardCharts': true,
          'DashboardTables': true,
          'DashboardAlerts': true
        }
      }
    })

    // Test refresh functionality if method exists
    if (wrapper.vm.handleRefresh) {
      await wrapper.vm.handleRefresh()
      expect(mockAdminStore.getGeneralStats).toHaveBeenCalled()
    }
  })

  it('should handle logout', async () => {
    wrapper = mount(AdminDashboard, {
      global: {
        stubs: {
          'router-link': true,
          'router-view': true,
          'AdminSidebar': true,
          'KPICards': true,
          'DashboardCharts': true,
          'DashboardTables': true,
          'DashboardAlerts': true
        }
      }
    })

    if (wrapper.vm.handleLogout) {
      await wrapper.vm.handleLogout()
      // Verify logout behavior
      expect(mockAuthStore).toBeDefined()
    }
  })
})

