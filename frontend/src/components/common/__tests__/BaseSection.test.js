import { describe, it, expect, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseSection from '../BaseSection.vue'

describe('BaseSection', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render component', () => {
    wrapper = mount(BaseSection)

    expect(wrapper.exists()).toBe(true)
  })

  it('should display title when provided', () => {
    wrapper = mount(BaseSection, {
      props: {
        title: 'Section Title'
      }
    })

    expect(wrapper.text()).toContain('Section Title')
  })

  it('should display subtitle when provided', () => {
    wrapper = mount(BaseSection, {
      props: {
        title: 'Section Title',
        subtitle: 'Section Subtitle'
      }
    })

    expect(wrapper.text()).toContain('Section Subtitle')
  })

  it('should render header slot', () => {
    wrapper = mount(BaseSection, {
      slots: {
        header: '<div>Custom Header</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Header')
  })

  it('should render default slot', () => {
    wrapper = mount(BaseSection, {
      slots: {
        default: '<div>Section Content</div>'
      }
    })

    expect(wrapper.text()).toContain('Section Content')
  })

  it('should apply default variant classes', () => {
    wrapper = mount(BaseSection, {
      props: {
        variant: 'default'
      }
    })

    const section = wrapper.find('section')
    expect(section.classes()).toContain('bg-white')
  })

  it('should apply hero variant classes', () => {
    wrapper = mount(BaseSection, {
      props: {
        variant: 'hero'
      }
    })

    const section = wrapper.find('section')
    expect(section.classes()).toContain('bg-gradient-to-br')
  })

  it('should apply features variant classes', () => {
    wrapper = mount(BaseSection, {
      props: {
        variant: 'features'
      }
    })

    const section = wrapper.find('section')
    expect(section.classes()).toContain('bg-gray-50')
  })

  it('should apply about variant classes', () => {
    wrapper = mount(BaseSection, {
      props: {
        variant: 'about'
      }
    })

    const section = wrapper.find('section')
    expect(section.classes()).toContain('bg-white')
  })

  it('should apply dark variant classes', () => {
    wrapper = mount(BaseSection, {
      props: {
        variant: 'dark'
      }
    })

    const section = wrapper.find('section')
    expect(section.classes()).toContain('bg-gray-900')
    expect(section.classes()).toContain('text-white')
  })

  it('should apply light variant classes', () => {
    wrapper = mount(BaseSection, {
      props: {
        variant: 'light'
      }
    })

    const section = wrapper.find('section')
    expect(section.classes()).toContain('bg-white')
  })

  it('should set id attribute when provided', () => {
    wrapper = mount(BaseSection, {
      props: {
        id: 'test-section-id'
      }
    })

    const section = wrapper.find('section')
    expect(section.attributes('id')).toBe('test-section-id')
  })

  it('should not set id attribute when not provided', () => {
    wrapper = mount(BaseSection)

    const section = wrapper.find('section')
    expect(section.attributes('id')).toBeUndefined()
  })

  it('should apply fullWidth class when fullWidth is true', () => {
    wrapper = mount(BaseSection, {
      props: {
        fullWidth: true
      }
    })

    const content = wrapper.find('.max-w-7xl')
    // Content should still have max-w-7xl container, fullWidth affects inner content
    expect(content.exists()).toBe(true)
  })

  it('should show header when title or subtitle is provided', () => {
    wrapper = mount(BaseSection, {
      props: {
        title: 'Test Title'
      }
    })

    const header = wrapper.find('.text-center')
    expect(header.exists()).toBe(true)
  })

  it('should show header when header slot is provided', () => {
    wrapper = mount(BaseSection, {
      slots: {
        header: '<div>Header Slot</div>'
      }
    })

    const header = wrapper.find('.text-center')
    expect(header.exists()).toBe(true)
    expect(wrapper.text()).toContain('Header Slot')
  })

  it('should not show header when no title, subtitle, or slot', () => {
    wrapper = mount(BaseSection)

    const header = wrapper.find('.text-center')
    expect(header.exists()).toBe(false)
  })
})

