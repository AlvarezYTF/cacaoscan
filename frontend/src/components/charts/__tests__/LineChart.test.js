import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import LineChart from '../LineChart.vue'

// Mock BaseChart component
vi.mock('@/components/common/BaseChart.vue', () => ({
  default: {
    name: 'BaseChart',
    template: `
      <div class="base-chart">
        <h3 v-if="title" class="chart-title">{{ title }}</h3>
        <canvas></canvas>
      </div>
    `,
    props: ['data', 'options', 'type', 'title', 'height', 'containerClass'],
    emits: ['chart-click', 'chart-hover', 'chart-loaded']
  }
}))

describe('LineChart', () => {
  let wrapper

  const defaultChartData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr'],
    datasets: [{
      label: 'Sales',
      data: [10, 20, 30, 40],
      backgroundColor: 'rgba(54, 162, 235, 0.5)',
      borderColor: 'rgba(54, 162, 235, 1)',
      borderWidth: 1
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
      wrapper = mount(LineChart, {
        props: {
          chartData: defaultChartData
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should render BaseChart component', () => {
      wrapper = mount(LineChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.exists()).toBe(true)
    })

    it('should pass type as line to BaseChart', () => {
      wrapper = mount(LineChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('type')).toBe('line')
    })
  })

  describe('Props', () => {
    it('should pass chartData to BaseChart', () => {
      wrapper = mount(LineChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('data')).toEqual(defaultChartData)
    })

    it('should pass default title to BaseChart', () => {
      wrapper = mount(LineChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('title')).toBe('Evolución de análisis por tipo de defecto')
    })

    it('should pass custom title to BaseChart when provided', () => {
      wrapper = mount(LineChart, {
        props: {
          chartData: defaultChartData,
          title: 'Custom Chart Title'
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('title')).toBe('Custom Chart Title')
    })

    it('should merge default options with custom chartOptions', () => {
      const customOptions = {
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      }

      wrapper = mount(LineChart, {
        props: {
          chartData: defaultChartData,
          chartOptions: customOptions
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const mergedOptions = baseChart.props('options')
      
      expect(mergedOptions.responsive).toBe(true)
      expect(mergedOptions.plugins.legend.position).toBe('bottom')
    })
  })

  describe('Default Options', () => {
    it('should apply default responsive option', () => {
      wrapper = mount(LineChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const options = baseChart.props('options')
      
      expect(options.responsive).toBe(true)
    })

    it('should apply default maintainAspectRatio option', () => {
      wrapper = mount(LineChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const options = baseChart.props('options')
      
      expect(options.maintainAspectRatio).toBe(false)
    })

    it('should apply default legend configuration', () => {
      wrapper = mount(LineChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const options = baseChart.props('options')
      
      expect(options.plugins.legend.position).toBe('top')
      expect(options.plugins.legend.labels.usePointStyle).toBe(true)
      expect(options.plugins.legend.labels.boxWidth).toBe(10)
      expect(options.plugins.legend.labels.padding).toBe(20)
    })

    it('should apply default tooltip configuration', () => {
      wrapper = mount(LineChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const options = baseChart.props('options')
      
      expect(options.plugins.tooltip.mode).toBe('index')
      expect(options.plugins.tooltip.intersect).toBe(false)
    })

    it('should apply default x-axis configuration', () => {
      wrapper = mount(LineChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const options = baseChart.props('options')
      
      expect(options.scales.x.grid.display).toBe(false)
    })

    it('should apply default y-axis configuration', () => {
      wrapper = mount(LineChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const options = baseChart.props('options')
      
      expect(options.scales.y.beginAtZero).toBe(true)
      expect(options.scales.y.ticks.stepSize).toBe(2)
    })
  })

  describe('Options Merging', () => {
    it('should override default options with custom options', () => {
      const customOptions = {
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 30
            }
          }
        }
      }

      wrapper = mount(LineChart, {
        props: {
          chartData: defaultChartData,
          chartOptions: customOptions
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const mergedOptions = baseChart.props('options')
      
      expect(mergedOptions.plugins.legend.position).toBe('bottom')
      expect(mergedOptions.plugins.legend.labels.padding).toBe(30)
    })

    it('should preserve default options not overridden', () => {
      const customOptions = {
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      }

      wrapper = mount(LineChart, {
        props: {
          chartData: defaultChartData,
          chartOptions: customOptions
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const mergedOptions = baseChart.props('options')
      
      expect(mergedOptions.responsive).toBe(true)
      expect(mergedOptions.maintainAspectRatio).toBe(false)
      expect(mergedOptions.plugins.tooltip.mode).toBe('index')
    })

    it('should handle empty chartOptions', () => {
      wrapper = mount(LineChart, {
        props: {
          chartData: defaultChartData,
          chartOptions: {}
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const options = baseChart.props('options')
      
      expect(options.responsive).toBe(true)
      expect(options.plugins.legend.position).toBe('top')
    })
  })

  describe('Chart Data', () => {
    it('should handle chart data with multiple datasets', () => {
      const multiDatasetData = {
        labels: ['Jan', 'Feb', 'Mar'],
        datasets: [
          {
            label: 'Dataset 1',
            data: [10, 20, 30]
          },
          {
            label: 'Dataset 2',
            data: [15, 25, 35]
          }
        ]
      }

      wrapper = mount(LineChart, {
        props: {
          chartData: multiDatasetData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('data')).toEqual(multiDatasetData)
    })

    it('should handle empty datasets', () => {
      const emptyData = {
        labels: [],
        datasets: []
      }

      wrapper = mount(LineChart, {
        props: {
          chartData: emptyData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('data')).toEqual(emptyData)
    })
  })

  describe('Reactivity', () => {
    it('should update when chartData changes', async () => {
      wrapper = mount(LineChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const newChartData = {
        labels: ['May', 'Jun'],
        datasets: [{
          label: 'New Sales',
          data: [50, 60]
        }]
      }

      await wrapper.setProps({ chartData: newChartData })
      await wrapper.vm.$nextTick()

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('data')).toEqual(newChartData)
    })

    it('should update when title changes', async () => {
      wrapper = mount(LineChart, {
        props: {
          chartData: defaultChartData,
          title: 'Original Title'
        }
      })

      await wrapper.setProps({ title: 'Updated Title' })
      await wrapper.vm.$nextTick()

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('title')).toBe('Updated Title')
    })
  })
})



