/**
 * Unit tests for useChartEvents composable
 */

import { describe, it, expect, vi } from 'vitest'
import { useChartEvents } from '../useChartEvents.js'

describe('useChartEvents', () => {
  describe('event handlers', () => {
    it('should create chart event handlers', () => {
      const emit = vi.fn()
      const chartEvents = useChartEvents(emit)

      expect(chartEvents.handleChartClick).toBeDefined()
      expect(chartEvents.handleChartHover).toBeDefined()
      expect(chartEvents.handleChartLoaded).toBeDefined()
    })

    it('should emit chart-click event', () => {
      const emit = vi.fn()
      const chartEvents = useChartEvents(emit)
      const clickData = { element: { index: 0 } }

      chartEvents.handleChartClick(clickData)

      expect(emit).toHaveBeenCalledWith('chart-click', clickData)
    })

    it('should emit chart-hover event', () => {
      const emit = vi.fn()
      const chartEvents = useChartEvents(emit)
      const hoverData = { element: { index: 1 } }

      chartEvents.handleChartHover(hoverData)

      expect(emit).toHaveBeenCalledWith('chart-hover', hoverData)
    })

    it('should emit chart-loaded event', () => {
      const emit = vi.fn()
      const chartEvents = useChartEvents(emit)
      const chartInstance = { id: 'chart-1' }

      chartEvents.handleChartLoaded(chartInstance)

      expect(emit).toHaveBeenCalledWith('chart-loaded', chartInstance)
    })
  })
})

