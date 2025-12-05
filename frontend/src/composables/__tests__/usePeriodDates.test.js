/**
 * Unit tests for usePeriodDates composable
 */

import { describe, it, expect, vi } from 'vitest'
import { usePeriodDates, calculatePeriodDates } from '../usePeriodDates.js'

describe('usePeriodDates', () => {
  describe('calculatePeriodDates', () => {
    it('should calculate today period', () => {
      const today = new Date('2024-01-15')
      const result = calculatePeriodDates('today', today)
      
      expect(result.fecha_desde).toBe('2024-01-15')
      expect(result.fecha_hasta).toBe('2024-01-15')
    })

    it('should calculate week period', () => {
      const today = new Date('2024-01-15')
      const result = calculatePeriodDates('week', today)
      
      expect(result.fecha_hasta).toBe('2024-01-15')
      expect(result.fecha_desde).toBeTruthy()
    })

    it('should calculate month period', () => {
      const today = new Date('2024-01-15')
      const result = calculatePeriodDates('month', today)
      
      expect(result.fecha_hasta).toBe('2024-01-15')
      expect(result.fecha_desde).toBeTruthy()
    })

    it('should calculate quarter period', () => {
      const today = new Date('2024-01-15')
      const result = calculatePeriodDates('quarter', today)
      
      expect(result.fecha_hasta).toBe('2024-01-15')
      expect(result.fecha_desde).toBeTruthy()
      const desdeDate = new Date(result.fecha_desde)
      const hastaDate = new Date(result.fecha_hasta)
      const diffDays = Math.floor((hastaDate - desdeDate) / (1000 * 60 * 60 * 24))
      expect(diffDays).toBeCloseTo(90, 0)
    })

    it('should calculate year period', () => {
      const today = new Date('2024-01-15')
      const result = calculatePeriodDates('year', today)
      
      expect(result.fecha_hasta).toBe('2024-01-15')
      expect(result.fecha_desde).toBeTruthy()
      const desdeDate = new Date(result.fecha_desde)
      const hastaDate = new Date(result.fecha_hasta)
      const diffDays = Math.floor((hastaDate - desdeDate) / (1000 * 60 * 60 * 24))
      expect(diffDays).toBeCloseTo(365, 0)
    })

    it('should return empty dates for custom period', () => {
      const result = calculatePeriodDates('custom')
      
      expect(result.fecha_desde).toBe('')
      expect(result.fecha_hasta).toBeTruthy()
    })

    it('should handle default/unknown period', () => {
      const today = new Date('2024-01-15')
      const result = calculatePeriodDates('unknown', today)
      
      expect(result.fecha_desde).toBe('')
      expect(result.fecha_hasta).toBe('2024-01-15')
    })

    it('should use current date when referenceDate not provided', () => {
      const result = calculatePeriodDates('today')
      const today = new Date().toISOString().split('T')[0]
      
      expect(result.fecha_desde).toBe(today)
      expect(result.fecha_hasta).toBe(today)
    })
  })

  describe('usePeriodDates', () => {
    it('should initialize with default period', () => {
      const period = usePeriodDates()
      
      expect(period.selectedPeriod.value).toBe('week')
      expect(period.fecha_desde.value).toBeTruthy()
      expect(period.fecha_hasta.value).toBeTruthy()
    })

    it('should accept custom initial period', () => {
      const period = usePeriodDates({ initialPeriod: 'month' })
      
      expect(period.selectedPeriod.value).toBe('month')
    })

    it('should set period and calculate dates', () => {
      const period = usePeriodDates()
      
      period.setPeriod('month')
      
      expect(period.selectedPeriod.value).toBe('month')
      expect(period.fecha_desde.value).toBeTruthy()
      expect(period.fecha_hasta.value).toBeTruthy()
    })

    it('should handle custom period', () => {
      const period = usePeriodDates()
      
      period.setPeriod('custom')
      
      expect(period.selectedPeriod.value).toBe('custom')
    })

    it('should set custom dates', () => {
      const period = usePeriodDates()
      
      period.setCustomDates('2024-01-01', '2024-01-31')
      
      expect(period.selectedPeriod.value).toBe('custom')
      expect(period.fecha_desde.value).toBe('2024-01-01')
      expect(period.fecha_hasta.value).toBe('2024-01-31')
    })

    it('should call onPeriodChange callback', () => {
      const onPeriodChange = vi.fn()
      const period = usePeriodDates({ onPeriodChange })
      
      period.setPeriod('month')
      
      expect(onPeriodChange).toHaveBeenCalled()
    })

    it('should call onPeriodChange for custom period', () => {
      const onPeriodChange = vi.fn()
      const period = usePeriodDates({ onPeriodChange })
      
      period.setPeriod('custom')
      
      expect(onPeriodChange).toHaveBeenCalledWith('custom', period.fecha_desde.value, period.fecha_hasta.value)
    })

    it('should call onPeriodChange when setting custom dates', () => {
      const onPeriodChange = vi.fn()
      const period = usePeriodDates({ onPeriodChange })
      
      period.setCustomDates('2024-01-01', '2024-01-31')
      
      expect(onPeriodChange).toHaveBeenCalledWith('custom', '2024-01-01', '2024-01-31')
    })

    it('should reset to initial period', () => {
      const period = usePeriodDates({ initialPeriod: 'week' })
      
      period.setPeriod('month')
      period.resetPeriod()
      
      expect(period.selectedPeriod.value).toBe('week')
    })

    it('should not change dates for custom period when setting', () => {
      const period = usePeriodDates()
      period.setCustomDates('2024-01-01', '2024-01-31')
      const originalDesde = period.fecha_desde.value
      const originalHasta = period.fecha_hasta.value
      
      period.setPeriod('custom')
      
      expect(period.fecha_desde.value).toBe(originalDesde)
      expect(period.fecha_hasta.value).toBe(originalHasta)
    })
  })
})

