import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import UserDetailsModal from './UserDetailsModal.vue'

const mockGetUserById = vi.fn()
const mockGetActivityLogs = vi.fn()

vi.mock('@/components/common/BaseModal.vue', () => ({
  default: {
    name: 'BaseModal',
    template: '<div v-if="show"><slot></slot></div>',
    props: ['show', 'title', 'subtitle', 'maxWidth'],
    emits: ['close', 'update:show']
  }
}))

vi.mock('@/stores/admin', () => ({
  useAdminStore: () => ({
    getUserById: mockGetUserById,
    getActivityLogs: mockGetActivityLogs
  })
}))

describe('UserDetailsModal', () => {
  const mockUser = {
    id: 1,
    username: 'testuser',
    email: 'test@test.com',
    first_name: 'Test',
    last_name: 'User'
  }

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    mockGetUserById.mockResolvedValue({ data: { ...mockUser, role: 'admin' } })
    mockGetActivityLogs.mockResolvedValue({ data: { results: [] } })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
    vi.useRealTimers()
    vi.clearAllTimers()
  })

  it('should render modal', () => {
    wrapper = mount(UserDetailsModal, {
      props: {
        user: mockUser
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should load user details on mount', async () => {
    wrapper = mount(UserDetailsModal, {
      props: {
        user: mockUser
      }
    })

    await wrapper.vm.$nextTick()
    vi.advanceTimersByTime(100)
    await wrapper.vm.$nextTick()

    expect(mockGetUserById).toHaveBeenCalledWith(mockUser.id)
  })

  it('should load recent activities', async () => {
    mockGetActivityLogs.mockResolvedValue({
      data: {
        results: [
          { id: 1, accion: 'login', timestamp: new Date().toISOString() }
        ]
      }
    })

    wrapper = mount(UserDetailsModal, {
      props: {
        user: mockUser
      }
    })

    await wrapper.vm.$nextTick()
    vi.advanceTimersByTime(100)
    await wrapper.vm.$nextTick()

    expect(mockGetActivityLogs).toHaveBeenCalled()
  })

  it('should handle error when loading user details', async () => {
    mockGetUserById.mockRejectedValue(new Error('Network error'))

    wrapper = mount(UserDetailsModal, {
      props: {
        user: mockUser
      }
    })

    await wrapper.vm.$nextTick()
    vi.advanceTimersByTime(100)
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.loading).toBe(false)
  })

  it('should handle error when loading activities', async () => {
    mockGetActivityLogs.mockRejectedValue(new Error('Network error'))

    wrapper = mount(UserDetailsModal, {
      props: {
        user: mockUser
      }
    })

    await wrapper.vm.$nextTick()
    await wrapper.vm.loadRecentActivities()
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.recentActivities).toEqual([])
  })

  it('should close modal and emit close event', async () => {
    wrapper = mount(UserDetailsModal, {
      props: {
        user: mockUser
      }
    })

    await wrapper.vm.closeModal()

    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('should emit edit event', async () => {
    wrapper = mount(UserDetailsModal, {
      props: {
        user: mockUser
      }
    })

    wrapper.vm.userDetails = { id: 1, username: 'test' }
    await wrapper.vm.editUser()

    expect(wrapper.emitted('edit')).toBeTruthy()
  })

  it('should format date time correctly', () => {
    wrapper = mount(UserDetailsModal, {
      props: {
        user: mockUser
      }
    })

    const date = new Date('2024-01-01T12:00:00')
    const formatted = wrapper.vm.formatDateTime(date)

    expect(formatted).toBeTruthy()
  })

  it('should return correct role badge class', () => {
    wrapper = mount(UserDetailsModal, {
      props: {
        user: mockUser
      }
    })

    expect(wrapper.vm.getRoleBadgeClass('Administrador')).toBe('badge-danger')
    expect(wrapper.vm.getRoleBadgeClass('Agricultor')).toBe('badge-success')
    expect(wrapper.vm.getRoleBadgeClass('Técnico')).toBe('badge-info')
    expect(wrapper.vm.getRoleBadgeClass('Unknown')).toBe('badge-secondary')
  })

  it('should return connection status for user without last_login', () => {
    wrapper = mount(UserDetailsModal, {
      props: {
        user: mockUser
      }
    })

    const status = wrapper.vm.getConnectionStatus({})
    expect(status).toBe('Nunca conectado')
  })

  it('should return "En línea" for recent login', () => {
    wrapper = mount(UserDetailsModal, {
      props: {
        user: mockUser
      }
    })

    const recentLogin = new Date(Date.now() - 2 * 60 * 1000).toISOString()
    const status = wrapper.vm.getConnectionStatus({ last_login: recentLogin })
    expect(status).toBe('En línea')
  })

  it('should return "Reciente" for login within hour', () => {
    wrapper = mount(UserDetailsModal, {
      props: {
        user: mockUser
      }
    })

    const recentLogin = new Date(Date.now() - 30 * 60 * 1000).toISOString()
    const status = wrapper.vm.getConnectionStatus({ last_login: recentLogin })
    expect(status).toBe('Reciente')
  })

  it('should return "Desconectado" for old login', () => {
    wrapper = mount(UserDetailsModal, {
      props: {
        user: mockUser
      }
    })

    const oldLogin = new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
    const status = wrapper.vm.getConnectionStatus({ last_login: oldLogin })
    expect(status).toBe('Desconectado')
  })

  it('should return correct connection status class', () => {
    wrapper = mount(UserDetailsModal, {
      props: {
        user: mockUser
      }
    })

    expect(wrapper.vm.getConnectionStatusClass({})).toBe('badge-secondary')

    const recentLogin = new Date(Date.now() - 2 * 60 * 1000).toISOString()
    expect(wrapper.vm.getConnectionStatusClass({ last_login: recentLogin })).toBe('badge-success')

    const hourAgoLogin = new Date(Date.now() - 30 * 60 * 1000).toISOString()
    expect(wrapper.vm.getConnectionStatusClass({ last_login: hourAgoLogin })).toBe('badge-warning')

    const oldLogin = new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
    expect(wrapper.vm.getConnectionStatusClass({ last_login: oldLogin })).toBe('badge-secondary')
  })

  it('should return correct activity icon', () => {
    wrapper = mount(UserDetailsModal, {
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
    expect(wrapper.vm.getActivityIcon('unknown')).toBe('fas fa-circle')
  })
})

