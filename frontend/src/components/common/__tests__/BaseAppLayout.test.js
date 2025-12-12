/**
 * Unit tests for BaseAppLayout component
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseAppLayout from '../BaseAppLayout.vue'

vi.mock('../GlobalLoader.vue', () => ({
  default: {
    name: 'GlobalLoader',
    template: '<div class="global-loader">Loading...</div>'
  }
}))

vi.mock('../SessionExpiredModal.vue', () => ({
  default: {
    name: 'SessionExpiredModal',
    template: '<div class="session-modal"></div>',
    methods: {
      show: vi.fn()
    }
  }
}))

describe('BaseAppLayout', () => {
  let wrapper

  const mountOptions = {
    global: {
      stubs: {
        'router-view': {
          template: '<div class="router-view">Router View</div>'
        },
        RouterView: {
          template: '<div class="router-view">Router View</div>'
        }
      }
    }
  }

  beforeEach(() => {
    vi.clearAllMocks()
    globalThis.showSessionExpiredModal = undefined
  })

  describe('Props validation', () => {
    it('should accept containerClass prop', () => {
      wrapper = mount(BaseAppLayout, {
        ...mountOptions,
        props: {
          containerClass: 'custom-class'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should default showGlobalLoader to true', () => {
      wrapper = mount(BaseAppLayout, {
        ...mountOptions
      })
      expect(wrapper.props('showGlobalLoader')).toBe(true)
    })

    it('should default showSessionModal to true', () => {
      wrapper = mount(BaseAppLayout, {
        ...mountOptions
      })
      expect(wrapper.props('showSessionModal')).toBe(true)
    })
  })

  describe('Rendering', () => {
    it('should render RouterView by default', () => {
      wrapper = mount(BaseAppLayout, {
        ...mountOptions
      })

      expect(wrapper.find('.router-view').exists()).toBe(true)
    })

    it('should render GlobalLoader when showGlobalLoader is true', () => {
      wrapper = mount(BaseAppLayout, {
        ...mountOptions,
        props: {
          showGlobalLoader: true
        }
      })

      expect(wrapper.findComponent({ name: 'GlobalLoader' }).exists()).toBe(true)
    })

    it('should not render GlobalLoader when showGlobalLoader is false', () => {
      wrapper = mount(BaseAppLayout, {
        ...mountOptions,
        props: {
          showGlobalLoader: false
        }
      })

      expect(wrapper.findComponent({ name: 'GlobalLoader' }).exists()).toBe(false)
    })

    it('should render SessionExpiredModal when showSessionModal is true', () => {
      wrapper = mount(BaseAppLayout, {
        ...mountOptions,
        props: {
          showSessionModal: true
        }
      })

      expect(wrapper.findComponent({ name: 'SessionExpiredModal' }).exists()).toBe(true)
    })

    it('should apply containerClass when provided', () => {
      wrapper = mount(BaseAppLayout, {
        ...mountOptions,
        props: {
          containerClass: 'custom-class'
        }
      })

      const container = wrapper.find('.app')
      expect(container.classes()).toContain('custom-class')
    })
  })

  describe('Slots', () => {
    it('should render default slot content', () => {
      wrapper = mount(BaseAppLayout, {
        ...mountOptions,
        slots: {
          default: '<div>Custom Content</div>'
        }
      })

      expect(wrapper.text()).toContain('Custom Content')
    })

    it('should render global slot content', () => {
      wrapper = mount(BaseAppLayout, {
        ...mountOptions,
        slots: {
          global: '<div>Global Content</div>'
        }
      })

      expect(wrapper.text()).toContain('Global Content')
    })
  })

  describe('Lifecycle', () => {
    it('should expose showSessionExpiredModal globally on mount', async () => {
      wrapper = mount(BaseAppLayout, {
        ...mountOptions,
        props: {
          showSessionModal: true
        }
      })

      await wrapper.vm.$nextTick()
      expect(typeof globalThis.showSessionExpiredModal).toBe('function')
    })
  })
})
