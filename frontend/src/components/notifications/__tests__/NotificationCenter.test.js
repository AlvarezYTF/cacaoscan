import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import NotificationCenter from '../NotificationCenter.vue'

const mockNotificationStore = {
  getNotifications: vi.fn().mockResolvedValue({
    data: {
      results: [],
      count: 0
    }
  }),
  markAsRead: vi.fn(),
  markAllAsRead: vi.fn(),
  deleteNotification: vi.fn(),
  updateSettings: vi.fn(),
  websocket: null
}

vi.mock('@/stores/notifications', () => ({
  useNotificationsStore: () => mockNotificationStore,
  useNotificationStore: () => mockNotificationStore
}))

vi.mock('@/composables/useNotifications', () => ({
  useNotifications: () => ({
    showSuccess: vi.fn(),
    showError: vi.fn(),
    showWarning: vi.fn(),
    showInfo: vi.fn(),
    clearAll: vi.fn(),
    notifications: { value: [] },
    unreadCount: { value: 0 },
    loading: { value: false },
    error: { value: null },
    store: mockNotificationStore
  })
}))

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn().mockResolvedValue({ isConfirmed: true })
  }
}))

describe('NotificationCenter', () => {
  let wrapper

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('should render notification center', () => {
    wrapper = mount(NotificationCenter)

    expect(wrapper.find('.notification-center').exists()).toBe(true)
    expect(wrapper.text()).toContain('Centro de Notificaciones')
  })

  it('should load notifications on mount', async () => {
    mockNotificationStore.getNotifications.mockResolvedValue({
      data: {
        results: [],
        count: 0
      }
    })

    wrapper = mount(NotificationCenter)
    await wrapper.vm.$nextTick()

    expect(mockNotificationStore.getNotifications).toHaveBeenCalled()
  })

  it('should display notifications list', async () => {
    const mockNotifications = [
      { id: 1, titulo: 'Test 1', mensaje: 'Message 1', leida: false, fecha_creacion: new Date().toISOString() },
      { id: 2, titulo: 'Test 2', mensaje: 'Message 2', leida: true, fecha_creacion: new Date().toISOString() }
    ]

    mockNotificationStore.getNotifications.mockResolvedValue({
      data: {
        results: mockNotifications,
        count: 2
      }
    })

    wrapper = mount(NotificationCenter)
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.vm.notifications).toHaveLength(2)
  })

  it('should filter notifications by read status', async () => {
    const mockNotifications = [
      { id: 1, leida: false },
      { id: 2, leida: true },
      { id: 3, leida: false }
    ]

    mockNotificationStore.getNotifications.mockResolvedValue({
      data: {
        results: mockNotifications,
        count: 3
      }
    })

    wrapper = mount(NotificationCenter)
    await wrapper.vm.$nextTick()

    wrapper.vm.setFilter('unread')
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.filteredNotifications.every(n => !n.leida)).toBe(true)
  })

  it('should filter notifications by type', async () => {
    const mockNotifications = [
      { id: 1, tipo: 'info', leida: false },
      { id: 2, tipo: 'error', leida: false },
      { id: 3, tipo: 'info', leida: false }
    ]

    mockNotificationStore.getNotifications.mockResolvedValue({
      data: {
        results: mockNotifications,
        count: 3
      }
    })

    wrapper = mount(NotificationCenter)
    await wrapper.vm.$nextTick()

    wrapper.vm.typeFilter = 'info'
    wrapper.vm.applyFilters()
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.filteredNotifications.every(n => n.tipo === 'info')).toBe(true)
  })

  it('should mark notification as read', async () => {
    mockNotificationStore.markAsRead.mockResolvedValue({})

    const notification = {
      id: 1,
      leida: false,
      fecha_creacion: new Date().toISOString()
    }

    wrapper = mount(NotificationCenter)
    wrapper.vm.notifications = [notification]
    await wrapper.vm.$nextTick()

    await wrapper.vm.markAsRead(notification)
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 50))

    expect(mockNotificationStore.markAsRead).toHaveBeenCalledWith(1)
    // The component updates notifications.value[index], not the original object
    const updatedNotification = wrapper.vm.notifications.find(n => n.id === 1)
    expect(updatedNotification?.leida).toBe(true)
  })

  it('should mark all notifications as read', async () => {
    mockNotificationStore.markAllAsRead.mockResolvedValue(true)

    wrapper = mount(NotificationCenter)
    wrapper.vm.notifications = [
      { id: 1, leida: false },
      { id: 2, leida: false }
    ]
    await wrapper.vm.$nextTick()

    await wrapper.vm.markAllAsRead()
    await wrapper.vm.$nextTick()

    expect(mockNotificationStore.markAllAsRead).toHaveBeenCalled()
    expect(wrapper.vm.notifications.every(n => n.leida)).toBe(true)
  })

  it('should delete notification', async () => {
    mockNotificationStore.deleteNotification.mockResolvedValue({})
    mockNotificationStore.getNotifications.mockResolvedValue({
      data: {
        results: [
          { id: 1, titulo: 'Test', leida: false },
          { id: 2, titulo: 'Test 2', leida: false }
        ],
        count: 2
      }
    })

    wrapper = mount(NotificationCenter)
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Ensure notifications are loaded
    expect(wrapper.vm.notifications).toHaveLength(2)
    wrapper.vm.totalCount = 2

    // SweetAlert2 is mocked to return isConfirmed: true, so deletion should proceed
    await wrapper.vm.deleteNotification({ id: 1, titulo: 'Test', leida: false })
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(mockNotificationStore.deleteNotification).toHaveBeenCalledWith(1)
    // After deletion, the notification should be removed from the array
    expect(wrapper.vm.notifications.find(n => n.id === 1)).toBeUndefined()
    expect(wrapper.vm.totalCount).toBe(1)
  })

  it('should change page', async () => {
    mockNotificationStore.getNotifications.mockResolvedValue({
      data: {
        results: [],
        count: 20,
        page: 2
      }
    })

    wrapper = mount(NotificationCenter)
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Set up pagination
    wrapper.vm.totalPages = 2
    wrapper.vm.currentPage = 1
    await wrapper.vm.$nextTick()

    // Change page
    await wrapper.vm.changePage(2)
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.vm.currentPage).toBe(2)
    expect(mockNotificationStore.getNotifications).toHaveBeenCalled()
  })

  it('should get notification icon', () => {
    wrapper = mount(NotificationCenter)

    expect(wrapper.vm.getNotificationIcon('info')).toContain('info-circle')
    expect(wrapper.vm.getNotificationIcon('error')).toContain('times-circle')
    expect(wrapper.vm.getNotificationIcon('success')).toContain('check-circle')
  })

  it('should format time correctly', () => {
    wrapper = mount(NotificationCenter)

    const now = new Date()
    const oneMinuteAgo = new Date(now.getTime() - 60 * 1000)
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000)

    expect(wrapper.vm.formatTime(oneMinuteAgo.toISOString())).toContain('min')
    expect(wrapper.vm.formatTime(oneHourAgo.toISOString())).toContain('h')
  })

  it('should update settings', async () => {
    mockNotificationStore.updateSettings.mockResolvedValue({})

    wrapper = mount(NotificationCenter)
    wrapper.vm.settings = {
      email_notifications: true,
      push_notifications: false
    }
    await wrapper.vm.$nextTick()

    await wrapper.vm.updateSettings()
    await wrapper.vm.$nextTick()

    expect(mockNotificationStore.updateSettings).toHaveBeenCalledWith(wrapper.vm.settings)
  })

  it('should show empty state when no notifications', async () => {
    mockNotificationStore.getNotifications.mockResolvedValue({
      data: {
        results: [],
        count: 0
      }
    })

    wrapper = mount(NotificationCenter)
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.find('.empty-state').exists()).toBe(true)
  })

  it('should show loading state', async () => {
    wrapper = mount(NotificationCenter)
    wrapper.vm.loading = true
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.loading-state').exists()).toBe(true)
  })

  it('should compute unread count', async () => {
    mockNotificationStore.getNotifications.mockResolvedValue({
      data: {
        results: [
          { id: 1, leida: false },
          { id: 2, leida: true },
          { id: 3, leida: false }
        ],
        count: 3
      }
    })

    wrapper = mount(NotificationCenter)
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // unreadCount is a computed property that filters notifications
    expect(wrapper.vm.unreadCount).toBe(2)
  })

  it('should compute read count', async () => {
    mockNotificationStore.getNotifications.mockResolvedValue({
      data: {
        results: [
          { id: 1, leida: false },
          { id: 2, leida: true },
          { id: 3, leida: true }
        ],
        count: 3
      }
    })

    wrapper = mount(NotificationCenter)
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // readCount is a computed property that filters notifications
    expect(wrapper.vm.readCount).toBe(2)
  })
})

