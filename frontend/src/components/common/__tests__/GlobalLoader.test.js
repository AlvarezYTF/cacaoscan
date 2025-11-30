import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import GlobalLoader from '../GlobalLoader.vue'

describe('GlobalLoader', () => {
  let wrapper

  beforeEach(() => {
    vi.useFakeTimers()
    globalThis.addEventListener = vi.fn()
    globalThis.removeEventListener = vi.fn()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.useRealTimers()
    vi.clearAllMocks()
  })

  it('should render when isLoading is true', async () => {
    wrapper = mount(GlobalLoader)
    
    // Trigger loading
    globalThis.showGlobalLoading('Test', 'Message')
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.fixed').exists()).toBe(true)
  })

  it('should not render when isLoading is false', () => {
    wrapper = mount(GlobalLoader)

    expect(wrapper.find('.fixed').exists()).toBe(false)
  })

  it('should display loading text and message', async () => {
    wrapper = mount(GlobalLoader)
    
    globalThis.showGlobalLoading('Loading...', 'Please wait')
    await wrapper.vm.$nextTick()

    const text = wrapper.text()
    expect(text).toContain('Loading...')
    expect(text).toContain('Please wait')
  })

  it('should show progress bar', async () => {
    wrapper = mount(GlobalLoader)
    
    globalThis.showGlobalLoading()
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.bg-gray-200').exists()).toBe(true)
  })

  it('should listen to route-loading-start event', () => {
    wrapper = mount(GlobalLoader)

    expect(globalThis.addEventListener).toHaveBeenCalledWith('route-loading-start', expect.any(Function))
  })

  it('should listen to route-loading-end event', () => {
    wrapper = mount(GlobalLoader)

    expect(globalThis.addEventListener).toHaveBeenCalledWith('route-loading-end', expect.any(Function))
  })

  it('should listen to api-loading-start event', () => {
    wrapper = mount(GlobalLoader)

    expect(globalThis.addEventListener).toHaveBeenCalledWith('api-loading-start', expect.any(Function))
  })

  it('should listen to api-loading-end event', () => {
    wrapper = mount(GlobalLoader)

    expect(globalThis.addEventListener).toHaveBeenCalledWith('api-loading-end', expect.any(Function))
  })

  it('should clean up event listeners on unmount', () => {
    wrapper = mount(GlobalLoader)
    wrapper.unmount()

    expect(globalThis.removeEventListener).toHaveBeenCalled()
  })
})

