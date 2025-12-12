import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseSectionCard from './BaseSectionCard.vue'

describe('BaseSectionCard', () => {
  it('should render section card', () => {
    const wrapper = mount(BaseSectionCard, {
      props: {
        title: 'Test Title'
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text().includes('Test Title')).toBe(true)
  })

  it('should display title when provided', () => {
    const wrapper = mount(BaseSectionCard, {
      props: {
        title: 'Test Title'
      }
    })

    expect(wrapper.text().includes('Test Title')).toBe(true)
  })

  it('should display description when provided', () => {
    const wrapper = mount(BaseSectionCard, {
      props: {
        title: 'Test Title',
        description: 'Test Description'
      }
    })

    expect(wrapper.text().includes('Test Description')).toBe(true)
  })

  it('should render header slot', () => {
    const wrapper = mount(BaseSectionCard, {
      props: {
        title: 'Test Title'
      },
      slots: {
        header: '<div>Custom Header</div>'
      }
    })

    expect(wrapper.text().includes('Custom Header')).toBe(true)
    expect(wrapper.text().includes('Test Title')).toBe(false)
  })

  it('should render default slot', () => {
    const wrapper = mount(BaseSectionCard, {
      props: {
        title: 'Test Title'
      },
      slots: {
        default: '<div>Card Content</div>'
      }
    })

    expect(wrapper.text().includes('Card Content')).toBe(true)
  })

  it('should render icon slot', () => {
    const wrapper = mount(BaseSectionCard, {
      props: {
        title: 'Test Title'
      },
      slots: {
        icon: '<div>Custom Icon</div>'
      }
    })

    expect(wrapper.text().includes('Custom Icon')).toBe(true)
  })

  it('should render headerActions slot', () => {
    const wrapper = mount(BaseSectionCard, {
      props: {
        title: 'Test Title'
      },
      slots: {
        headerActions: '<button>Action</button>'
      }
    })

    expect(wrapper.text().includes('Action')).toBe(true)
  })

  it('should apply custom container class', () => {
    const wrapper = mount(BaseSectionCard, {
      props: {
        title: 'Test Title',
        containerClass: 'custom-class'
      }
    })

    expect(wrapper.classes()).toContain('custom-class')
  })

  it('should display default icon when no icon or icon slot provided', () => {
    const wrapper = mount(BaseSectionCard, {
      props: {
        title: 'Test Title'
      }
    })

    const iconContainer = wrapper.find('.bg-green-100')
    expect(iconContainer.exists()).toBe(true)
  })
})

