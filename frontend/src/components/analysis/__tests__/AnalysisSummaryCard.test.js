import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import AnalysisSummaryCard from '../AnalysisSummaryCard.vue'

describe('AnalysisSummaryCard', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render component', () => {
    wrapper = mount(AnalysisSummaryCard)

    expect(wrapper.exists()).toBe(true)
  })

  it('should display default title', () => {
    wrapper = mount(AnalysisSummaryCard)

    const title = wrapper.find('h3')
    expect(title.exists()).toBe(true)
    expect(title.text()).toBe('Resumen del Análisis')
  })

  it('should display default quality score of 0', () => {
    wrapper = mount(AnalysisSummaryCard)

    const qualityScoreText = wrapper.text()
    expect(qualityScoreText).toContain('0/100')
  })

  it('should display custom quality score', () => {
    wrapper = mount(AnalysisSummaryCard, {
      props: {
        qualityScore: 85
      }
    })

    const qualityScoreText = wrapper.text()
    expect(qualityScoreText).toContain('85/100')
  })

  it('should display quality score progress bar with correct width', () => {
    wrapper = mount(AnalysisSummaryCard, {
      props: {
        qualityScore: 75
      }
    })

    const progressBar = wrapper.find('.bg-green-600')
    expect(progressBar.exists()).toBe(true)
    expect(progressBar.element.style.width).toBe('75%')
  })

  it('should display quality score progress bar at 0% when score is 0', () => {
    wrapper = mount(AnalysisSummaryCard, {
      props: {
        qualityScore: 0
      }
    })

    const progressBar = wrapper.find('.bg-green-600')
    expect(progressBar.exists()).toBe(true)
    expect(progressBar.element.style.width).toBe('0%')
  })

  it('should display quality score progress bar at 100% when score is 100', () => {
    wrapper = mount(AnalysisSummaryCard, {
      props: {
        qualityScore: 100
      }
    })

    const progressBar = wrapper.find('.bg-green-600')
    expect(progressBar.exists()).toBe(true)
    expect(progressBar.element.style.width).toBe('100%')
  })

  it('should display default defect count of 0', () => {
    wrapper = mount(AnalysisSummaryCard)

    const defectCountText = wrapper.text()
    expect(defectCountText).toContain('Defectos Detectados')
    expect(defectCountText).toContain('0')
  })

  it('should display custom defect count', () => {
    wrapper = mount(AnalysisSummaryCard, {
      props: {
        defectCount: 5
      }
    })

    const defectCountText = wrapper.text()
    expect(defectCountText).toContain('5')
  })

  it('should display empty metrics list by default', () => {
    wrapper = mount(AnalysisSummaryCard)

    const metricsSection = wrapper.find('.space-y-2')
    expect(metricsSection.exists()).toBe(true)
    
    // Should not have any metric items
    const metricItems = wrapper.findAll('.flex.justify-between.text-sm')
    // There should be 2 items: quality score and defect count, but no metrics
    expect(metricItems.length).toBe(2)
  })

  it('should display metrics when provided', () => {
    const metrics = [
      { name: 'Granos Totales', value: '1000' },
      { name: 'Granos Buenos', value: '950' },
      { name: 'Granos Defectuosos', value: '50' }
    ]

    wrapper = mount(AnalysisSummaryCard, {
      props: {
        metrics
      }
    })

    const metricItems = wrapper.findAll('.flex.justify-between.text-sm')
    // Should have quality score, defect count, plus 3 metrics
    expect(metricItems.length).toBeGreaterThanOrEqual(3)
    
    for (const metric of metrics) {
      expect(wrapper.text()).toContain(metric.name)
      expect(wrapper.text()).toContain(metric.value)
    }
  })

  it('should display multiple metrics correctly', () => {
    const metrics = [
      { name: 'Metric 1', value: 'Value 1' },
      { name: 'Metric 2', value: 'Value 2' },
      { name: 'Metric 3', value: 'Value 3' }
    ]

    wrapper = mount(AnalysisSummaryCard, {
      props: {
        metrics
      }
    })

    for (const metric of metrics) {
      const metricText = wrapper.text()
      expect(metricText).toContain(metric.name)
      expect(metricText).toContain(metric.value)
    }
  })

  it('should handle all props together', () => {
    const metrics = [
      { name: 'Test Metric', value: 'Test Value' }
    ]

    wrapper = mount(AnalysisSummaryCard, {
      props: {
        qualityScore: 90,
        defectCount: 3,
        metrics
      }
    })

    expect(wrapper.text()).toContain('90/100')
    expect(wrapper.text()).toContain('3')
    expect(wrapper.text()).toContain('Test Metric')
    expect(wrapper.text()).toContain('Test Value')
  })

  it('should update quality score when prop changes', async () => {
    wrapper = mount(AnalysisSummaryCard, {
      props: {
        qualityScore: 50
      }
    })

    expect(wrapper.text()).toContain('50/100')

    await wrapper.setProps({ qualityScore: 80 })

    expect(wrapper.text()).toContain('80/100')
    
    const progressBar = wrapper.find('.bg-green-600')
    expect(progressBar.element.style.width).toBe('80%')
  })

  it('should update defect count when prop changes', async () => {
    wrapper = mount(AnalysisSummaryCard, {
      props: {
        defectCount: 5
      }
    })

    expect(wrapper.text()).toContain('5')

    await wrapper.setProps({ defectCount: 10 })

    expect(wrapper.text()).toContain('10')
  })

  it('should update metrics when prop changes', async () => {
    wrapper = mount(AnalysisSummaryCard, {
      props: {
        metrics: [{ name: 'Initial', value: 'Value' }]
      }
    })

    expect(wrapper.text()).toContain('Initial')

    await wrapper.setProps({
      metrics: [{ name: 'Updated', value: 'New Value' }]
    })

    expect(wrapper.text()).toContain('Updated')
    expect(wrapper.text()).toContain('New Value')
    expect(wrapper.text()).not.toContain('Initial')
  })

  it('should handle quality score above 100', () => {
    wrapper = mount(AnalysisSummaryCard, {
      props: {
        qualityScore: 150
      }
    })

    expect(wrapper.text()).toContain('150/100')
    const progressBar = wrapper.find('.bg-green-600')
    // The component normalizes quality score to max 100, so width should be 100%
    expect(progressBar.element.style.width).toBe('100%')
  })

  it('should handle negative quality score', () => {
    wrapper = mount(AnalysisSummaryCard, {
      props: {
        qualityScore: -10
      }
    })

    expect(wrapper.text()).toContain('-10/100')
    const progressBar = wrapper.find('.bg-green-600')
    expect(progressBar.exists()).toBe(true)
    const style = progressBar.element.style.width
    expect(style).toBe('0%')
  })

  it('should handle large defect count', () => {
    wrapper = mount(AnalysisSummaryCard, {
      props: {
        defectCount: 9999
      }
    })

    expect(wrapper.text()).toContain('9999')
  })

  it('should render with correct CSS classes', () => {
    wrapper = mount(AnalysisSummaryCard)

    expect(wrapper.classes()).toContain('bg-gray-50')
    expect(wrapper.find('.rounded-lg').exists()).toBe(true)
  })

  it('should have proper structure with all sections', () => {
    wrapper = mount(AnalysisSummaryCard, {
      props: {
        qualityScore: 75,
        defectCount: 5,
        metrics: [{ name: 'Test', value: 'Value' }]
      }
    })

    // Check for quality score section
    expect(wrapper.find('.font-semibold.text-green-600').exists()).toBe(true)
    
    // Check for defect count section
    expect(wrapper.text()).toContain('Defectos Detectados')
    
    // Check for metrics section
    expect(wrapper.find('.border-t.border-gray-200').exists()).toBe(true)
  })
})

