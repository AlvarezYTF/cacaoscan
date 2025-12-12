import { describe, it, expect, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseLandingLayout from '../BaseLandingLayout.vue'

describe('BaseLandingLayout', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
  })

  it('should render main content slot', () => {
    wrapper = mount(BaseLandingLayout, {
      slots: {
        default: '<div class="main-content">Main Content</div>'
      }
    })

    expect(wrapper.find('.main-content').exists()).toBe(true)
    expect(wrapper.text()).toContain('Main Content')
  })

  it('should render header slot when provided', () => {
    wrapper = mount(BaseLandingLayout, {
      slots: {
        header: '<div class="header-content">Header Content</div>',
        default: '<div>Main Content</div>'
      }
    })

    expect(wrapper.find('.header-content').exists()).toBe(true)
    expect(wrapper.text()).toContain('Header Content')
  })

  it('should render footer slot when provided', () => {
    wrapper = mount(BaseLandingLayout, {
      slots: {
        footer: '<div class="footer-content">Footer Content</div>',
        default: '<div>Main Content</div>'
      }
    })

    expect(wrapper.find('.footer-content').exists()).toBe(true)
    expect(wrapper.text()).toContain('Footer Content')
  })

  it('should not render header when header slot is not provided', () => {
    wrapper = mount(BaseLandingLayout, {
      slots: {
        default: '<div>Main Content</div>'
      }
    })

    const header = wrapper.find('header')
    expect(header.exists()).toBe(false)
  })

  it('should not render footer when footer slot is not provided', () => {
    wrapper = mount(BaseLandingLayout, {
      slots: {
        default: '<div>Main Content</div>'
      }
    })

    const footer = wrapper.find('footer')
    expect(footer.exists()).toBe(false)
  })
})

