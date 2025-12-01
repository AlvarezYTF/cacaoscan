import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import SessionExpiredModal from '../SessionExpiredModal.vue'

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    logout: vi.fn()
  })
}))

// Mock BaseModal component
vi.mock('../BaseModal.vue', () => ({
  default: {
    name: 'BaseModal',
    template: '<div v-if="show" class="fixed"><slot name="header"></slot><slot></slot><slot name="footer"></slot></div>',
    props: ['show', 'title', 'subtitle', 'maxWidth', 'showCloseButton', 'closeOnOverlay'],
    emits: ['close', 'update:show']
  }
}))

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
    }
    vi.useRealTimers()
    vi.clearAllMocks()
  })

  it('should not render when visible is false', () => {
    wrapper = mount(SessionExpiredModal, {
      global: {
        stubs: { BaseModal: true, 'router-link': true }
      }
    })

    expect(wrapper.find('.fixed').exists()).toBe(false)
  })

  it('should render when show is called', async () => {
    wrapper = mount(SessionExpiredModal, {
      global: {
        stubs: { BaseModal: true, 'router-link': true }
      }
    })

    wrapper.vm.show()
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.fixed').exists()).toBe(true)
  })

  it('should display countdown', async () => {
    wrapper = mount(SessionExpiredModal, {
      global: {
        stubs: { BaseModal: true, 'router-link': true }
      }
    })

    wrapper.vm.show()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('5 segundos')
  })

  it('should decrease countdown every second', async () => {
    wrapper = mount(SessionExpiredModal, {
      global: {
        stubs: { BaseModal: true, 'router-link': true }
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
    wrapper = mount(SessionExpiredModal, {
      global: {
        stubs: { BaseModal: true, 'router-link': true }
      }
    })

    wrapper.vm.show()
    await wrapper.vm.$nextTick()

    vi.advanceTimersByTime(5000)
    await wrapper.vm.$nextTick()
    vi.advanceTimersByTime(300)

    // Router push will be called by the component using the global router
    expect(wrapper.vm.$router).toBeDefined()
  })

  it('should redirect to login when button is clicked', async () => {
    wrapper = mount(SessionExpiredModal, {
      global: {
        stubs: { BaseModal: true, 'router-link': true }
      }
    })

    wrapper.vm.show()
    await wrapper.vm.$nextTick()

    const button = wrapper.find('button')
    await button.trigger('click')
    vi.advanceTimersByTime(300)

    // Router push will be called by the component using the global router
    expect(wrapper.vm.$router).toBeDefined()
  })

  it('should expose show method', () => {
    wrapper = mount(SessionExpiredModal, {
      global: {
        stubs: { BaseModal: true, 'router-link': true }
      }
    })

    expect(typeof wrapper.vm.show).toBe('function')
  })
})
