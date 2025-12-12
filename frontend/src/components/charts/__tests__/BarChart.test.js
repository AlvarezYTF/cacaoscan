import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BarChart from '../BarChart.vue'

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

describe('BarChart', () => {
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
      wrapper = mount(BarChart, {
        props: {
          chartData: defaultChartData
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should render BaseChart component', () => {
      wrapper = mount(BarChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.exists()).toBe(true)
    })

    it('should pass type as bar to BaseChart', () => {
      wrapper = mount(BarChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('type')).toBe('bar')
    })
  })

  describe('Props', () => {
    it('should pass chartData to BaseChart', () => {
      wrapper = mount(BarChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('data')).toEqual(defaultChartData)
    })

    it('should pass title to BaseChart when provided', () => {
      wrapper = mount(BarChart, {
        props: {
          chartData: defaultChartData,
          title: 'Sales Chart'
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('title')).toBe('Sales Chart')
    })

    it('should pass empty title to BaseChart when not provided', () => {
      wrapper = mount(BarChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('title')).toBe('')
    })

    it('should pass default height to BaseChart', () => {
      wrapper = mount(BarChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('height')).toBe(400)
    })

    it('should pass custom height as string to BaseChart', () => {
      wrapper = mount(BarChart, {
        props: {
          chartData: defaultChartData,
          height: '500px'
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('height')).toBe('500px')
    })

    it('should pass custom height as number to BaseChart', () => {
      wrapper = mount(BarChart, {
        props: {
          chartData: defaultChartData,
          height: 600
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('height')).toBe(600)
    })

    it('should pass default containerClass to BaseChart', () => {
      wrapper = mount(BarChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('containerClass')).toBe('bg-white p-6 rounded-lg shadow-sm border border-gray-200')
    })

    it('should pass custom containerClass to BaseChart', () => {
      wrapper = mount(BarChart, {
        props: {
          chartData: defaultChartData,
          containerClass: 'custom-class'
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('containerClass')).toBe('custom-class')
    })
  })

  describe('Options Merging', () => {
    it('should merge default options with provided options', () => {
      wrapper = mount(BarChart, {
        props: {
          chartData: defaultChartData,
          options: {
            plugins: {
              legend: {
                display: false
              }
            }
          }
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const mergedOptions = baseChart.props('options')
      
      expect(mergedOptions.responsive).toBe(true)
      expect(mergedOptions.maintainAspectRatio).toBe(false)
      expect(mergedOptions.plugins.legend.display).toBe(false)
    })

    it('should use default options when no options provided', () => {
      wrapper = mount(BarChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const mergedOptions = baseChart.props('options')
      
      expect(mergedOptions.responsive).toBe(true)
      expect(mergedOptions.maintainAspectRatio).toBe(false)
      expect(mergedOptions.plugins.legend.display).toBe(true)
      expect(mergedOptions.plugins.legend.position).toBe('top')
    })

    it('should override default options with provided options', () => {
      wrapper = mount(BarChart, {
        props: {
          chartData: defaultChartData,
          options: {
            responsive: false,
            plugins: {
              tooltip: {
                enabled: false
              }
            }
          }
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const mergedOptions = baseChart.props('options')
      
      expect(mergedOptions.responsive).toBe(false)
      expect(mergedOptions.plugins.tooltip.enabled).toBe(false)
      expect(mergedOptions.maintainAspectRatio).toBe(false)
    })

    it('should preserve default scales configuration', () => {
      wrapper = mount(BarChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const mergedOptions = baseChart.props('options')
      
      expect(mergedOptions.scales.y.beginAtZero).toBe(true)
      expect(mergedOptions.scales.x.grid.display).toBe(false)
    })

    it('should merge nested options correctly', () => {
      wrapper = mount(BarChart, {
        props: {
          chartData: defaultChartData,
          options: {
            scales: {
              y: {
                beginAtZero: false,
                max: 100
              }
            }
          }
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const mergedOptions = baseChart.props('options')
      
      expect(mergedOptions.scales.y.beginAtZero).toBe(false)
      expect(mergedOptions.scales.y.max).toBe(100)
      expect(mergedOptions.scales.y.grid.display).toBe(true)
    })
  })

  describe('Default Options', () => {
    it('should have correct default tooltip configuration', () => {
      wrapper = mount(BarChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const mergedOptions = baseChart.props('options')
      
      expect(mergedOptions.plugins.tooltip.enabled).toBe(true)
      expect(mergedOptions.plugins.tooltip.mode).toBe('index')
      expect(mergedOptions.plugins.tooltip.intersect).toBe(false)
    })

    it('should have correct default interaction configuration', () => {
      wrapper = mount(BarChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const mergedOptions = baseChart.props('options')
      
      expect(mergedOptions.interaction.mode).toBe('nearest')
      expect(mergedOptions.interaction.axis).toBe('x')
      expect(mergedOptions.interaction.intersect).toBe(false)
    })

    it('should have correct default legend configuration', () => {
      wrapper = mount(BarChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const mergedOptions = baseChart.props('options')
      
      expect(mergedOptions.plugins.legend.display).toBe(true)
      expect(mergedOptions.plugins.legend.position).toBe('top')
      expect(mergedOptions.plugins.legend.labels.boxWidth).toBe(12)
      expect(mergedOptions.plugins.legend.labels.padding).toBe(15)
    })
  })

  describe('Reactivity', () => {
    it('should update options when props change', async () => {
      wrapper = mount(BarChart, {
        props: {
          chartData: defaultChartData,
          options: {
            responsive: true
          }
        }
      })

      await wrapper.setProps({
        options: {
          responsive: false
        }
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      const mergedOptions = baseChart.props('options')
      
      expect(mergedOptions.responsive).toBe(false)
    })

    it('should update chartData when props change', async () => {
      wrapper = mount(BarChart, {
        props: {
          chartData: defaultChartData
        }
      })

      const newChartData = {
        labels: ['May', 'Jun'],
        datasets: [{
          label: 'Revenue',
          data: [50, 60]
        }]
      }

      await wrapper.setProps({
        chartData: newChartData
      })

      const baseChart = wrapper.findComponent({ name: 'BaseChart' })
      expect(baseChart.props('data')).toEqual(newChartData)
    })
  })
})

