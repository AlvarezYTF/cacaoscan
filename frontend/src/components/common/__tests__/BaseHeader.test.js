import { describe, it, expect, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseHeader from '../BaseHeader.vue'

describe('BaseHeader', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
  })

  describe('Rendering', () => {
    it('should render with title', () => {
      wrapper = mount(BaseHeader, {
        props: {
          title: 'Page Title'
        }
      })

      expect(wrapper.text()).toContain('Page Title')
    })

    it('should render with subtitle', () => {
      wrapper = mount(BaseHeader, {
        props: {
          title: 'Page Title',
          subtitle: 'Page Subtitle'
        }
      })

      expect(wrapper.text()).toContain('Page Title')
      expect(wrapper.text()).toContain('Page Subtitle')
    })
  })

  describe('Slots', () => {
    it('should render brand slot when provided', () => {
      wrapper = mount(BaseHeader, {
        props: {
          title: 'Default Title'
        },
        slots: {
          brand: '<div class="custom-brand">Custom Brand</div>'
        }
      })

      expect(wrapper.find('.custom-brand').exists()).toBe(true)
      expect(wrapper.text()).not.toContain('Default Title')
    })

    it('should render actions slot when provided', () => {
      wrapper = mount(BaseHeader, {
        props: {
          title: 'Page Title'
        },
        slots: {
          actions: '<button class="action-btn">Action</button>'
        }
      })

      expect(wrapper.find('.action-btn').exists()).toBe(true)
    })

    it('should show actions section when showActions is true', () => {
      wrapper = mount(BaseHeader, {
        props: {
          title: 'Page Title',
          showActions: true
        }
      })

      const actionsSection = wrapper.find('.flex.items-center.gap-3')
      expect(actionsSection.exists()).toBe(true)
    })
  })

  describe('Custom Classes', () => {
    it('should apply custom headerClass', () => {
      wrapper = mount(BaseHeader, {
        props: {
          title: 'Page Title',
          headerClass: 'custom-header-class'
        }
      })

      const header = wrapper.find('header')
      expect(header.classes()).toContain('custom-header-class')
    })
  })
})

