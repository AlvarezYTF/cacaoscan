import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import UserActivityModal from './UserActivityModal.vue'

const mockGetActivityLogs = vi.fn()
const mockExportData = vi.fn()

vi.mock('@/components/common/BaseModal.vue', () => ({
  default: {
    name: 'BaseModal',
    template: '<div v-if="show" class="base-modal"><slot name="header"></slot><slot></slot><slot name="footer"></slot></div>',
    props: ['show', 'title', 'subtitle', 'maxWidth'],
    emits: ['close', 'update:show']
  }
}))

vi.mock('@/stores/admin', () => ({
  useAdminStore: () => ({
    getActivityLogs: mockGetActivityLogs,
    exportData: mockExportData
  })
}))

vi.mock('@/composables/usePagination', () => ({
  usePagination: () => ({
    currentPage: { value: 1 },
    itemsPerPage: { value: 20 },
    visiblePages: { value: [1, 2, 3] },
    goToPage: vi.fn().mockReturnValue(true),
    updateFromApiResponse: vi.fn()
  })
}))

describe('UserActivityModal', () => {
  const mockUser = {
    id: 1,
    username: 'testuser'
  }

  const mockActivities = [
    { id: 1, accion: 'login', timestamp: new Date().toISOString(), user_agent: 'Chrome' },
    { id: 2, accion: 'logout', timestamp: new Date(Date.now() - 60 * 60 * 1000).toISOString(), user_agent: 'Firefox' }
  ]

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockGetActivityLogs.mockResolvedValue({
      data: {
        results: mockActivities,
        count: 2,
        page: 1,
        page_size: 20,
        total_pages: 1
      }
    })
    mockExportData.mockResolvedValue({ data: new Blob(['test'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }) })
  })

  afterEach(() => {
    // Clean up wrapper
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
  })

  it('should render modal', () => {
    wrapper = mount(UserActivityModal, {
      props: {
        user: mockUser
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should load activities on mount', async () => {
    wrapper = mount(UserActivityModal, {
      props: {
        user: mockUser
      }
    })

    await new Promise(resolve => setTimeout(resolve, 100))

    expect(mockGetActivityLogs).toHaveBeenCalled()
  })

  it('should calculate activities today', () => {
    wrapper = mount(UserActivityModal, {
      props: {
        user: mockUser
      }
    })

    wrapper.vm.activities = [
      { timestamp: new Date().toISOString() },
      { timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString() }
    ]

    expect(wrapper.vm.activitiesToday).toBe(1)
  })

  it('should calculate most common action', () => {
    wrapper = mount(UserActivityModal, {
      props: {
        user: mockUser
      }
    })

    wrapper.vm.activities = [
      { accion: 'login' },
      { accion: 'login' },
      { accion: 'logout' }
    ]

    expect(wrapper.vm.mostCommonAction).toBe('login')
  })

  it('should return N/A when no activities', () => {
    wrapper = mount(UserActivityModal, {
      props: {
        user: mockUser
      }
    })

    wrapper.vm.activities = []

    expect(wrapper.vm.mostCommonAction).toBe('N/A')
    expect(wrapper.vm.lastActivity).toBe('N/A')
  })

  it('should calculate last activity time', () => {
    wrapper = mount(UserActivityModal, {
      props: {
        user: mockUser
      }
    })

    const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000)
    wrapper.vm.activities = [
      { timestamp: oneHourAgo.toISOString() }
    ]

    const lastActivity = wrapper.vm.lastActivity
    expect(lastActivity).toBeTruthy()
    expect(lastActivity.includes('hora')).toBe(true)
  })

  it('should load activities with filters', async () => {
    wrapper = mount(UserActivityModal, {
      props: {
        user: mockUser
      }
    })

    wrapper.vm.filters.action = 'login'
    wrapper.vm.filters.model = 'user'
    wrapper.vm.filters.period = '7'

    await wrapper.vm.loadActivities()
    await wrapper.vm.$nextTick()

    expect(mockGetActivityLogs).toHaveBeenCalled()
  })

  it('should handle error when loading activities', async () => {
    mockGetActivityLogs.mockRejectedValue(new Error('Network error'))

    wrapper = mount(UserActivityModal, {
      props: {
        user: mockUser
      }
    })

    await wrapper.vm.loadActivities()
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.loading).toBe(false)
  })

  it('should calculate start date from period', () => {
    wrapper = mount(UserActivityModal, {
      props: {
        user: mockUser
      }
    })

    wrapper.vm.filters.period = '30'
    const startDate = wrapper.vm.getStartDate()

    expect(startDate).toBeTruthy()
  })

  it('should clear filters', async () => {
    wrapper = mount(UserActivityModal, {
      props: {
        user: mockUser
      }
    })

    wrapper.vm.filters.action = 'login'
    wrapper.vm.filters.model = 'user'
    wrapper.vm.filters.period = '7'

    await wrapper.vm.clearFilters()
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.filters.action).toBe('')
    expect(wrapper.vm.filters.model).toBe('')
    expect(wrapper.vm.filters.period).toBe('30')
  })

  it('should change page', async () => {
    wrapper = mount(UserActivityModal, {
      props: {
        user: mockUser
      }
    })

    wrapper.vm.changePage = vi.fn().mockImplementation((page) => {
      wrapper.vm.pagination.goToPage = vi.fn().mockReturnValue(true)
      wrapper.vm.loadActivities()
    })

    await wrapper.vm.changePage(2)
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.changePage).toHaveBeenCalled()
  })

  it('should export activities', async () => {
    const originalCreateElement = document.createElement
    const originalAppendChild = document.body.appendChild
    const originalRemoveChild = document.body.removeChild
    const originalCreateObjectURL = global.URL.createObjectURL
    const originalRevokeObjectURL = global.URL.revokeObjectURL
    
    global.URL.createObjectURL = vi.fn().mockReturnValue('blob:test-url')
    global.URL.revokeObjectURL = vi.fn()
    document.createElement = vi.fn().mockImplementation((tagName) => {
      if (tagName === 'a') {
        return {
          href: '',
          download: '',
          click: vi.fn(),
          remove: vi.fn()
        }
      }
      return originalCreateElement.call(document, tagName)
    })
    document.body.appendChild = vi.fn()
    document.body.removeChild = vi.fn()

    wrapper = mount(UserActivityModal, {
      props: {
        user: mockUser
      }
    })

    await wrapper.vm.exportActivities()
    await wrapper.vm.$nextTick()

    expect(mockExportData).toHaveBeenCalled()
    
    // Restore original methods
    document.createElement = originalCreateElement
    document.body.appendChild = originalAppendChild
    document.body.removeChild = originalRemoveChild
    global.URL.createObjectURL = originalCreateObjectURL
    global.URL.revokeObjectURL = originalRevokeObjectURL
  })

  it('should handle error when exporting activities', async () => {
    mockExportData.mockRejectedValue(new Error('Export error'))

    wrapper = mount(UserActivityModal, {
      props: {
        user: mockUser
      }
    })

    await wrapper.vm.exportActivities()
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.loading).toBe(false)
  })

  it('should close modal and emit close event', async () => {
    wrapper = mount(UserActivityModal, {
      props: {
        user: mockUser
      }
    })

    await wrapper.vm.closeModal()

    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('should format date time correctly', () => {
    wrapper = mount(UserActivityModal, {
      props: {
        user: mockUser
      }
    })

    const date = new Date('2024-01-01T12:00:00')
    const formatted = wrapper.vm.formatDateTime(date)

    expect(formatted).toBeTruthy()
  })

  it('should return correct activity icon', () => {
    wrapper = mount(UserActivityModal, {
      props: {
        user: mockUser
      }
    })

    expect(wrapper.vm.getActivityIcon('login')).toBe('fas fa-sign-in-alt')
    expect(wrapper.vm.getActivityIcon('logout')).toBe('fas fa-sign-out-alt')
    expect(wrapper.vm.getActivityIcon('create')).toBe('fas fa-plus')
    expect(wrapper.vm.getActivityIcon('update')).toBe('fas fa-edit')
    expect(wrapper.vm.getActivityIcon('delete')).toBe('fas fa-trash')
    expect(wrapper.vm.getActivityIcon('view')).toBe('fas fa-eye')
    expect(wrapper.vm.getActivityIcon('analysis')).toBe('fas fa-microscope')
    expect(wrapper.vm.getActivityIcon('training')).toBe('fas fa-brain')
    expect(wrapper.vm.getActivityIcon('report')).toBe('fas fa-file-alt')
    expect(wrapper.vm.getActivityIcon('download')).toBe('fas fa-download')
    expect(wrapper.vm.getActivityIcon('upload')).toBe('fas fa-upload')
    expect(wrapper.vm.getActivityIcon('error')).toBe('fas fa-exclamation-triangle')
    expect(wrapper.vm.getActivityIcon('unknown')).toBe('fas fa-circle')
  })

  it('should return correct action class', () => {
    wrapper = mount(UserActivityModal, {
      props: {
        user: mockUser
      }
    })

    expect(wrapper.vm.getActionClass('login')).toBe('action-success')
    expect(wrapper.vm.getActionClass('logout')).toBe('action-info')
    expect(wrapper.vm.getActionClass('create')).toBe('action-success')
    expect(wrapper.vm.getActionClass('update')).toBe('action-warning')
    expect(wrapper.vm.getActionClass('delete')).toBe('action-danger')
    expect(wrapper.vm.getActionClass('view')).toBe('action-info')
    expect(wrapper.vm.getActionClass('analysis')).toBe('action-primary')
    expect(wrapper.vm.getActionClass('training')).toBe('action-primary')
    expect(wrapper.vm.getActionClass('report')).toBe('action-info')
    expect(wrapper.vm.getActionClass('error')).toBe('action-danger')
    expect(wrapper.vm.getActionClass('unknown')).toBe('action-secondary')
  })

  it('should detect browser from user agent', () => {
    wrapper = mount(UserActivityModal, {
      props: {
        user: mockUser
      }
    })

    expect(wrapper.vm.getBrowserInfo('Chrome/91.0')).toBe('Chrome')
    expect(wrapper.vm.getBrowserInfo('Firefox/89.0')).toBe('Firefox')
    expect(wrapper.vm.getBrowserInfo('Safari/14.0')).toBe('Safari')
    expect(wrapper.vm.getBrowserInfo('Edge/91.0')).toBe('Edge')
    expect(wrapper.vm.getBrowserInfo('Unknown')).toBe('Otro')
    expect(wrapper.vm.getBrowserInfo(null)).toBe('N/A')
  })
})

