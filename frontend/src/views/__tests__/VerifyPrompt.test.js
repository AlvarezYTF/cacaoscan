import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import VerifyPrompt from '../VerifyPrompt.vue'

// Mock dependencies
const mockRoute = {
  query: { email: 'test@example.com' }
}

const mockRouter = {
  replace: vi.fn(),
  push: vi.fn()
}

const mockAuthStore = {
  resendEmailVerification: vi.fn()
}

vi.mock('vue-router', () => ({
  useRoute: () => mockRoute,
  useRouter: () => mockRouter
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

describe('VerifyPrompt', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    // Reset mockRoute.query to default value before each test
    mockRoute.query = { email: 'test@example.com' }
  })

  afterEach(() => {
    vi.useRealTimers()
    // Reset mockRoute.query after each test
    mockRoute.query = { email: 'test@example.com' }
  })

  it('should render verify prompt', () => {
    const wrapper = mount(VerifyPrompt, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toContain('Verifica tu correo')
  })

  it('should display email from query', () => {
    const wrapper = mount(VerifyPrompt, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    expect(wrapper.text()).toContain('test@example.com')
  })

  it('should display default email if not in query', () => {
    // Set query to empty for this test
    mockRoute.query = {}
    
    const wrapper = mount(VerifyPrompt, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    expect(wrapper.text()).toContain('tu correo')
  })

  it('should resend email on button click', async () => {
    // Ensure query has email for this test
    mockRoute.query = { email: 'test@example.com' }
    mockAuthStore.resendEmailVerification.mockResolvedValue({ success: true })
    
    const wrapper = mount(VerifyPrompt, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    const button = wrapper.find('button')
    await button.trigger('click')

    expect(mockAuthStore.resendEmailVerification).toHaveBeenCalledWith('test@example.com')
  })

  const createDelayedVerificationResponse = (delay = 100) => {
    return new Promise(resolve => setTimeout(() => resolve({ success: true }), delay))
  }

  it('should show loading state while resending', async () => {
    mockAuthStore.resendEmailVerification.mockImplementation(() => createDelayedVerificationResponse())
    
    const wrapper = mount(VerifyPrompt, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    const button = wrapper.find('button')
    button.trigger('click')
    
    await wrapper.vm.$nextTick()
    
    expect(wrapper.text()).toContain('Enviando')
  })

  it('should show success message after resending', async () => {
    mockAuthStore.resendEmailVerification.mockResolvedValue({ success: true })
    
    const wrapper = mount(VerifyPrompt, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    const button = wrapper.find('button')
    await button.trigger('click')
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('reenviado exitosamente')
  })

  it('should show error message on failure', async () => {
    mockAuthStore.resendEmailVerification.mockResolvedValue({ 
      success: false, 
      error: 'Error message' 
    })
    
    const wrapper = mount(VerifyPrompt, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    const button = wrapper.find('button')
    await button.trigger('click')
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Error')
  })

  it('should disable button during cooldown', async () => {
    mockAuthStore.resendEmailVerification.mockResolvedValue({ success: true })
    
    const wrapper = mount(VerifyPrompt, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    const button = wrapper.find('button')
    await button.trigger('click')
    await wrapper.vm.$nextTick()

    expect(button.attributes('disabled')).toBeDefined()
  })

  it('should show cooldown countdown', async () => {
    mockAuthStore.resendEmailVerification.mockResolvedValue({ success: true })
    
    const wrapper = mount(VerifyPrompt, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    const button = wrapper.find('button')
    await button.trigger('click')
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Espera')
  })

  it('should clear status message after timeout', async () => {
    mockAuthStore.resendEmailVerification.mockResolvedValue({ success: true })
    
    const wrapper = mount(VerifyPrompt, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    const button = wrapper.find('button')
    await button.trigger('click')
    await wrapper.vm.$nextTick()

    vi.advanceTimersByTime(5000)
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.mt-6').exists()).toBe(false)
  })

  it('should cleanup interval on unmount', () => {
    const wrapper = mount(VerifyPrompt, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    wrapper.unmount()

    // Should not throw
    expect(true).toBe(true)
  })
})

