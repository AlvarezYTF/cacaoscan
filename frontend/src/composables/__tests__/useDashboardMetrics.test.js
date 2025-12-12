/**
 * Unit tests for useDashboardMetrics composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useDashboardMetrics } from '../useDashboardMetrics.js'

// Mock useDateFormatting
vi.mock('../useDateFormatting', () => ({
  useDateFormatting: () => ({
    formatDate: vi.fn((date) => date),
    formatNumber: vi.fn((num) => num.toString())
  })
}))

describe('useDashboardMetrics', () => {
  let metrics

  beforeEach(() => {
    metrics = useDashboardMetrics()
  })

  describe('formatMetricValue', () => {
    it('should format number value', () => {
      const result = metrics.formatMetricValue(1000)
      
      expect(result).toBeTruthy()
    })

    it('should format large numbers with abbreviations', () => {
      const result = metrics.formatMetricValue(1500000)
      
      expect(result).toContain('M')
    })

    it('should format thousands with K', () => {
      const result = metrics.formatMetricValue(5000)
      
      expect(result).toContain('K')
    })

    it('should return N/A for null', () => {
      const result = metrics.formatMetricValue(null)
      
      expect(result).toBe('N/A')
    })
  })

  describe('formatPercentageChange', () => {
    it('should format positive change', () => {
      const result = metrics.formatPercentageChange(10.5)
      
      expect(result).toContain('+')
      expect(result).toContain('%')
    })

    it('should format negative change', () => {
      const result = metrics.formatPercentageChange(-5.2)
      
      expect(result).toContain('%')
    })
  })

  describe('getChangeClass', () => {
    it('should return positive for positive change', () => {
      expect(metrics.getChangeClass(10)).toBe('positive')
    })

    it('should return negative for negative change', () => {
      expect(metrics.getChangeClass(-5)).toBe('negative')
    })

    it('should return neutral for zero', () => {
      expect(metrics.getChangeClass(0)).toBe('neutral')
    })
  })

  describe('getChangeIcon', () => {
    it('should return arrow-up for positive change', () => {
      expect(metrics.getChangeIcon(10)).toContain('arrow-up')
    })

    it('should return arrow-down for negative change', () => {
      expect(metrics.getChangeIcon(-5)).toContain('arrow-down')
    })
  })

  describe('calculatePercentageChange', () => {
    it('should calculate percentage change', () => {
      const result = metrics.calculatePercentageChange(110, 100)
      
      expect(result).toBe(10)
    })

    it('should handle zero previous value', () => {
      const result = metrics.calculatePercentageChange(10, 0)
      
      expect(result).toBe(100)
    })

    it('should handle zero current value with zero previous', () => {
      const result = metrics.calculatePercentageChange(0, 0)
      
      expect(result).toBe(0)
    })

    it('should calculate negative change', () => {
      const result = metrics.calculatePercentageChange(90, 100)
      
      expect(result).toBe(-10)
    })
  })

  describe('formatMetricValue', () => {
    it('should format with suffix', () => {
      const result = metrics.formatMetricValue(100, { suffix: 'g' })
      expect(result).toContain('g')
    })

    it('should format with prefix', () => {
      const result = metrics.formatMetricValue(100, { prefix: '$' })
      expect(result).toContain('$')
    })

    it('should format with decimals', () => {
      const result = metrics.formatMetricValue(100.123, { decimals: 2 })
      expect(result).toContain('100')
    })

    it('should format undefined as N/A', () => {
      const result = metrics.formatMetricValue(undefined)
      expect(result).toBe('N/A')
    })

    it('should format string value', () => {
      const result = metrics.formatMetricValue('100')
      expect(result).toBe('100')
    })
  })

  describe('formatPercentageChange', () => {
    it('should format null as empty string', () => {
      const result = metrics.formatPercentageChange(null)
      expect(result).toBe('')
    })

    it('should format undefined as empty string', () => {
      const result = metrics.formatPercentageChange(undefined)
      expect(result).toBe('')
    })

    it('should format non-number as string', () => {
      const result = metrics.formatPercentageChange('10')
      expect(result).toBe('10')
    })

    it('should format zero change', () => {
      const result = metrics.formatPercentageChange(0)
      expect(result).toBe('+0.0%')
    })
  })

  describe('getChangeClass', () => {
    it('should return neutral for null', () => {
      expect(metrics.getChangeClass(null)).toBe('neutral')
    })

    it('should return neutral for undefined', () => {
      expect(metrics.getChangeClass(undefined)).toBe('neutral')
    })

    it('should return neutral for non-number', () => {
      expect(metrics.getChangeClass('string')).toBe('neutral')
    })
  })

  describe('getChangeIcon', () => {
    it('should return minus for null', () => {
      expect(metrics.getChangeIcon(null)).toContain('minus')
    })

    it('should return minus for undefined', () => {
      expect(metrics.getChangeIcon(undefined)).toContain('minus')
    })

    it('should return minus for non-number', () => {
      expect(metrics.getChangeIcon('string')).toContain('minus')
    })

    it('should return minus for zero', () => {
      expect(metrics.getChangeIcon(0)).toContain('minus')
    })
  })

  describe('buildStatCard', () => {
    it('should build stat card with all properties', () => {
      const config = {
        id: 'test',
        value: 100,
        previousValue: 90,
        label: 'Test Stat',
        icon: 'test-icon',
        variant: 'primary',
        suffix: 'g',
        prefix: '$',
        description: 'Test description',
        trendData: [1, 2, 3],
        changePeriod: 'vs last week',
        clickable: true
      }

      const result = metrics.buildStatCard(config)

      expect(result.id).toBe('test')
      expect(result.rawValue).toBe(100)
      expect(result.label).toBe('Test Stat')
      expect(result.icon).toBe('test-icon')
      expect(result.variant).toBe('primary')
      expect(result.suffix).toBe('g')
      expect(result.prefix).toBe('$')
      expect(result.description).toBe('Test description')
      expect(result.change).toBeDefined()
      expect(result.trend).toBeDefined()
      expect(result.clickable).toBe(true)
    })

    it('should build stat card with default values', () => {
      const config = {
        id: 'test',
        label: 'Test Stat'
      }

      const result = metrics.buildStatCard(config)

      expect(result.value).toBe('0')
      expect(result.rawValue).toBe(0)
      expect(result.variant).toBe('default')
      expect(result.changePeriod).toBe('vs período anterior')
      expect(result.clickable).toBe(false)
    })

    it('should handle null previousValue', () => {
      const config = {
        id: 'test',
        value: 100,
        previousValue: null,
        label: 'Test Stat'
      }

      const result = metrics.buildStatCard(config)

      expect(result.change).toBeUndefined()
      expect(result.rawChange).toBe(null)
    })

    it('should handle empty trendData', () => {
      const config = {
        id: 'test',
        value: 100,
        label: 'Test Stat',
        trendData: []
      }

      const result = metrics.buildStatCard(config)

      expect(result.trend).toBe(null)
    })
  })

  describe('buildStatCards', () => {
    it('should build multiple stat cards', () => {
      const configs = [
        { id: '1', value: 100, label: 'Stat 1' },
        { id: '2', value: 200, label: 'Stat 2' }
      ]

      const result = metrics.buildStatCards(configs)

      expect(result).toHaveLength(2)
      expect(result[0].id).toBe('1')
      expect(result[1].id).toBe('2')
    })
  })

  describe('getVariantColor', () => {
    it('should return color for known variant', () => {
      expect(metrics.getVariantColor('primary')).toBe('#3b82f6')
      expect(metrics.getVariantColor('success')).toBe('#10b981')
      expect(metrics.getVariantColor('warning')).toBe('#f59e0b')
      expect(metrics.getVariantColor('danger')).toBe('#ef4444')
      expect(metrics.getVariantColor('info')).toBe('#06b6d4')
    })

    it('should return default color for unknown variant', () => {
      expect(metrics.getVariantColor('unknown')).toBe('#6b7280')
    })
  })

  describe('normalizeStatsData', () => {
    it('should normalize stats data with default mapping', () => {
      const apiData = {
        total_users: 100,
        total_fincas: 50,
        total_analyses: 200,
        avg_quality: 0.95
      }

      const result = metrics.normalizeStatsData(apiData)

      expect(result.totalUsers).toBe(100)
      expect(result.totalFincas).toBe(50)
      expect(result.totalAnalyses).toBe(200)
      expect(result.avgQuality).toBe(0.95)
    })

    it('should normalize stats data with custom mapping', () => {
      const apiData = {
        users_count: 100,
        farms_count: 50
      }
      const mapping = {
        totalUsers: 'users_count',
        totalFincas: 'farms_count'
      }

      const result = metrics.normalizeStatsData(apiData, mapping)

      expect(result.totalUsers).toBe(100)
      expect(result.totalFincas).toBe(50)
    })

    it('should handle missing fields', () => {
      const apiData = {
        total_users: 100
      }

      const result = metrics.normalizeStatsData(apiData)

      expect(result.totalUsers).toBe(100)
      expect(result.totalFincas).toBeUndefined()
    })
  })
})

