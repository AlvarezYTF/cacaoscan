import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import AdvancedChart from '../AdvancedChart.vue'

// Mock BaseChart component
vi.mock('../BaseChart.vue', () => ({
  default: {
    name: 'BaseChart',
    template: `
      <div class="base-chart">
        <div v-if="title" class="chart-header">
          <h3 class="chart-title">{{ title }}</h3>
        </div>
        <div class="chart-body">
          <div class="chart-container"><canvas></canvas></div>
        </div>
      </div>
    `,
    props: ['chartData', 'options', 'type', 'title', 'height', 'responsive', 'maintainAspectRatio', 'showControls', 'showLegend', 'legendPosition', 'animation', 'animationDuration', 'colors', 'gradient', 'theme', 'enableResizeObserver'],
    emits: ['chart-click', 'chart-hover', 'chart-loaded'],
    setup(props, { emit }) {
      return {
        emit
      }
    }
  }
}))

vi.mock('chart.js', () => {
  const mockChart = vi.fn().mockImplementation(() => ({
    destroy: vi.fn(),
    update: vi.fn(),
    resize: vi.fn(),
    toBase64Image: vi.fn().mockReturnValue('data:image/png;base64,test')
  }))

  mockChart.register = vi.fn()

  return {
    Chart: mockChart,
    registerables: []
  }
})

describe('AdvancedChart', () => {
  let wrapper

  const defaultChartData = {
    labels: ['Jan', 'Feb', 'Mar'],
    datasets: [{
      label: 'Test Data',
      data: [10, 20, 30]
    }]
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render chart container', () => {
    wrapper = mount(AdvancedChart, {
      props: {
        chartData: defaultChartData
      }
    })

    expect(wrapper.find('.base-chart').exists()).toBe(true)
    expect(wrapper.find('.chart-container').exists()).toBe(true)
    expect(wrapper.find('canvas').exists()).toBe(true)
  })

  it('should display title when provided', () => {
    wrapper = mount(AdvancedChart, {
      props: {
        chartData: defaultChartData,
        title: 'Test Chart'
      }
    })

    expect(wrapper.find('.chart-title').exists()).toBe(true)
    expect(wrapper.text()).toContain('Test Chart')
  })

  it('should not display title when not provided', () => {
    wrapper = mount(AdvancedChart, {
      props: {
        chartData: defaultChartData
      }
    })

    expect(wrapper.find('.chart-title').exists()).toBe(false)
  })

  it('should apply custom height', () => {
    wrapper = mount(AdvancedChart, {
      props: {
        chartData: defaultChartData,
        height: '500px'
      }
    })

    // AdvancedChart passes height as prop to BaseChart through $attrs
    const baseChart = wrapper.findComponent({ name: 'BaseChart' })
    expect(baseChart.exists()).toBe(true)
    expect(baseChart.props('height')).toBe('500px')
  })

  it('should pass props to BaseChart correctly', () => {
    wrapper = mount(AdvancedChart, {
      props: {
        chartData: defaultChartData,
        type: 'bar',
        title: 'Test Chart',
        height: '400px'
      }
    })

    const baseChart = wrapper.findComponent({ name: 'BaseChart' })
    expect(baseChart.exists()).toBe(true)
    expect(baseChart.props('type')).toBe('bar')
    expect(baseChart.props('title')).toBe('Test Chart')
    expect(baseChart.props('height')).toBe('400px')
  })

  it('should handle chart-loaded event', async () => {
    wrapper = mount(AdvancedChart, {
      props: {
        chartData: defaultChartData
      }
    })

    const baseChart = wrapper.findComponent({ name: 'BaseChart' })
    await baseChart.vm.$emit('chart-loaded', {})
    
    expect(wrapper.emitted('chart-loaded')).toBeTruthy()
  })
})

