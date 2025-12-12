import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import PieChart from '../PieChart.vue'

vi.mock('@/components/common/BaseChart.vue', () => ({
  default: {
    name: 'BaseChart',
    template: '<div class="base-chart"><h3 v-if="title">{{ title }}</h3><canvas></canvas></div>',
    props: ['data', 'options', 'type', 'title', 'height', 'containerClass']
  }
}))

describe('PieChart', () => {
  let wrapper

  const defaultChartData = {
    labels: ['Red', 'Blue', 'Yellow'],
    datasets: [{
      data: [300, 50, 100],
      backgroundColor: [
        'rgb(255, 99, 132)',
        'rgb(54, 162, 235)',
        'rgb(255, 205, 86)'
      ]
    }]
  }

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = mount(PieChart, {
        props: {
          chartData: defaultChartData
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should render BaseChart component', () => {
      wrapper = mount(PieChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.exists()).toBe(true)
    })

    it('should pass type as pie to BaseChart', () => {
      wrapper = mount(PieChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('type')).toBe('pie')
    })
  })

  describe('Props', () => {
    it('should pass chartData to BaseChart', () => {
      wrapper = mount(PieChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('data')).toEqual(defaultChartData)
    })

    it('should pass title to BaseChart when provided', () => {
      wrapper = mount(PieChart, {
        props: {
          chartData: defaultChartData,
          title: 'Pie Chart Title'
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('title')).toBe('Pie Chart Title')
    })

    it('should pass empty title to BaseChart when not provided', () => {
      wrapper = mount(PieChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('title')).toBe('')
    })

    it('should pass default height to BaseChart', () => {
      wrapper = mount(PieChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('height')).toBe(400)
    })

    it('should pass custom height as string to BaseChart', () => {
      wrapper = mount(PieChart, {
        props: {
          chartData: defaultChartData,
          height: '500px'
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('height')).toBe('500px')
    })

    it('should pass custom height as number to BaseChart', () => {
      wrapper = mount(PieChart, {
        props: {
          chartData: defaultChartData,
          height: 600
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('height')).toBe(600)
    })

    it('should pass default containerClass to BaseChart', () => {
      wrapper = mount(PieChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('containerClass')).toContain('bg-white')
      expect(baseChart.props('containerClass')).toContain('p-6')
    })

    it('should pass custom containerClass to BaseChart', () => {
      wrapper = mount(PieChart, {
        props: {
          chartData: defaultChartData,
          containerClass: 'custom-class'
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('containerClass')).toBe('custom-class')
    })
  })

  describe('Chart Options', () => {
    it('should merge default pie options with custom options', () => {
      const customOptions = {
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      }

      wrapper = mount(PieChart, {
        props: {
          chartData: defaultChartData,
          options: customOptions
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const mergedOptions = baseChart.props('options')
      
      expect(mergedOptions.responsive).toBe(true)
      expect(mergedOptions.maintainAspectRatio).toBe(false)
      expect(mergedOptions.plugins.legend.position).toBe('bottom')
    })

    it('should have default legend position on right', () => {
      wrapper = mount(PieChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const options = baseChart.props('options')
      
      expect(options.plugins.legend.position).toBe('right')
    })

    it('should have tooltip callback for percentage calculation', () => {
      wrapper = mount(PieChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const options = baseChart.props('options')
      
      expect(options.plugins.tooltip.callbacks).toBeDefined()
      expect(typeof options.plugins.tooltip.callbacks.label).toBe('function')
    })

    it('should calculate percentage correctly in tooltip callback', () => {
      wrapper = mount(PieChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const options = baseChart.props('options')
      
      const mockContext = {
        label: 'Red',
        raw: 300,
        dataset: {
          data: [300, 50, 100]
        }
      }

      const result = options.plugins.tooltip.callbacks.label(mockContext)
      
      expect(result).toContain('Red')
      expect(result).toContain('300')
      expect(result).toContain('67%') // 300 / 450 * 100 = 66.67% rounded to 67%
    })

    it('should override default options when custom options provided', () => {
      const customOptions = {
        responsive: false,
        maintainAspectRatio: true
      }

      wrapper = mount(PieChart, {
        props: {
          chartData: defaultChartData,
          options: customOptions
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const mergedOptions = baseChart.props('options')
      
      expect(mergedOptions.responsive).toBe(false)
      expect(mergedOptions.maintainAspectRatio).toBe(true)
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty chartData', () => {
      wrapper = mount(PieChart, {
        props: {
          chartData: {
            labels: [],
            datasets: []
          }
        }
      })

      expect(wrapper.exists()).toBe(true)
      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.exists()).toBe(true)
    })

    it('should handle chartData with single value', () => {
      const singleData = {
        labels: ['Only'],
        datasets: [{
          data: [100]
        }]
      }

      wrapper = mount(PieChart, {
        props: {
          chartData: singleData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('data')).toEqual(singleData)
    })

    it('should require chartData prop', () => {
      expect(() => {
        mount(PieChart)
      }).toThrow()
    })
  })
})



