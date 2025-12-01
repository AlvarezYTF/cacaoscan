import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { nextTick } from 'vue'
import GlobalLoader from '../GlobalLoader.vue'

describe('GlobalLoader', () => {
  let wrapper
  let container

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
    globalThis.addEventListener = vi.fn()
    globalThis.removeEventListener = vi.fn()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    if (container) {
      try {
        document.body.removeChild(container)
      } catch (e) {
        // Container may have already been removed
      }
      container = null
    }
    // Clean up any teleported content
    const teleported = document.querySelectorAll('.fixed')
    teleported.forEach(el => el.remove())
    // Clean up global functions
    delete globalThis.showGlobalLoading
    delete globalThis.hideGlobalLoading
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
})


