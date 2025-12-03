import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import SessionExpiredModal from '../SessionExpiredModal.vue'

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    logout: vi.fn()
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
      path: '/',
      name: 'home',
      params: {},
      query: {},
      meta: {}
    }
  },
  isReady: vi.fn().mockResolvedValue(true)
}

const mockRoute = {
  path: '/',
  name: 'home',
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

// Mock BaseModal component - define stub inside factory to avoid hoisting issues
vi.mock('../BaseModal.vue', () => {
  const BaseModalStub = {
    name: 'BaseModal',
    template: '<div v-if="show" class="fixed"><slot name="header"></slot><slot></slot><slot name="footer"></slot></div>',
    props: {
      show: {
        type: Boolean,
        default: false
      },
      title: String,
      subtitle: String,
      maxWidth: String,
      showCloseButton: Boolean,
      closeOnOverlay: Boolean
    },
    emits: ['close', 'update:show']
  }
  
  return {
    default: BaseModalStub
  }
})

describe('SessionExpiredModal', () => {
  let wrapper

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.useFakeTimers()
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
    vi.useRealTimers()
    vi.clearAllMocks()
  })

  it('should not render when visible is false', () => {
    wrapper = mount(SessionExpiredModal, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    expect(wrapper.find('.fixed').exists()).toBe(false)
  })

  it('should render when show is called', async () => {
    wrapper = mount(SessionExpiredModal, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    wrapper.vm.show()
    await wrapper.vm.$nextTick()
    await vi.runOnlyPendingTimersAsync()

    expect(wrapper.find('.fixed').exists()).toBe(true)
  })

  it('should display countdown', async () => {
    wrapper = mount(SessionExpiredModal, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    wrapper.vm.show()
    await wrapper.vm.$nextTick()
    // Don't run timers - we want to check the initial countdown value (5)
    // before the timer executes

    const text = wrapper.text()
    expect(text).toContain('5 segundos')
  })

  it('should decrease countdown every second', async () => {
    wrapper = mount(SessionExpiredModal, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    wrapper.vm.show()
    await wrapper.vm.$nextTick()
    
    // Verify initial countdown value before running timers
    expect(wrapper.text()).toContain('5 segundos')

    // Advance timer by 1 second (1000ms) to trigger the interval once
    // This should execute the interval callback and decrement from 5 to 4
    vi.advanceTimersByTime(1000)
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('4 segundos')
  })

  it('should redirect to login when countdown reaches 0', async () => {
    wrapper = mount(SessionExpiredModal, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    wrapper.vm.show()
    await wrapper.vm.$nextTick()
    await vi.runOnlyPendingTimersAsync()

    vi.advanceTimersByTime(5000)
    await wrapper.vm.$nextTick()
    await vi.runOnlyPendingTimersAsync()
    vi.advanceTimersByTime(300)
    await vi.runOnlyPendingTimersAsync()

    expect(mockRouter.push).toHaveBeenCalledWith('/login')
  })

  it('should redirect to login when button is clicked', async () => {
    wrapper = mount(SessionExpiredModal, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    wrapper.vm.show()
    await wrapper.vm.$nextTick()
    await vi.runOnlyPendingTimersAsync()

    const button = wrapper.find('button')
    expect(button.exists()).toBe(true)
    await button.trigger('click')
    vi.advanceTimersByTime(300)
    await vi.runOnlyPendingTimersAsync()

    expect(mockRouter.push).toHaveBeenCalledWith('/login')
  })

  it('should expose show method', () => {
    wrapper = mount(SessionExpiredModal, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    expect(typeof wrapper.vm.show).toBe('function')
  })

  it('should clear interval when redirecting to login', async () => {
    wrapper = mount(SessionExpiredModal, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    wrapper.vm.show()
    await wrapper.vm.$nextTick()
    await vi.runOnlyPendingTimersAsync()

    vi.advanceTimersByTime(5000)
    await wrapper.vm.$nextTick()
    await vi.runOnlyPendingTimersAsync()
    vi.advanceTimersByTime(300)
    await vi.runOnlyPendingTimersAsync()

    expect(mockRouter.push).toHaveBeenCalledWith('/login')
  })

  it('should handle update:show event', async () => {
    wrapper = mount(SessionExpiredModal, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    wrapper.vm.show()
    await wrapper.vm.$nextTick()
    await vi.runOnlyPendingTimersAsync()

    wrapper.vm.handleUpdateShow(false)
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.visible).toBe(false)
  })

  it('should clean up interval on unmount', () => {
    wrapper = mount(SessionExpiredModal, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    wrapper.vm.show()
    wrapper.unmount()

    expect(wrapper.vm.countdownInterval).toBeNull()
  })
})
