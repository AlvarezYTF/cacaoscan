import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import NotificationBell from '../NotificationBell.vue'

const mockNotificationStore = {
  getNotifications: vi.fn().mockResolvedValue({
    data: {
      results: [],
      count: 0
    }
  }),
  markAsRead: vi.fn(),
  markAllAsRead: vi.fn(),
  websocket: null,
  settings: {
    show_toasts: true
  }
}

const mockRouter = {
  push: vi.fn()
}

vi.mock('@/stores/notifications', () => ({
  useNotificationStore: () => mockNotificationStore
}))

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRouter: () => mockRouter
  }
})

describe('NotificationBell', () => {
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

  it('should render notification bell', () => {
    wrapper = mount(NotificationBell, {
      global: {
      }
    })

    expect(wrapper.find('.bell-container').exists()).toBe(true)
    expect(wrapper.find('.fa-bell').exists()).toBe(true)
  })

  it('should show unread count badge', async () => {
    mockNotificationStore.getNotifications.mockResolvedValue({
      data: {
        results: [
          { id: 1, leida: false },
          { id: 2, leida: false }
        ]
      }
    })

    wrapper = mount(NotificationBell, {
      global: {
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    const badge = wrapper.find('.notification-badge')
    expect(badge.exists()).toBe(true)
  })

  it('should toggle dropdown on click', async () => {
    mockNotificationStore.getNotifications.mockResolvedValue({
      data: {
        results: []
      }
    })

    wrapper = mount(NotificationBell, {
      global: {
      }
    })

    const bellContainer = wrapper.find('.bell-container')
    expect(wrapper.vm.showDropdown).toBe(false)

    await bellContainer.trigger('click')
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.showDropdown).toBe(true)
    expect(mockNotificationStore.getNotifications).toHaveBeenCalled()
  })

  it('should load notifications when dropdown opens', async () => {
    mockNotificationStore.getNotifications.mockResolvedValue({
      data: {
        results: [
          { id: 1, titulo: 'Test', mensaje: 'Test message', leida: false }
        ]
      }
    })

    wrapper = mount(NotificationBell, {
      global: {
      }
    })

    await wrapper.vm.toggleDropdown()
    await wrapper.vm.$nextTick()

    expect(mockNotificationStore.getNotifications).toHaveBeenCalledWith({
      page: 1,
      page_size: 5,
      ordering: '-fecha_creacion'
    })
  })

  it('should mark notification as read on click', async () => {
    mockNotificationStore.getNotifications.mockResolvedValue({
      data: {
        results: [
          { id: 1, titulo: 'Test', mensaje: 'Test message', leida: false }
        ]
      }
    })
    mockNotificationStore.markAsRead.mockResolvedValue(true)

    wrapper = mount(NotificationBell, {
      global: {
      }
    })

    await wrapper.vm.toggleDropdown()
    await wrapper.vm.$nextTick()

    const notification = wrapper.vm.recentNotifications[0]
    await wrapper.vm.handleNotificationClick(notification)

    expect(mockNotificationStore.markAsRead).toHaveBeenCalledWith(1)
    expect(notification.leida).toBe(true)
  })

  it('should mark all as read', async () => {
    mockNotificationStore.getNotifications.mockResolvedValue({
      data: {
        results: [
          { id: 1, titulo: 'Test 1', mensaje: 'Message 1', leida: false },
          { id: 2, titulo: 'Test 2', mensaje: 'Message 2', leida: false }
        ]
      }
    })
    mockNotificationStore.markAllAsRead.mockResolvedValue(true)

    wrapper = mount(NotificationBell, {
      global: {
      }
    })

    await wrapper.vm.toggleDropdown()
    await wrapper.vm.$nextTick()
    await wrapper.vm.markAllAsRead()
    await wrapper.vm.$nextTick()

    expect(mockNotificationStore.markAllAsRead).toHaveBeenCalled()
    expect(wrapper.vm.recentNotifications.every(n => n.leida)).toBe(true)
  })

  it('should navigate to notification center', async () => {
    vi.clearAllMocks()
    
    wrapper = mount(NotificationBell, {
      global: {
      }
    })

    await wrapper.vm.goToNotificationCenter()

    expect(mockRouter.push).toHaveBeenCalledWith('/notifications')
    expect(wrapper.vm.showDropdown).toBe(false)
  })

  it('should format time correctly', () => {
    wrapper = mount(NotificationBell, {
      global: {
      }
    })

    const now = new Date()
    const oneMinuteAgo = new Date(now.getTime() - 60 * 1000)
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000)

    expect(wrapper.vm.formatTime(oneMinuteAgo.toISOString())).toContain('m')
    expect(wrapper.vm.formatTime(oneHourAgo.toISOString())).toContain('h')
  })

  it('should truncate long messages', () => {
    wrapper = mount(NotificationBell, {
      global: {
      }
    })

    const longMessage = 'a'.repeat(100)
    const truncated = wrapper.vm.truncateMessage(longMessage)

    expect(truncated.length).toBeLessThanOrEqual(63)
    expect(truncated).toContain('...')
  })

  it('should get correct notification icon', () => {
    wrapper = mount(NotificationBell, {
      global: {
      }
    })

    expect(wrapper.vm.getNotificationIcon('info')).toContain('info-circle')
    expect(wrapper.vm.getNotificationIcon('error')).toContain('times-circle')
    expect(wrapper.vm.getNotificationIcon('success')).toContain('check-circle')
  })

  it('should close dropdown when clicking outside', async () => {
    wrapper = mount(NotificationBell, {
      global: {
      }
    })

    wrapper.vm.showDropdown = true
    await wrapper.vm.$nextTick()

    const event = new MouseEvent('click', { bubbles: true })
    Object.defineProperty(event, 'target', {
      value: document.createElement('div')
    })

    document.dispatchEvent(event)
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.showDropdown).toBe(false)
  })
})

