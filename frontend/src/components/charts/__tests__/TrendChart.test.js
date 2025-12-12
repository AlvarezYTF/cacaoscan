import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import TrendChart from '../TrendChart.vue'

// Mock BaseChart component
vi.mock('../BaseChart.vue', () => ({
  default: {
    name: 'BaseChart',
    template: '<div class="base-chart"><slot></slot></div>',
    props: ['chartData', 'options', 'type', 'height', 'showLegend', 'enableResizeObserver']
  }
}))

describe('TrendChart', () => {
  let wrapper

  const mockData = [10, 20, 30, 25, 35, 40]

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should render BaseChart component', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.exists()).toBe(true)
    })

    it('should pass line type to BaseChart', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('type')).toBe('line')
    })
  })

  describe('Props', () => {
    it('should pass data prop correctly', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const chartData = baseChart.props('chartData')
      expect(chartData.datasets[0].data).toEqual(mockData)
    })

    it('should use default color', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const chartData = baseChart.props('chartData')
      expect(chartData.datasets[0].borderColor).toBe('#3498db')
      expect(chartData.datasets[0].backgroundColor).toBe('#3498db')
    })

    it('should use custom color', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData,
          color: '#ff0000'
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const chartData = baseChart.props('chartData')
      expect(chartData.datasets[0].borderColor).toBe('#ff0000')
      expect(chartData.datasets[0].backgroundColor).toBe('#ff0000')
    })

    it('should use default height', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('height')).toBe(40)
    })

    it('should use custom height', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData,
          height: 100
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('height')).toBe(100)
    })

    it('should pass showLegend as false', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('showLegend')).toBe(false)
    })

    it('should pass enableResizeObserver as false', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('enableResizeObserver')).toBe(false)
    })
  })

  describe('Chart Data Configuration', () => {
    it('should generate labels from data indices', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const chartData = baseChart.props('chartData')
      expect(chartData.labels).toEqual([0, 1, 2, 3, 4, 5])
    })

    it('should set borderWidth to 2', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const chartData = baseChart.props('chartData')
      expect(chartData.datasets[0].borderWidth).toBe(2)
    })

    it('should set spanGaps to true', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const chartData = baseChart.props('chartData')
      expect(chartData.datasets[0].spanGaps).toBe(true)
    })
  })

  describe('Show Points', () => {
    it('should hide points by default', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const chartData = baseChart.props('chartData')
      expect(chartData.datasets[0].pointRadius).toBe(0)
      expect(chartData.datasets[0].pointHoverRadius).toBe(0)
    })

    it('should show points when showPoints is true', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData,
          showPoints: true
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const chartData = baseChart.props('chartData')
      expect(chartData.datasets[0].pointRadius).toBe(2)
      expect(chartData.datasets[0].pointHoverRadius).toBe(4)
    })

    it('should set point colors when showPoints is true', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData,
          showPoints: true,
          color: '#ff0000'
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const chartData = baseChart.props('chartData')
      expect(chartData.datasets[0].pointBackgroundColor).toBe('#ff0000')
      expect(chartData.datasets[0].pointBorderColor).toBe('#ff0000')
    })
  })

  describe('Smooth', () => {
    it('should use smooth tension by default', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const chartData = baseChart.props('chartData')
      expect(chartData.datasets[0].tension).toBe(0.4)
    })

    it('should use zero tension when smooth is false', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData,
          smooth: false
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const chartData = baseChart.props('chartData')
      expect(chartData.datasets[0].tension).toBe(0)
    })
  })

  describe('Fill', () => {
    it('should enable fill by default', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const chartData = baseChart.props('chartData')
      expect(chartData.datasets[0].fill).toBe(true)
    })

    it('should disable fill when fill is false', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData,
          fill: false
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const chartData = baseChart.props('chartData')
      expect(chartData.datasets[0].fill).toBe(false)
    })
  })

  describe('Chart Options', () => {
    it('should set responsive to true', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const options = baseChart.props('options')
      expect(options.responsive).toBe(true)
    })

    it('should set maintainAspectRatio to false', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const options = baseChart.props('options')
      expect(options.maintainAspectRatio).toBe(false)
    })

    it('should disable legend', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const options = baseChart.props('options')
      expect(options.plugins.legend.display).toBe(false)
    })

    it('should disable tooltip', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const options = baseChart.props('options')
      expect(options.plugins.tooltip.enabled).toBe(false)
    })

    it('should hide x and y axes', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const options = baseChart.props('options')
      expect(options.scales.x.display).toBe(false)
      expect(options.scales.y.display).toBe(false)
    })

    it('should set intersect to false', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const options = baseChart.props('options')
      expect(options.interaction.intersect).toBe(false)
    })

    it('should set hover colors', () => {
      wrapper = mount(TrendChart, {
        props: {
          data: mockData,
          color: '#ff0000'
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const options = baseChart.props('options')
      expect(options.elements.point.hoverBackgroundColor).toBe('#ff0000')
      expect(options.elements.point.hoverBorderColor).toBe('#ff0000')
    })
  })

  describe('Props Validation', () => {
    it('should require data prop', () => {
      expect(() => {
        wrapper = mount(TrendChart)
      }).toThrow()
    })

    it('should validate data is array', () => {
      expect(() => {
        wrapper = mount(TrendChart, {
          props: {
            data: 'not an array'
          }
        })
      }).toThrow()
    })

    it('should validate data has length > 0', () => {
      expect(() => {
        wrapper = mount(TrendChart, {
          props: {
            data: []
          }
        })
      }).toThrow()
    })
  })
})



