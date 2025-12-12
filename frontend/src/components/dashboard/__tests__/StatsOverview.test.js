import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import StatsOverview from '../StatsOverview.vue'

vi.mock('@/components/common/BaseStatsCard.vue', () => ({
  default: {
    name: 'BaseStatsCard',
    template: '<div class="base-stats-card"></div>',
    props: ['title', 'value', 'icon', 'trend', 'format', 'color']
  }
}))

vi.mock('@/utils/formatters', () => ({
  parseChange: vi.fn((change) => {
    if (!change || typeof change !== 'string') return 0
    const trimmed = change.trim()
    const regex = /^([+-]?)(\d+\.?\d*)/
    const match = regex.exec(trimmed)
    if (!match) return 0
    const sign = match[1] === '-' ? -1 : 1
    const value = Number.parseFloat(match[2])
    return Number.isNaN(value) ? 0 : sign * value
  })
}))

describe('StatsOverview', () => {
  let wrapper

  const defaultStats = {
    totalBatches: 24,
    batchesChange: '+5%',
    avgQuality: 87,
    qualityChange: '+2%',
    defectRate: 5.2,
    defectChange: '-1.2%'
  }

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
  })

  describe('Rendering', () => {
    it('should render stats overview section', () => {
      wrapper = mount(StatsOverview, {
        props: {
          stats: defaultStats
        }
      })

      expect(wrapper.find('.stats-overview').exists()).toBe(true)
    })

    it('should render three stat cards', () => {
      wrapper = mount(StatsOverview, {
        props: {
          stats: defaultStats
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      expect(cards.length).toBe(3)
    })
  })

  describe('Total Batches Card', () => {
    it('should render total batches card with correct props', () => {
      wrapper = mount(StatsOverview, {
        props: {
          stats: defaultStats
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      const batchesCard = cards[0]
      
      expect(batchesCard.props('title')).toBe('Total de lotes')
      expect(batchesCard.props('value')).toBe(24)
      expect(batchesCard.props('icon')).toBe('fas fa-seedling')
      expect(batchesCard.props('color')).toBe('success')
    })

    it('should show zero when totalBatches is not provided', () => {
      wrapper = mount(StatsOverview, {
        props: {
          stats: {}
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      expect(cards[0].props('value')).toBe(0)
    })

    it('should render trend when batchesChange is provided', () => {
      wrapper = mount(StatsOverview, {
        props: {
          stats: defaultStats
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      const trend = cards[0].props('trend')
      
      expect(trend).toBeTruthy()
      expect(trend.label).toContain('+5%')
      expect(trend.value).toBe(5)
    })

    it('should not render trend when batchesChange is not provided', () => {
      wrapper = mount(StatsOverview, {
        props: {
          stats: {
            totalBatches: 24
          }
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      expect(cards[0].props('trend')).toBeNull()
    })
  })

  describe('Average Quality Card', () => {
    it('should render average quality card with correct props', () => {
      wrapper = mount(StatsOverview, {
        props: {
          stats: defaultStats
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      const qualityCard = cards[1]
      
      expect(qualityCard.props('title')).toBe('Calidad promedio')
      expect(qualityCard.props('value')).toBe(87)
      expect(qualityCard.props('icon')).toBe('fas fa-star')
      expect(qualityCard.props('format')).toBe('percentage')
      expect(qualityCard.props('color')).toBe('warning')
    })

    it('should show zero when avgQuality is not provided', () => {
      wrapper = mount(StatsOverview, {
        props: {
          stats: {}
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      expect(cards[1].props('value')).toBe(0)
    })

    it('should render trend when qualityChange is provided', () => {
      wrapper = mount(StatsOverview, {
        props: {
          stats: defaultStats
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      const trend = cards[1].props('trend')
      
      expect(trend).toBeTruthy()
      expect(trend.label).toContain('+2%')
      expect(trend.value).toBe(2)
    })
  })

  describe('Defect Rate Card', () => {
    it('should render defect rate card with correct props', () => {
      wrapper = mount(StatsOverview, {
        props: {
          stats: defaultStats
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      const defectCard = cards[2]
      
      expect(defectCard.props('title')).toBe('Defectos')
      expect(defectCard.props('value')).toBe(5.2)
      expect(defectCard.props('icon')).toBe('fas fa-exclamation-triangle')
      expect(defectCard.props('format')).toBe('percentage')
      expect(defectCard.props('color')).toBe('danger')
    })

    it('should show zero when defectRate is not provided', () => {
      wrapper = mount(StatsOverview, {
        props: {
          stats: {}
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      expect(cards[2].props('value')).toBe(0)
    })

    it('should render trend when defectChange is provided', () => {
      wrapper = mount(StatsOverview, {
        props: {
          stats: defaultStats
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      const trend = cards[2].props('trend')
      
      expect(trend).toBeTruthy()
      expect(trend.label).toContain('-1.2%')
      expect(trend.value).toBe(-1.2)
    })
  })

  describe('Change Values', () => {
    it('should handle positive changes', () => {
      wrapper = mount(StatsOverview, {
        props: {
          stats: {
            totalBatches: 10,
            batchesChange: '+10%'
          }
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      const trend = cards[0].props('trend')
      
      expect(trend.value).toBe(10)
      expect(trend.label).toContain('+10%')
    })

    it('should handle negative changes', () => {
      wrapper = mount(StatsOverview, {
        props: {
          stats: {
            totalBatches: 10,
            batchesChange: '-5%'
          }
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      const trend = cards[0].props('trend')
      
      expect(trend.value).toBe(-5)
      expect(trend.label).toContain('-5%')
    })

    it('should handle decimal changes', () => {
      wrapper = mount(StatsOverview, {
        props: {
          stats: {
            avgQuality: 85,
            qualityChange: '+2.5%'
          }
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      const trend = cards[1].props('trend')
      
      expect(trend.value).toBe(2.5)
    })
  })
})




