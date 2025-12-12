/**
 * Unit tests for BaseFincasSection component
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseFincasSection from '../BaseFincasSection.vue'

describe('BaseFincasSection', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Props validation', () => {
    it('should accept title prop', () => {
      wrapper = mount(BaseFincasSection, {
        props: {
          title: 'Test Title'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should accept variant prop', () => {
      wrapper = mount(BaseFincasSection, {
        props: {
          variant: 'bordered'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should handle invalid variant prop gracefully', () => {
      // Vue 3 validators only emit warnings in development, they don't throw errors
      // The component will still render but the variant won't match any valid option
      wrapper = mount(BaseFincasSection, {
        props: {
          variant: 'invalid'
        }
      })
      
      // Component should still render
      expect(wrapper.exists()).toBe(true)
      // Container class should be empty since 'invalid' doesn't match any variant
      expect(wrapper.vm.containerClass).toBe('')
    })
  })

  describe('Rendering', () => {
    it('should render title when provided', () => {
      wrapper = mount(BaseFincasSection, {
        props: {
          title: 'Test Title'
        }
      })

      expect(wrapper.text()).toContain('Test Title')
    })

    it('should render subtitle when provided', () => {
      wrapper = mount(BaseFincasSection, {
        props: {
          title: 'Test Title',
          subtitle: 'Test Subtitle'
        }
      })

      expect(wrapper.text()).toContain('Test Subtitle')
    })

    it('should show header when title is provided', () => {
      wrapper = mount(BaseFincasSection, {
        props: {
          title: 'Test Title'
        }
      })

      expect(wrapper.find('.px-4').exists()).toBe(true)
    })

    it('should apply noPadding class when noPadding is true', () => {
      wrapper = mount(BaseFincasSection, {
        props: {
          noPadding: true
        }
      })

      const content = wrapper.find('.p-4')
      expect(content.classes()).toContain('p-0')
    })
  })

  describe('Computed properties', () => {
    it('should apply default container class', () => {
      wrapper = mount(BaseFincasSection, {
        props: {
          variant: 'default'
        }
      })

      expect(wrapper.vm.containerClass).toBe('')
    })

    it('should apply bordered container class', () => {
      wrapper = mount(BaseFincasSection, {
        props: {
          variant: 'bordered'
        }
      })

      expect(wrapper.vm.containerClass).toBe('border-2')
    })

    it('should apply shadow container class', () => {
      wrapper = mount(BaseFincasSection, {
        props: {
          variant: 'shadow'
        }
      })

      expect(wrapper.vm.containerClass).toBe('shadow-md')
    })
  })

  describe('Slots', () => {
    it('should render default slot content', () => {
      wrapper = mount(BaseFincasSection, {
        slots: {
          default: '<div>Content</div>'
        }
      })

      expect(wrapper.text()).toContain('Content')
    })

    it('should render header slot when provided', () => {
      wrapper = mount(BaseFincasSection, {
        slots: {
          header: '<div>Custom Header</div>'
        }
      })

      expect(wrapper.text()).toContain('Custom Header')
    })

    it('should render footer slot when provided', () => {
      wrapper = mount(BaseFincasSection, {
        slots: {
          footer: '<div>Footer</div>'
        }
      })

      expect(wrapper.text()).toContain('Footer')
    })
  })
})

