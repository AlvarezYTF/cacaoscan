import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import SummaryCard from '../SummaryCard.vue'

vi.mock('@/components/common/BaseStatsCard.vue', () => ({
  default: {
    name: 'BaseStatsCard',
    template: '<div class="base-stats-card"></div>',
    props: ['label', 'value', 'icon', 'color', 'trend', 'trendLabel']
  }
}))

describe('SummaryCard', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
  })

  describe('Rendering', () => {
    it('should render summary card', () => {
      wrapper = mount(SummaryCard, {
        props: {
          title: 'Test Title',
          value: 100
        }
      })

      const card = wrapper.findComponent({ name: 'BaseStatsCard' })
      expect(card.exists()).toBe(true)
    })

    it('should pass title as label to BaseStatsCard', () => {
      wrapper = mount(SummaryCard, {
        props: {
          title: 'Test Title',
          value: 100
        }
      })

      const card = wrapper.findComponent({ name: 'BaseStatsCard' })
      expect(card.props('label')).toBe('Test Title')
    })

    it('should pass value to BaseStatsCard', () => {
      wrapper = mount(SummaryCard, {
        props: {
          title: 'Test Title',
          value: 100
        }
      })

      const card = wrapper.findComponent({ name: 'BaseStatsCard' })
      expect(card.props('value')).toBe(100)
    })
  })

  describe('Props', () => {
    it('should use default icon when not provided', () => {
      wrapper = mount(SummaryCard, {
        props: {
          title: 'Test Title',
          value: 100
        }
      })

      const card = wrapper.findComponent({ name: 'BaseStatsCard' })
      expect(card.props('icon')).toBe('📊')
    })

    it('should use custom icon when provided', () => {
      wrapper = mount(SummaryCard, {
        props: {
          title: 'Test Title',
          value: 100,
          icon: 'custom-icon'
        }
      })

      const card = wrapper.findComponent({ name: 'BaseStatsCard' })
      expect(card.props('icon')).toBe('custom-icon')
    })

    it('should use default color when not provided', () => {
      wrapper = mount(SummaryCard, {
        props: {
          title: 'Test Title',
          value: 100
        }
      })

      const card = wrapper.findComponent({ name: 'BaseStatsCard' })
      expect(card.props('color')).toBe('blue')
    })

    it('should use custom color when provided', () => {
      wrapper = mount(SummaryCard, {
        props: {
          title: 'Test Title',
          value: 100,
          color: 'green'
        }
      })

      const card = wrapper.findComponent({ name: 'BaseStatsCard' })
      expect(card.props('color')).toBe('green')
    })

    it('should pass empty string color as default', () => {
      wrapper = mount(SummaryCard, {
        props: {
          title: 'Test Title',
          value: 100,
          color: ''
        }
      })

      const card = wrapper.findComponent({ name: 'BaseStatsCard' })
      expect(card.props('color')).toBe('blue')
    })
  })

  describe('Trend/Percentage', () => {
    it('should pass trend when percentage is provided', () => {
      wrapper = mount(SummaryCard, {
        props: {
          title: 'Test Title',
          value: 100,
          percentage: 5
        }
      })

      const card = wrapper.findComponent({ name: 'BaseStatsCard' })
      expect(card.props('trend')).toBe(5)
    })

    it('should not pass trend when percentage is null', () => {
      wrapper = mount(SummaryCard, {
        props: {
          title: 'Test Title',
          value: 100,
          percentage: null
        }
      })

      const card = wrapper.findComponent({ name: 'BaseStatsCard' })
      expect(card.props('trend')).toBeNull()
    })

    it('should not pass trend when percentage is undefined', () => {
      wrapper = mount(SummaryCard, {
        props: {
          title: 'Test Title',
          value: 100,
          percentage: undefined
        }
      })

      const card = wrapper.findComponent({ name: 'BaseStatsCard' })
      expect(card.props('trend')).toBeNull()
    })

    it('should pass trend label', () => {
      wrapper = mount(SummaryCard, {
        props: {
          title: 'Test Title',
          value: 100,
          percentage: 5
        }
      })

      const card = wrapper.findComponent({ name: 'BaseStatsCard' })
      expect(card.props('trendLabel')).toBe('desde el mes pasado')
    })

    it('should handle negative percentage', () => {
      wrapper = mount(SummaryCard, {
        props: {
          title: 'Test Title',
          value: 100,
          percentage: -5
        }
      })

      const card = wrapper.findComponent({ name: 'BaseStatsCard' })
      expect(card.props('trend')).toBe(-5)
    })
  })

  describe('Value Types', () => {
    it('should handle string values', () => {
      wrapper = mount(SummaryCard, {
        props: {
          title: 'Test Title',
          value: '100'
        }
      })

      const card = wrapper.findComponent({ name: 'BaseStatsCard' })
      expect(card.props('value')).toBe('100')
    })

    it('should handle number values', () => {
      wrapper = mount(SummaryCard, {
        props: {
          title: 'Test Title',
          value: 100
        }
      })

      const card = wrapper.findComponent({ name: 'BaseStatsCard' })
      expect(card.props('value')).toBe(100)
    })
  })
})




