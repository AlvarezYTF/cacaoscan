import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import GlobalLoader from '../GlobalLoader.vue'

describe('GlobalLoader', () => {
  let wrapper
  let container
  let originalAddEventListener
  let originalRemoveEventListener
  let originalDispatchEvent
  let eventListeners

  const mountComponent = () => {
    // Create a container for teleport
    container = document.createElement('div')
    container.id = 'teleport-container'
    document.body.appendChild(container)
    
    return mount(GlobalLoader, {
      attachTo: document.body
    })
  }

  const triggerLoading = async (title, message) => {
    // Wait for component to mount and register global functions
    await nextTick()
    await wrapper.vm.$nextTick()
    
    // Wait a bit more to ensure onMounted has run and global functions are registered
    let attempts = 0
    while (!globalThis.showGlobalLoading && attempts < 10) {
      await new Promise(resolve => setTimeout(resolve, 10))
      attempts++
    }
    
    expect(globalThis.showGlobalLoading).toBeDefined()
    
    if (globalThis.showGlobalLoading) {
      globalThis.showGlobalLoading(title, message)
    }
    
    // Wait for the loading state to update and DOM to render
    await nextTick()
    await wrapper.vm.$nextTick()
    // Give time for teleport to render and reactive updates
    await new Promise(resolve => setTimeout(resolve, 50))
  }

  beforeEach(() => {
    // Don't use fake timers as they interfere with component lifecycle and DOM updates
    // vi.useFakeTimers()
    // Save original methods
    originalAddEventListener = globalThis.addEventListener
    originalRemoveEventListener = globalThis.removeEventListener
    
    // Store event listeners so we can call them when events are dispatched
    eventListeners = new Map()
    
    globalThis.addEventListener = vi.fn((eventName, handler) => {
      if (!eventListeners.has(eventName)) {
        eventListeners.set(eventName, [])
      }
      eventListeners.get(eventName).push(handler)
    })
    
    globalThis.removeEventListener = vi.fn((eventName, handler) => {
      if (eventListeners.has(eventName)) {
        const handlers = eventListeners.get(eventName)
        const index = handlers.indexOf(handler)
        if (index > -1) {
          handlers.splice(index, 1)
        }
      }
    })
    
    // Override dispatchEvent to call stored handlers
    originalDispatchEvent = globalThis.dispatchEvent
    globalThis.dispatchEvent = (event) => {
      // Call stored handlers first
      const handlers = eventListeners.get(event.type) || []
      for (const handler of handlers) {
        if (typeof handler === 'function') {
          try {
            handler(event)
          } catch (error) {
            throw error
          }
        }
      }
      // Also call original if it exists
      if (originalDispatchEvent && typeof originalDispatchEvent === 'function') {
        return originalDispatchEvent.call(globalThis, event)
      }
      return true
    }
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    if (container) {
      if (container.parentNode) {
        container.remove()
      }
      container = null
    }
    // Clean up any teleported content
    const teleported = document.querySelectorAll('.fixed')
    for (const el of teleported) {
      el.remove()
    }
    // Clean up global functions
    delete globalThis.showGlobalLoading
    delete globalThis.hideGlobalLoading
    // Restore original methods
    if (originalAddEventListener) {
      globalThis.addEventListener = originalAddEventListener
    }
    if (originalRemoveEventListener) {
      globalThis.removeEventListener = originalRemoveEventListener
    }
    if (originalDispatchEvent) {
      globalThis.dispatchEvent = originalDispatchEvent
    }
    // vi.useRealTimers() // Not needed if we're not using fake timers
    vi.clearAllMocks()
  })

  it('should render when isLoading is true', async () => {
    wrapper = mountComponent()
    await triggerLoading('Test', 'Message')
    // Since the component uses teleport, we need to search in document.body
    const loader = document.querySelector('.fixed')
    expect(loader).toBeTruthy()
  })

  it('should not render when isLoading is false', () => {
    wrapper = mountComponent()
    const loader = document.querySelector('.fixed')
    expect(loader).toBeFalsy()
  })

  it('should display loading text and message', async () => {
    wrapper = mountComponent()
    await triggerLoading('Loading...', 'Please wait')
    // Since the component uses teleport, we need to search in document.body
    const loader = document.querySelector('.fixed')
    expect(loader).toBeTruthy()
    expect(loader).toBeInstanceOf(HTMLElement)
    const text = loader?.textContent || loader?.innerText || ''
    expect(text).toContain('Loading...')
    expect(text).toContain('Please wait')
  })

  it('should show progress bar', async () => {
    wrapper = mountComponent()
    await triggerLoading()
    
    // Since the component uses teleport, we need to search in document.body
    const progressBar = document.querySelector('.bg-gray-200')
    expect(progressBar).toBeTruthy()
  })

  const testEventListening = (eventName) => {
    it(`should listen to ${eventName} event`, () => {
      wrapper = mountComponent()
      expect(globalThis.addEventListener).toHaveBeenCalledWith(eventName, expect.any(Function))
    })
  }

  testEventListening('route-loading-start')
  testEventListening('route-loading-end')
  testEventListening('api-loading-start')
  testEventListening('api-loading-end')

  it('should clean up event listeners on unmount', () => {
    wrapper = mountComponent()
    wrapper.unmount()
    expect(globalThis.removeEventListener).toHaveBeenCalled()
  })

  it('should handle route-loading-start event', async () => {
    wrapper = mountComponent()
    await wrapper.vm.$nextTick()
    // Wait for onMounted to complete and register event listeners
    await new Promise(resolve => setTimeout(resolve, 10))

    const event = new CustomEvent('route-loading-start', { detail: { to: { name: 'Test' } } })
    globalThis.dispatchEvent(event)
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 50))

    expect(wrapper.vm.isLoading).toBe(true)
  })

  it('should handle route-loading-end event', async () => {
    wrapper = mountComponent()
    await wrapper.vm.$nextTick()
    // Wait for onMounted to complete and register event listeners
    await new Promise(resolve => setTimeout(resolve, 50))

    wrapper.vm.isLoading = true
    await wrapper.vm.$nextTick()
    
    const event = new CustomEvent('route-loading-end')
    globalThis.dispatchEvent(event)
    await wrapper.vm.$nextTick()
    // hideLoading uses setTimeout of 200ms, so wait longer
    await new Promise(resolve => setTimeout(resolve, 250))
    // Wait for Vue to process the reactive change after setTimeout
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.isLoading).toBe(false)
  })

  it('should handle api-loading-start event', async () => {
    wrapper = mountComponent()
    await wrapper.vm.$nextTick()

    const event = new CustomEvent('api-loading-start', { detail: { type: 'upload', message: 'Please wait' } })
    globalThis.dispatchEvent(event)
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 50))

    expect(wrapper.vm.isLoading).toBe(true)
  })

  it('should handle api-loading-end event', async () => {
    wrapper = mountComponent()
    await wrapper.vm.$nextTick()

    wrapper.vm.isLoading = true
    const event = new CustomEvent('api-loading-end')
    globalThis.dispatchEvent(event)
    await wrapper.vm.$nextTick()
    // hideLoading uses setTimeout of 200ms, so wait longer
    await new Promise(resolve => setTimeout(resolve, 250))
    // Wait for Vue to process the reactive change after setTimeout
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.isLoading).toBe(false)
  })

  it('should hide loading when hideGlobalLoading is called', async () => {
    wrapper = mountComponent()
    await wrapper.vm.$nextTick()
    
    // Wait for component to mount and register global functions
    let attempts = 0
    while (!globalThis.hideGlobalLoading && attempts < 10) {
      await new Promise(resolve => setTimeout(resolve, 10))
      attempts++
    }
    
    expect(globalThis.hideGlobalLoading).toBeDefined()

    wrapper.vm.isLoading = true
    if (globalThis.hideGlobalLoading) {
      globalThis.hideGlobalLoading()
    }
    await wrapper.vm.$nextTick()
    // hideLoading uses setTimeout(200ms), so we need to wait at least 250ms
    await new Promise(resolve => setTimeout(resolve, 250))

    expect(wrapper.vm.isLoading).toBe(false)
  })

  it('should update title and message when showGlobalLoading is called', async () => {
    wrapper = mountComponent()
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 50))

    if (globalThis.showGlobalLoading) {
      globalThis.showGlobalLoading('New Title', 'New Message')
    }
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 50))

    expect(wrapper.vm.title).toBe('New Title')
    expect(wrapper.vm.message).toBe('New Message')
  })
})


