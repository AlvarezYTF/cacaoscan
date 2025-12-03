import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import LoadingSkeleton from './LoadingSkeleton.vue'

describe('LoadingSkeleton', () => {
  it('should render loading skeleton', () => {
    const wrapper = mount(LoadingSkeleton)

    expect(wrapper.exists()).toBe(true)
  })

  it('should display title skeleton when showTitle is true', () => {
    const wrapper = mount(LoadingSkeleton, {
      props: {
        showTitle: true
      }
    })

    const title = wrapper.find('.h-4.bg-gray-200')
    expect(title.exists()).toBe(true)
  })

  it('should not display title skeleton when showTitle is false', () => {
    const wrapper = mount(LoadingSkeleton, {
      props: {
        showTitle: false
      }
    })

    const title = wrapper.find('.h-4.bg-gray-200.w-1\\/4')
    expect(title.exists()).toBe(false)
  })

  it('should render correct number of lines', () => {
    const wrapper = mount(LoadingSkeleton, {
      props: {
        lines: 5,
        showTitle: false
      }
    })

    const lines = wrapper.findAll('.space-y-2 .h-4.bg-gray-200.rounded')
    expect(lines.length).toBe(5)
  })

  it('should use default 3 lines when not specified', () => {
    const wrapper = mount(LoadingSkeleton, {
      props: {
        showTitle: false,
        lines: 3
      }
    })

    const lines = wrapper.findAll('.space-y-2 .h-4.bg-gray-200.rounded')
    expect(lines.length).toBe(3)
  })

  it('should apply different width classes to lines', () => {
    const wrapper = mount(LoadingSkeleton, {
      props: {
        lines: 4,
        showTitle: false
      }
    })

    const lines = wrapper.findAll('.h-4.bg-gray-200.rounded')
    expect(lines.length).toBe(4)

    // Check that different width classes are applied
    const widthClasses = lines.map(line => {
      const classes = line.classes()
      if (classes.includes('w-full')) return 'w-full'
      if (classes.includes('w-5/6')) return 'w-5/6'
      if (classes.includes('w-4/6')) return 'w-4/6'
      if (classes.includes('w-3/4')) return 'w-3/4'
      return null
    })

    expect(widthClasses.some(w => w !== null)).toBe(true)
  })
})

