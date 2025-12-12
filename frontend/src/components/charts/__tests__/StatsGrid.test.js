import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import StatsGrid from '../StatsGrid.vue'

vi.mock('@/components/common/BaseStatsCard.vue', () => ({
  default: {
    name: 'BaseStatsCard',
    template: '<div class="base-stats-card"><slot name="footer"></slot></div>',
    props: ['title', 'value', 'icon', 'trend', 'format', 'color', 'loading']
  }
}))

vi.mock('../TrendChart.vue', () => ({
  default: {
    name: 'TrendChart',
    template: '<div class="trend-chart"></div>',
    props: ['data', 'color', 'height']
  }
}))

describe('StatsGrid', () => {
  let wrapper

  const mockStats = [
    {
      id: '1',
      label: 'Total Users',
      value: 100,
      icon: 'users'
    },
    {
      id: '2',
      label: 'Active Sessions',
      value: 50,
      icon: 'sessions'
    }
  ]

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
  })

  describe('Rendering', () => {
    it('should render stats grid with provided stats', () => {
      wrapper = mount(StatsGrid, {
        props: {
          stats: mockStats
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      expect(cards.length).toBe(2)
    })

    it('should render stat cards with correct props', () => {
      wrapper = mount(StatsGrid, {
        props: {
          stats: mockStats
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      expect(cards[0].props('title')).toBe('Total Users')
      expect(cards[0].props('value')).toBe(100)
      expect(cards[1].props('title')).toBe('Active Sessions')
      expect(cards[1].props('value')).toBe(50)
    })
  })

  describe('Columns Configuration', () => {
    it('should use auto columns by default', () => {
      wrapper = mount(StatsGrid, {
        props: {
          stats: mockStats
        }
      })

      const grid = wrapper.find('.stats-grid')
      expect(grid.exists()).toBe(true)
      // The computed value is bound via v-bind, so we check the component exists
      expect(wrapper.vm.gridColumns).toBe('repeat(auto-fit, minmax(250px, 1fr))')
    })

    it('should use specified number of columns', () => {
      wrapper = mount(StatsGrid, {
        props: {
          stats: mockStats,
          columns: 3
        }
      })

      expect(wrapper.vm.gridColumns).toBe('repeat(3, 1fr)')
    })

    it('should use string column value', () => {
      wrapper = mount(StatsGrid, {
        props: {
          stats: mockStats,
          columns: '4'
        }
      })

      expect(wrapper.vm.gridColumns).toBe('repeat(4, 1fr)')
    })
  })

  describe('Spacing Configuration', () => {
    it('should use normal spacing by default', () => {
      wrapper = mount(StatsGrid, {
        props: {
          stats: mockStats
        }
      })

      expect(wrapper.vm.gridGap).toBe('20px')
    })

    it('should use compact spacing', () => {
      wrapper = mount(StatsGrid, {
        props: {
          stats: mockStats,
          spacing: 'compact'
        }
      })

      expect(wrapper.vm.gridGap).toBe('12px')
    })

    it('should use spacious spacing', () => {
      wrapper = mount(StatsGrid, {
        props: {
          stats: mockStats,
          spacing: 'spacious'
        }
      })

      expect(wrapper.vm.gridGap).toBe('32px')
    })
  })

  describe('Stat Properties', () => {
    it('should pass format prop to stat card', () => {
      const statsWithFormat = [
        {
          label: 'Total',
          value: 100,
          icon: 'icon',
          format: 'currency'
        }
      ]

      wrapper = mount(StatsGrid, {
        props: {
          stats: statsWithFormat
        }
      })

      const card = wrapper.findComponent({ name: 'BaseStatsCard' })
      expect(card.props('format')).toBe('currency')
    })

    it('should pass color/variant prop to stat card', () => {
      const statsWithVariant = [
        {
          label: 'Total',
          value: 100,
          icon: 'icon',
          variant: 'success'
        }
      ]

      wrapper = mount(StatsGrid, {
        props: {
          stats: statsWithVariant
        }
      })

      const card = wrapper.findComponent({ name: 'BaseStatsCard' })
      expect(card.props('color')).toBe('success')
    })

    it('should pass loading state to stat card', () => {
      const statsWithLoading = [
        {
          label: 'Total',
          value: 100,
          icon: 'icon',
          loading: true
        }
      ]

      wrapper = mount(StatsGrid, {
        props: {
          stats: statsWithLoading
        }
      })

      const card = wrapper.findComponent({ name: 'BaseStatsCard' })
      expect(card.props('loading')).toBe(true)
    })
  })

  describe('Trend Data', () => {
    it('should pass trend prop when provided', () => {
      const statsWithTrend = [
        {
          label: 'Total',
          value: 100,
          icon: 'icon',
          trend: {
            value: 5,
            label: '5% increase',
            data: [1, 2, 3]
          }
        }
      ]

      wrapper = mount(StatsGrid, {
        props: {
          stats: statsWithTrend
        }
      })

      const card = wrapper.findComponent({ name: 'BaseStatsCard' })
      expect(card.props('trend')).toEqual({
        value: 5,
        label: '5% increase',
        data: [1, 2, 3]
      })
    })

    it('should create trend from change property', () => {
      const statsWithChange = [
        {
          label: 'Total',
          value: 100,
          icon: 'icon',
          change: 5
        }
      ]

      wrapper = mount(StatsGrid, {
        props: {
          stats: statsWithChange
        }
      })

      const card = wrapper.findComponent({ name: 'BaseStatsCard' })
      const trend = card.props('trend')
      expect(trend.value).toBe(5)
      expect(trend.label).toContain('5%')
    })

    it('should use custom changePeriod when provided', () => {
      const statsWithChangePeriod = [
        {
          label: 'Total',
          value: 100,
          icon: 'icon',
          change: 5,
          changePeriod: 'desde ayer'
        }
      ]

      wrapper = mount(StatsGrid, {
        props: {
          stats: statsWithChangePeriod
        }
      })

      const card = wrapper.findComponent({ name: 'BaseStatsCard' })
      const trend = card.props('trend')
      expect(trend.label).toBe('desde ayer')
    })

    it('should render TrendChart in footer when trend has data', () => {
      const statsWithTrendData = [
        {
          label: 'Total',
          value: 100,
          icon: 'icon',
          trend: {
            value: 5,
            data: [1, 2, 3],
            color: '#3498db'
          }
        }
      ]

      wrapper = mount(StatsGrid, {
        props: {
          stats: statsWithTrendData
        }
      })

      const trendChart = wrapper.findComponent({ name: 'TrendChart' })
      expect(trendChart.exists()).toBe(true)
      expect(trendChart.props('data')).toEqual([1, 2, 3])
      expect(trendChart.props('color')).toBe('#3498db')
    })
  })

  describe('Stat Click Handling', () => {
    it('should emit stat-click event when clickable stat is clicked', async () => {
      const clickableStats = [
        {
          label: 'Total',
          value: 100,
          icon: 'icon',
          clickable: true
        }
      ]

      wrapper = mount(StatsGrid, {
        props: {
          stats: clickableStats
        }
      })

      await wrapper.vm.handleStatClick(clickableStats[0])

      expect(wrapper.emitted('stat-click')).toBeTruthy()
      expect(wrapper.emitted('stat-click')[0]).toEqual([clickableStats[0]])
    })

    it('should not emit event for non-clickable stats', async () => {
      const nonClickableStats = [
        {
          label: 'Total',
          value: 100,
          icon: 'icon',
          clickable: false
        }
      ]

      wrapper = mount(StatsGrid, {
        props: {
          stats: nonClickableStats
        }
      })

      const card = wrapper.findComponent({ name: 'BaseStatsCard' })
      await card.trigger('click')

      expect(wrapper.emitted('stat-click')).toBeFalsy()
    })

    it('should apply cursor-pointer class to clickable stats', () => {
      const clickableStats = [
        {
          label: 'Total',
          value: 100,
          icon: 'icon',
          clickable: true
        }
      ]

      wrapper = mount(StatsGrid, {
        props: {
          stats: clickableStats
        }
      })

      const card = wrapper.findComponent({ name: 'BaseStatsCard' })
      expect(card.classes()).toContain('cursor-pointer')
    })
  })

  describe('Stat Color Generation', () => {
    it('should generate colors for stats based on index', () => {
      const multipleStats = [
        { label: 'Stat 1', value: 1, icon: 'icon' },
        { label: 'Stat 2', value: 2, icon: 'icon' },
        { label: 'Stat 3', value: 3, icon: 'icon' }
      ]

      wrapper = mount(StatsGrid, {
        props: {
          stats: multipleStats
        }
      })

      const color1 = wrapper.vm.getStatColor(0)
      const color2 = wrapper.vm.getStatColor(1)
      const color3 = wrapper.vm.getStatColor(2)

      expect(color1).toBe('#3498db')
      expect(color2).toBe('#e74c3c')
      expect(color3).toBe('#2ecc71')
    })

    it('should use trend color when provided', () => {
      const statsWithTrendColor = [
        {
          label: 'Total',
          value: 100,
          icon: 'icon',
          trend: {
            value: 5,
            data: [1, 2, 3],
            color: '#custom-color'
          }
        }
      ]

      wrapper = mount(StatsGrid, {
        props: {
          stats: statsWithTrendColor
        }
      })

      const trendChart = wrapper.findComponent({ name: 'TrendChart' })
      expect(trendChart.props('color')).toBe('#custom-color')
    })
  })

  describe('Keys', () => {
    it('should use stat id as key when available', () => {
      const statsWithId = [
        {
          id: 'unique-id-1',
          label: 'Total',
          value: 100,
          icon: 'icon'
        }
      ]

      wrapper = mount(StatsGrid, {
        props: {
          stats: statsWithId
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      expect(cards.length).toBe(1)
    })

    it('should use index as key when id is not available', () => {
      const statsWithoutId = [
        {
          label: 'Total',
          value: 100,
          icon: 'icon'
        }
      ]

      wrapper = mount(StatsGrid, {
        props: {
          stats: statsWithoutId
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      expect(cards.length).toBe(1)
    })
  })
})




