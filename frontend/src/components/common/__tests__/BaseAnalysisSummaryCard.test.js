/**
 * Unit tests for BaseAnalysisSummaryCard component
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseAnalysisSummaryCard from '../BaseAnalysisSummaryCard.vue'

vi.mock('../BaseStatsCard.vue', () => ({
  default: {
    name: 'BaseStatsCard',
    template: `
      <div class="base-stats-card">
        <div class="card-title">{{ title }}</div>
        <slot name="value">
          <div class="card-value">{{ value }}</div>
        </slot>
        <slot name="footer"></slot>
      </div>
    `,
    props: {
      title: String,
      value: [String, Number],
      icon: [String, Object],
      trend: Object,
      color: String,
      format: String,
      loading: Boolean
    }
  }
}))

describe('BaseAnalysisSummaryCard', () => {
  let wrapper

  const createSummaryData = () => ({
    total: 100,
    avgWeight: 25.5,
    avgDimensions: {
      width: 10,
      height: 15,
      thickness: 5
    },
    qualityDistribution: {
      excellent: 30,
      good: 50,
      fair: 15,
      poor: 5
    }
  })

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Props validation', () => {
    it('should accept summary prop', () => {
      const summary = createSummaryData()
      wrapper = mount(BaseAnalysisSummaryCard, {
        props: {
          summary
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should require summary prop', () => {
      expect(() => {
        wrapper = mount(BaseAnalysisSummaryCard)
      }).toThrow()
    })

    it('should accept title prop', () => {
      const summary = createSummaryData()
      wrapper = mount(BaseAnalysisSummaryCard, {
        props: {
          summary,
          title: 'Custom Title'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should accept format prop', () => {
      const summary = createSummaryData()
      wrapper = mount(BaseAnalysisSummaryCard, {
        props: {
          summary,
          format: 'average'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Rendering', () => {
    it('should render with default title', () => {
      const summary = createSummaryData()
      wrapper = mount(BaseAnalysisSummaryCard, {
        props: {
          summary
        }
      })

      expect(wrapper.text()).toContain('Resumen de Análisis')
    })

    it('should render custom title when provided', () => {
      const summary = createSummaryData()
      wrapper = mount(BaseAnalysisSummaryCard, {
        props: {
          summary,
          title: 'Custom Title'
        }
      })

      expect(wrapper.text()).toContain('Custom Title')
    })

    it('should display total when format is total', () => {
      const summary = createSummaryData()
      wrapper = mount(BaseAnalysisSummaryCard, {
        props: {
          summary,
          format: 'total'
        }
      })

      expect(wrapper.text()).toContain('100')
    })

    it('should display average weight when format is average', () => {
      const summary = createSummaryData()
      wrapper = mount(BaseAnalysisSummaryCard, {
        props: {
          summary,
          format: 'average'
        }
      })

      expect(wrapper.text()).toContain('25.5g')
    })

    it('should display average weight when format is weight', () => {
      const summary = createSummaryData()
      wrapper = mount(BaseAnalysisSummaryCard, {
        props: {
          summary,
          format: 'weight'
        }
      })

      expect(wrapper.text()).toContain('25.5g')
    })

    it('should show details when showDetails is true', () => {
      const summary = createSummaryData()
      wrapper = mount(BaseAnalysisSummaryCard, {
        props: {
          summary,
          showDetails: true
        }
      })

      expect(wrapper.text()).toContain('Peso promedio')
      expect(wrapper.text()).toContain('Dimensiones')
    })

    it('should not show details when showDetails is false', () => {
      const summary = createSummaryData()
      wrapper = mount(BaseAnalysisSummaryCard, {
        props: {
          summary,
          showDetails: false
        }
      })

      expect(wrapper.text()).not.toContain('Peso promedio')
    })

    it('should display quality distribution', () => {
      const summary = createSummaryData()
      wrapper = mount(BaseAnalysisSummaryCard, {
        props: {
          summary
        }
      })

      expect(wrapper.text()).toContain('excellent: 30')
      expect(wrapper.text()).toContain('good: 50')
    })
  })

  describe('Computed properties', () => {
    it('should format summary as total by default', () => {
      const summary = createSummaryData()
      wrapper = mount(BaseAnalysisSummaryCard, {
        props: {
          summary
        }
      })

      expect(wrapper.vm.formattedSummary).toBe(100)
    })

    it('should format summary as average weight', () => {
      const summary = createSummaryData()
      wrapper = mount(BaseAnalysisSummaryCard, {
        props: {
          summary,
          format: 'average'
        }
      })

      expect(wrapper.vm.formattedSummary).toBe('25.5g')
    })

    it('should return 0g when avgWeight is missing', () => {
      const summary = { total: 100 }
      wrapper = mount(BaseAnalysisSummaryCard, {
        props: {
          summary,
          format: 'average'
        }
      })

      expect(wrapper.vm.formattedSummary).toBe('0g')
    })
  })

  describe('Methods', () => {
    it('should return correct quality color for excellent', () => {
      const summary = createSummaryData()
      wrapper = mount(BaseAnalysisSummaryCard, {
        props: {
          summary
        }
      })

      const color = wrapper.vm.getQualityColor('excellent')
      expect(color).toContain('green')
    })

    it('should return correct quality color for good', () => {
      const summary = createSummaryData()
      wrapper = mount(BaseAnalysisSummaryCard, {
        props: {
          summary
        }
      })

      const color = wrapper.vm.getQualityColor('good')
      expect(color).toContain('blue')
    })

    it('should return correct quality color for fair', () => {
      const summary = createSummaryData()
      wrapper = mount(BaseAnalysisSummaryCard, {
        props: {
          summary
        }
      })

      const color = wrapper.vm.getQualityColor('fair')
      expect(color).toContain('yellow')
    })

    it('should return correct quality color for poor', () => {
      const summary = createSummaryData()
      wrapper = mount(BaseAnalysisSummaryCard, {
        props: {
          summary
        }
      })

      const color = wrapper.vm.getQualityColor('poor')
      expect(color).toContain('red')
    })

    it('should return default color for unknown quality', () => {
      const summary = createSummaryData()
      wrapper = mount(BaseAnalysisSummaryCard, {
        props: {
          summary
        }
      })

      const color = wrapper.vm.getQualityColor('unknown')
      expect(color).toContain('gray')
    })
  })

  describe('Edge cases', () => {
    it('should handle missing qualityDistribution', () => {
      const summary = { total: 100 }
      wrapper = mount(BaseAnalysisSummaryCard, {
        props: {
          summary
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should handle empty qualityDistribution', () => {
      const summary = { total: 100, qualityDistribution: {} }
      wrapper = mount(BaseAnalysisSummaryCard, {
        props: {
          summary
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should handle missing avgDimensions', () => {
      const summary = { total: 100, avgWeight: 25.5 }
      wrapper = mount(BaseAnalysisSummaryCard, {
        props: {
          summary,
          showDetails: true
        }
      })

      expect(wrapper.exists()).toBe(true)
    })
  })
})

