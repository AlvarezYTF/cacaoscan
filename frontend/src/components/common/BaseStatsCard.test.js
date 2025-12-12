import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseStatsCard from './BaseStatsCard.vue'

describe('BaseStatsCard', () => {
  it('should render stats card', () => {
    const wrapper = mount(BaseStatsCard, {
      props: {
        label: 'Test Label',
        value: '100'
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text().includes('Test Label')).toBe(true)
    expect(wrapper.text().includes('100')).toBe(true)
  })

  it('should display icon when provided', () => {
    const wrapper = mount(BaseStatsCard, {
      props: {
        label: 'Test Label',
        value: '100',
        icon: '👥'
      }
    })

    expect(wrapper.text().includes('👥')).toBe(true)
  })

  it('should apply correct color class', () => {
    const wrapper = mount(BaseStatsCard, {
      props: {
        label: 'Test Label',
        value: '100',
        color: 'green',
        icon: '📊'
      }
    })

    const iconContainer = wrapper.find('.bg-green-100')
    expect(iconContainer.exists()).toBe(true)
    expect(iconContainer.classes()).toContain('text-green-600')
  })

  it('should show trend indicator when trend is positive', () => {
    const wrapper = mount(BaseStatsCard, {
      props: {
        label: 'Test Label',
        value: '100',
        trend: 5
      }
    })

    const trendIndicator = wrapper.find('svg')
    expect(trendIndicator.exists()).toBe(true)
  })

  it('should show trend indicator when trend is negative', () => {
    const wrapper = mount(BaseStatsCard, {
      props: {
        label: 'Test Label',
        value: '100',
        trend: -5
      }
    })

    const trendIndicator = wrapper.find('svg')
    expect(trendIndicator.exists()).toBe(true)
  })

  it('should display trend value when provided', () => {
    const wrapper = mount(BaseStatsCard, {
      props: {
        label: 'Test Label',
        value: '100',
        trend: 5
      }
    })

    expect(wrapper.text().includes('5%')).toBe(true)
  })

  it('should not display trend when not provided', () => {
    const wrapper = mount(BaseStatsCard, {
      props: {
        label: 'Test Label',
        value: '100'
      }
    })

    const trendIndicator = wrapper.find('.text-green-600')
    expect(trendIndicator.exists()).toBe(false)
  })
})

