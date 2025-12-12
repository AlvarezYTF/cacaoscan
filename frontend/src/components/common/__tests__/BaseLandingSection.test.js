import { describe, it, expect, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseLandingSection from '../BaseLandingSection.vue'

describe('BaseLandingSection', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
  })

  describe('Rendering', () => {
    it('should render with title', () => {
      wrapper = mount(BaseLandingSection, {
        props: {
          title: 'Section Title'
        }
      })

      expect(wrapper.text()).toContain('Section Title')
    })

    it('should render with subtitle', () => {
      wrapper = mount(BaseLandingSection, {
        props: {
          title: 'Section Title',
          subtitle: 'Section Subtitle'
        }
      })

      expect(wrapper.text()).toContain('Section Title')
      expect(wrapper.text()).toContain('Section Subtitle')
    })
  })

  describe('Slots', () => {
    it('should render content slot when provided', () => {
      wrapper = mount(BaseLandingSection, {
        props: {
          title: 'Default Title'
        },
        slots: {
          content: '<div class="custom-content">Custom Content</div>'
        }
      })

      expect(wrapper.find('.custom-content').exists()).toBe(true)
      expect(wrapper.text()).not.toContain('Default Title')
    })

    it('should render footer slot when provided', () => {
      wrapper = mount(BaseLandingSection, {
        slots: {
          footer: '<div class="footer-content">Footer Content</div>'
        }
      })

      expect(wrapper.find('.footer-content').exists()).toBe(true)
    })
  })

  describe('Custom Classes', () => {
    it('should apply custom backgroundClass', () => {
      wrapper = mount(BaseLandingSection, {
        props: {
          backgroundClass: 'custom-bg-class'
        }
      })

      const section = wrapper.find('section')
      expect(section.classes()).toContain('custom-bg-class')
    })

    it('should apply custom containerClass', () => {
      wrapper = mount(BaseLandingSection, {
        props: {
          containerClass: 'custom-container-class'
        }
      })

      const section = wrapper.find('section')
      expect(section.classes()).toContain('custom-container-class')
    })
  })
})

