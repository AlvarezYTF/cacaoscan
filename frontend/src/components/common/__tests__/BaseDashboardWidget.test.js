/**
 * Unit tests for BaseDashboardWidget component
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseDashboardWidget from '../BaseDashboardWidget.vue'

describe('BaseDashboardWidget', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
  })

  describe('Props validation', () => {
    it('should accept title prop', () => {
      wrapper = mount(BaseDashboardWidget, {
        props: {
          title: 'Test Title'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should accept variant prop', () => {
      wrapper = mount(BaseDashboardWidget, {
        props: {
          variant: 'primary'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should use default variant when invalid variant is provided', () => {
      // Vue 3 validators don't throw errors, they only emit warnings in development
      // The component should still mount and use default behavior
      wrapper = mount(BaseDashboardWidget, {
        props: {
          variant: 'invalid'
        }
      })
      
      // Component should mount successfully
      expect(wrapper.exists()).toBe(true)
      // Invalid variant should fallback to default behavior
      expect(wrapper.vm.iconBgClass).toContain('bg-gray-100')
    })
  })

  describe('Rendering', () => {
    it('should render title when provided', () => {
      wrapper = mount(BaseDashboardWidget, {
        props: {
          title: 'Test Title'
        }
      })

      expect(wrapper.text()).toContain('Test Title')
    })

    it('should render subtitle when provided', () => {
      wrapper = mount(BaseDashboardWidget, {
        props: {
          title: 'Test Title',
          subtitle: 'Test Subtitle'
        }
      })

      expect(wrapper.text()).toContain('Test Subtitle')
    })

    it('should show header when showHeader is true', () => {
      wrapper = mount(BaseDashboardWidget, {
        props: {
          showHeader: true
        }
      })

      expect(wrapper.find('.base-dashboard-widget-header').exists()).toBe(true)
    })

    it('should not show header when showHeader is false', () => {
      wrapper = mount(BaseDashboardWidget, {
        props: {
          showHeader: false
        }
      })

      expect(wrapper.find('.base-dashboard-widget-header').exists()).toBe(false)
    })

    it('should show footer when showFooter is true', () => {
      wrapper = mount(BaseDashboardWidget, {
        props: {
          showFooter: true
        }
      })

      expect(wrapper.find('.base-dashboard-widget-footer').exists()).toBe(true)
    })

    it('should apply custom widgetClass when provided', () => {
      wrapper = mount(BaseDashboardWidget, {
        props: {
          widgetClass: 'custom-class'
        }
      })

      const widget = wrapper.find('.base-dashboard-widget')
      expect(widget.classes()).toContain('custom-class')
    })
  })

  describe('Computed properties', () => {
    it('should apply correct icon background class for default variant', () => {
      wrapper = mount(BaseDashboardWidget, {
        props: {
          variant: 'default',
          icon: 'fas fa-chart'
        }
      })

      expect(wrapper.vm.iconBgClass).toContain('bg-gray-100')
    })

    it('should apply correct icon background class for primary variant', () => {
      wrapper = mount(BaseDashboardWidget, {
        props: {
          variant: 'primary',
          icon: 'fas fa-chart'
        }
      })

      expect(wrapper.vm.iconBgClass).toContain('bg-blue-100')
    })

    it('should apply correct icon background class for success variant', () => {
      wrapper = mount(BaseDashboardWidget, {
        props: {
          variant: 'success',
          icon: 'fas fa-chart'
        }
      })

      expect(wrapper.vm.iconBgClass).toContain('bg-green-100')
    })
  })

  describe('Slots', () => {
    it('should render header slot when provided', () => {
      wrapper = mount(BaseDashboardWidget, {
        slots: {
          header: '<div>Custom Header</div>'
        }
      })

      expect(wrapper.text()).toContain('Custom Header')
    })

    it('should render body slot when provided', () => {
      wrapper = mount(BaseDashboardWidget, {
        slots: {
          body: '<div>Custom Body</div>'
        }
      })

      expect(wrapper.text()).toContain('Custom Body')
    })

    it('should render footer slot when provided', () => {
      wrapper = mount(BaseDashboardWidget, {
        props: {
          showFooter: true
        },
        slots: {
          footer: '<div>Custom Footer</div>'
        }
      })

      expect(wrapper.text()).toContain('Custom Footer')
    })

    it('should render header-actions slot when provided', () => {
      wrapper = mount(BaseDashboardWidget, {
        slots: {
          'header-actions': '<button>Action</button>'
        }
      })

      expect(wrapper.text()).toContain('Action')
    })
  })
})

