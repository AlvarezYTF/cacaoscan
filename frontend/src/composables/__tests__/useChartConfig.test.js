/**
 * Unit tests for useChartConfig composable
 */

import { describe, it, expect, vi } from 'vitest'
import { useChartConfig, DEFAULT_CHART_COLORS, CHART_THEMES } from '../useChartConfig.js'

describe('useChartConfig', () => {
  describe('constants', () => {
    it('should export DEFAULT_CHART_COLORS', () => {
      expect(DEFAULT_CHART_COLORS).toBeDefined()
      expect(Array.isArray(DEFAULT_CHART_COLORS)).toBe(true)
      expect(DEFAULT_CHART_COLORS.length).toBeGreaterThan(0)
    })

    it('should export CHART_THEMES', () => {
      expect(CHART_THEMES).toBeDefined()
      expect(CHART_THEMES.light).toBeDefined()
      expect(CHART_THEMES.dark).toBeDefined()
    })
  })

  describe('useChartConfig', () => {
    it('should create chart config with default options', () => {
      const config = useChartConfig()
      
      expect(config.getDefaultOptions.value).toBeDefined()
      expect(config.colors).toBeDefined()
    })

    it('should use light theme by default', () => {
      const config = useChartConfig()
      
      expect(config.themeColors.value).toEqual(CHART_THEMES.light)
    })

    it('should use dark theme when specified', () => {
      const config = useChartConfig({ theme: 'dark' })
      
      expect(config.themeColors.value).toEqual(CHART_THEMES.dark)
    })

    it('should accept custom colors', () => {
      const customColors = ['#ff0000', '#00ff00']
      const config = useChartConfig({ colors: customColors })
      
      expect(config.colors).toEqual(customColors)
    })

    it('should create default options for line chart', () => {
      const config = useChartConfig({ type: 'line' })
      const options = config.getDefaultOptions.value
      
      expect(options.responsive).toBe(true)
      expect(options.plugins).toBeDefined()
      expect(options.scales).toBeDefined()
    })

    it('should process chart data correctly', () => {
      const config = useChartConfig()
      const chartData = {
        labels: ['A', 'B'],
        datasets: [{
          label: 'Dataset 1',
          data: [1, 2]
        }]
      }
      
      const processed = config.processChartData(chartData)
      
      expect(processed.datasets[0].backgroundColor).toBeDefined()
    })

    it('should apply colors to pie chart', () => {
      const config = useChartConfig({ type: 'pie' })
      const chartData = {
        labels: ['A', 'B', 'C'],
        datasets: [{
          data: [1, 2, 3]
        }]
      }
      
      const processed = config.processChartData(chartData)
      
      expect(Array.isArray(processed.datasets[0].backgroundColor)).toBe(true)
    })

    it('should create gradient', () => {
      const config = useChartConfig()
      const mockAddColorStop = vi.fn()
      const mockGradient = {
        addColorStop: mockAddColorStop
      }
      const mockCtx = {
        createLinearGradient: vi.fn(() => mockGradient)
      }
      
      const gradient = config.createGradient(mockCtx, '#3498db', 400)
      
      expect(mockCtx.createLinearGradient).toHaveBeenCalled()
      expect(gradient).toBeDefined()
      expect(mockAddColorStop).toHaveBeenCalledTimes(2)
    })

    it('should use default height for gradient', () => {
      const config = useChartConfig()
      const mockAddColorStop = vi.fn()
      const mockGradient = {
        addColorStop: mockAddColorStop
      }
      const mockCtx = {
        createLinearGradient: vi.fn(() => mockGradient)
      }
      
      config.createGradient(mockCtx, '#3498db')
      
      expect(mockCtx.createLinearGradient).toHaveBeenCalledWith(0, 0, 0, 400)
    })

    it('should process chart data with gradient', () => {
      const config = useChartConfig({ type: 'line' })
      const mockGradient = {}
      const createGradient = vi.fn(() => mockGradient)
      const chartData = {
        labels: ['A', 'B'],
        datasets: [{
          label: 'Dataset 1',
          data: [1, 2]
        }]
      }
      
      const processed = config.processChartData(chartData, true, createGradient)
      
      expect(processed.datasets[0].backgroundColor).toBe(mockGradient)
      expect(createGradient).toHaveBeenCalled()
    })

    it('should process chart data without datasets', () => {
      const config = useChartConfig()
      const chartData = { labels: ['A', 'B'] }
      
      const processed = config.processChartData(chartData)
      
      expect(processed).toBe(chartData)
    })

    it('should process chart data with null', () => {
      const config = useChartConfig()
      
      const processed = config.processChartData(null)
      
      expect(processed).toBe(null)
    })

    it('should process bar chart data', () => {
      const config = useChartConfig({ type: 'bar' })
      const chartData = {
        labels: ['A', 'B'],
        datasets: [{
          label: 'Dataset 1',
          data: [1, 2]
        }]
      }
      
      const processed = config.processChartData(chartData)
      
      expect(processed.datasets[0].borderWidth).toBe(1)
      expect(processed.datasets[0].borderRadius).toBe(4)
      expect(processed.datasets[0].borderSkipped).toBe(false)
    })

    it('should process doughnut chart data', () => {
      const config = useChartConfig({ type: 'doughnut' })
      const chartData = {
        labels: ['A', 'B', 'C'],
        datasets: [{
          data: [1, 2, 3]
        }]
      }
      
      const processed = config.processChartData(chartData)
      
      expect(Array.isArray(processed.datasets[0].backgroundColor)).toBe(true)
      expect(processed.datasets[0].borderColor).toBeUndefined()
    })

    it('should preserve existing backgroundColor', () => {
      const config = useChartConfig()
      const chartData = {
        labels: ['A', 'B'],
        datasets: [{
          label: 'Dataset 1',
          data: [1, 2],
          backgroundColor: 'custom-color'
        }]
      }
      
      const processed = config.processChartData(chartData)
      
      expect(processed.datasets[0].backgroundColor).toBe('custom-color')
    })

    it('should preserve existing borderColor', () => {
      const config = useChartConfig({ type: 'line' })
      const chartData = {
        labels: ['A', 'B'],
        datasets: [{
          label: 'Dataset 1',
          data: [1, 2],
          borderColor: 'custom-border'
        }]
      }
      
      const processed = config.processChartData(chartData)
      
      expect(processed.datasets[0].borderColor).toBe('custom-border')
    })

    it('should handle unknown theme', () => {
      const config = useChartConfig({ theme: 'unknown' })
      
      expect(config.themeColors.value).toEqual(CHART_THEMES.light)
    })

    it('should configure chart without animation', () => {
      const config = useChartConfig({ animation: false })
      const options = config.getDefaultOptions.value
      
      expect(options.animation).toBe(false)
    })

    it('should configure chart with custom animation duration', () => {
      const config = useChartConfig({ animationDuration: 2000 })
      const options = config.getDefaultOptions.value
      
      expect(options.animation.duration).toBe(2000)
    })

    it('should configure chart without legend', () => {
      const config = useChartConfig({ showLegend: false })
      const options = config.getDefaultOptions.value
      
      expect(options.plugins.legend.display).toBe(false)
    })

    it('should configure chart with custom legend position', () => {
      const config = useChartConfig({ legendPosition: 'bottom' })
      const options = config.getDefaultOptions.value
      
      expect(options.plugins.legend.position).toBe('bottom')
    })

    it('should not include scales for pie charts', () => {
      const config = useChartConfig({ type: 'pie' })
      const options = config.getDefaultOptions.value
      
      expect(options.scales).toEqual({})
    })

    it('should not include scales for doughnut charts', () => {
      const config = useChartConfig({ type: 'doughnut' })
      const options = config.getDefaultOptions.value
      
      expect(options.scales).toEqual({})
    })

    it('should handle tooltip callbacks', () => {
      const config = useChartConfig()
      const options = config.getDefaultOptions.value
      const tooltipCallbacks = options.plugins.tooltip.callbacks
      
      const title = tooltipCallbacks.title([{ label: 'Test' }])
      expect(title).toBe('Test')
      
      const label = tooltipCallbacks.label({ dataset: { label: 'Dataset' }, parsed: { y: 100 } })
      expect(label).toContain('Dataset')
      expect(label).toContain('100')
    })

    it('should handle tooltip with raw value', () => {
      const config = useChartConfig()
      const options = config.getDefaultOptions.value
      const tooltipCallbacks = options.plugins.tooltip.callbacks
      
      const label = tooltipCallbacks.label({ dataset: { label: 'Dataset' }, raw: 'raw-value' })
      expect(label).toContain('raw-value')
    })

    it('should handle multiple datasets with color cycling', () => {
      const config = useChartConfig()
      const chartData = {
        labels: ['A', 'B'],
        datasets: [
          { label: 'Dataset 1', data: [1, 2] },
          { label: 'Dataset 2', data: [3, 4] },
          { label: 'Dataset 3', data: [5, 6] }
        ]
      }
      
      const processed = config.processChartData(chartData)
      
      expect(processed.datasets[0].backgroundColor).toBe(DEFAULT_CHART_COLORS[0])
      expect(processed.datasets[1].backgroundColor).toBe(DEFAULT_CHART_COLORS[1])
      expect(processed.datasets[2].backgroundColor).toBe(DEFAULT_CHART_COLORS[2])
    })
  })
})

