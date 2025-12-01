import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import SessionExpiredModal from '../SessionExpiredModal.vue'

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    logout: vi.fn()
  })
}))

describe('SessionExpiredModal', () => {
  let wrapper
  let router

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.useFakeTimers()
    // Create router with memory history to avoid $route redefinition issues
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/login', component: { template: '<div>Login</div>' } }
      ]
    })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.useRealTimers()
    vi.clearAllMocks()
  })

  it('should not render when visible is false', () => {
    wrapper = mount(SessionExpiredModal, {
      global: {
        plugins: [router]
      }
    })

    expect(wrapper.find('.fixed').exists()).toBe(false)
  })

  it('should render when show is called', async () => {
    wrapper = mount(SessionExpiredModal, {
      global: {
        plugins: [router]
      }
    })

    wrapper.vm.show()
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.fixed').exists()).toBe(true)
  })

  it('should display countdown', async () => {
    wrapper = mount(SessionExpiredModal, {
      global: {
        plugins: [router]
      }
    })

    wrapper.vm.show()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('5 segundos')
  })

  it('should decrease countdown every second', async () => {
    wrapper = mount(SessionExpiredModal, {
      global: {
        plugins: [router]
      }
    })

    wrapper.vm.show()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('5 segundos')

    vi.advanceTimersByTime(1000)
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('4 segundos')
  })

  it('should redirect to login when countdown reaches 0', async () => {
    const pushSpy = vi.spyOn(router, 'push')
    wrapper = mount(SessionExpiredModal, {
      global: {
        plugins: [router]
      }
    })

    wrapper.vm.show()
    await wrapper.vm.$nextTick()

    vi.advanceTimersByTime(5000)
    await wrapper.vm.$nextTick()
    vi.advanceTimersByTime(300)

    expect(pushSpy).toHaveBeenCalledWith('/login')
  })

  it('should redirect to login when button is clicked', async () => {
    const pushSpy = vi.spyOn(router, 'push')
    wrapper = mount(SessionExpiredModal, {
      global: {
        plugins: [router]
      }
    })

    wrapper.vm.show()
    await wrapper.vm.$nextTick()

    const button = wrapper.find('button')
    await button.trigger('click')
    vi.advanceTimersByTime(300)

    expect(pushSpy).toHaveBeenCalledWith('/login')
  })

  it('should expose show method', () => {
    wrapper = mount(SessionExpiredModal, {
      global: {
        plugins: [router]
      }
    })

    expect(typeof wrapper.vm.show).toBe('function')
  })
})

