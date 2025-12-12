/**
 * Unit tests for formatters utility functions
 * Pure functions with no external dependencies - deterministic tests
 */

import { describe, it, expect } from 'vitest'
import {
  formatNumber,
  formatCurrency,
  formatPercentage,
  formatDate,
  formatDateTime,
  formatChange,
  formatFileSize,
  formatDuration,
  parseChange
} from '../formatters.js'

describe('formatters', () => {
  describe('formatNumber', () => {
    it('should format number with default locale and options', () => {
      expect(formatNumber(1234.56)).toBe('1.234,56')
    })

    it('should format integer numbers', () => {
      expect(formatNumber(1234)).toBe('1.234')
    })

    it('should format large numbers', () => {
      expect(formatNumber(1000000)).toBe('1.000.000')
    })

    it('should handle decimal numbers', () => {
      expect(formatNumber(1234.567)).toBe('1.234,57')
    })

    it('should respect minimumFractionDigits option', () => {
      expect(formatNumber(1234, { minimumFractionDigits: 2 })).toBe('1.234,00')
    })

    it('should respect maximumFractionDigits option', () => {
      expect(formatNumber(1234.567, { maximumFractionDigits: 1 })).toBe('1.234,6')
    })

    it('should handle string numbers', () => {
      expect(formatNumber('1234.56')).toBe('1.234,56')
    })

    it('should handle custom locale', () => {
      expect(formatNumber(1234.56, { locale: 'en-US' })).toBe('1,234.56')
    })

    it('should return string value for NaN input', () => {
      expect(formatNumber('invalid')).toBe('invalid')
    })

    it('should handle null input', () => {
      expect(formatNumber(null)).toBe('null')
    })

    it('should handle undefined input', () => {
      expect(formatNumber(undefined)).toBe('undefined')
    })

    it('should handle zero', () => {
      expect(formatNumber(0)).toBe('0')
    })

    it('should handle negative numbers', () => {
      expect(formatNumber(-1234.56)).toBe('-1.234,56')
    })
  })

  describe('formatCurrency', () => {
    it('should format currency with default options', () => {
      const result = formatCurrency(1234.56)
      expect(result).toMatch(/\d+/)
      expect(typeof result).toBe('string')
    })

    it('should format currency as integer (no decimals)', () => {
      const result = formatCurrency(1234.56)
      expect(result).not.toContain(',')
      expect(result).not.toContain('.')
    })

    it('should handle string numbers', () => {
      const result = formatCurrency('1234.56')
      expect(typeof result).toBe('string')
    })

    it('should handle custom currency', () => {
      const result = formatCurrency(1234.56, { currency: 'USD' })
      expect(result).toContain('$')
    })

    it('should handle custom locale', () => {
      const result = formatCurrency(1234.56, { locale: 'en-US', currency: 'USD' })
      expect(result).toContain('$')
    })

    it('should return string value for NaN input', () => {
      expect(formatCurrency('invalid')).toBe('invalid')
    })

    it('should handle zero', () => {
      const result = formatCurrency(0)
      expect(result).toBeDefined()
    })

    it('should handle negative values', () => {
      const result = formatCurrency(-1234.56)
      expect(result).toBeDefined()
      expect(result).toContain('-')
    })
  })

  describe('formatPercentage', () => {
    it('should format percentage with default decimals', () => {
      expect(formatPercentage(85.5)).toBe('85.5%')
    })

    it('should format percentage with custom decimals', () => {
      expect(formatPercentage(85.567, { decimals: 2 })).toBe('85.57%')
    })

    it('should return 0% for zero value', () => {
      expect(formatPercentage(0)).toBe('0%')
    })

    it('should handle string numbers', () => {
      expect(formatPercentage('85.5')).toBe('85.5%')
    })

    it('should handle integer percentages', () => {
      expect(formatPercentage(85)).toBe('85.0%')
    })

    it('should handle negative percentages', () => {
      expect(formatPercentage(-5.5)).toBe('-5.5%')
    })

    it('should return string value for NaN input', () => {
      expect(formatPercentage('invalid')).toBe('invalid')
    })

    it('should handle large percentages', () => {
      expect(formatPercentage(150.75)).toBe('150.8%')
    })

    it('should handle very small percentages', () => {
      expect(formatPercentage(0.123)).toBe('0.1%')
    })
  })

  describe('formatDate', () => {
    it('should format date string with default options', () => {
      const dateStr = '2024-01-15'
      const result = formatDate(dateStr)
      expect(result).toBeDefined()
      expect(typeof result).toBe('string')
      expect(result).not.toBe('N/A')
    })

    it('should format Date object', () => {
      const date = new Date('2024-01-15')
      const result = formatDate(date)
      expect(result).toBeDefined()
      expect(typeof result).toBe('string')
    })

    it('should return N/A for null input', () => {
      expect(formatDate(null)).toBe('N/A')
    })

    it('should return N/A for undefined input', () => {
      expect(formatDate(undefined)).toBe('N/A')
    })

    it('should return N/A for empty string', () => {
      expect(formatDate('')).toBe('N/A')
    })

    it('should return N/A for invalid date string', () => {
      expect(formatDate('invalid-date')).toBe('N/A')
    })

    it('should handle custom locale', () => {
      const dateStr = '2024-01-15'
      const result = formatDate(dateStr, { locale: 'en-US' })
      expect(result).toBeDefined()
      expect(result).not.toBe('N/A')
    })

    it('should handle dateStyle option', () => {
      const dateStr = '2024-01-15'
      const result = formatDate(dateStr, { dateStyle: 'long' })
      expect(result).toBeDefined()
      expect(result).not.toBe('N/A')
    })

    it('should handle timeStyle option', () => {
      const dateStr = '2024-01-15T10:30:00'
      const result = formatDate(dateStr, { timeStyle: 'short' })
      expect(result).toBeDefined()
      expect(result).not.toBe('N/A')
    })
  })

  describe('formatDateTime', () => {
    it('should format date and time', () => {
      const dateStr = '2024-01-15T10:30:00'
      const result = formatDateTime(dateStr)
      expect(result).toBeDefined()
      expect(typeof result).toBe('string')
      expect(result).not.toBe('N/A')
    })

    it('should format Date object with time', () => {
      const date = new Date('2024-01-15T10:30:00')
      const result = formatDateTime(date)
      expect(result).toBeDefined()
      expect(result).not.toBe('N/A')
    })

    it('should return N/A for invalid date', () => {
      expect(formatDateTime('invalid')).toBe('N/A')
    })

    it('should handle custom options', () => {
      const dateStr = '2024-01-15T10:30:00'
      const result = formatDateTime(dateStr, { locale: 'en-US' })
      expect(result).toBeDefined()
      expect(result).not.toBe('N/A')
    })
  })

  describe('formatChange', () => {
    it('should format positive change with sign', () => {
      const result = formatChange(5.5)
      expect(result).toContain('+')
      expect(result).toContain('%')
    })

    it('should format negative change', () => {
      const result = formatChange(-3.2)
      expect(result).toContain('-')
      expect(result).toContain('%')
    })

    it('should format zero change', () => {
      const result = formatChange(0)
      expect(result).toBe('0%')
    })

    it('should format change without sign when showSign is false', () => {
      const result = formatChange(5.5, { showSign: false })
      expect(result).not.toContain('+')
      expect(result).toContain('%')
    })

    it('should handle string numbers', () => {
      const result = formatChange('5.5')
      expect(result).toBeDefined()
      expect(result).toContain('%')
    })

    it('should return string value for NaN input', () => {
      expect(formatChange('invalid')).toBe('invalid')
    })

    it('should format large positive changes', () => {
      const result = formatChange(150.75)
      expect(result).toContain('+')
      expect(result).toContain('%')
    })

    it('should format small changes', () => {
      const result = formatChange(0.1)
      expect(result).toBeDefined()
    })
  })

  describe('formatFileSize', () => {
    it('should format bytes', () => {
      expect(formatFileSize(512)).toBe('512 B')
    })

    it('should format kilobytes', () => {
      expect(formatFileSize(1024)).toBe('1 KB')
    })

    it('should format megabytes', () => {
      expect(formatFileSize(1048576)).toBe('1 MB')
    })

    it('should format gigabytes', () => {
      expect(formatFileSize(1073741824)).toBe('1 GB')
    })

    it('should format terabytes', () => {
      expect(formatFileSize(1099511627776)).toBe('1 TB')
    })

    it('should handle decimal sizes', () => {
      const result = formatFileSize(1536)
      expect(result).toContain('KB')
    })

    it('should return 0 B for zero bytes', () => {
      expect(formatFileSize(0)).toBe('0 B')
    })

    it('should return 0 B for null input', () => {
      expect(formatFileSize(null)).toBe('0 B')
    })

    it('should handle large file sizes', () => {
      const result = formatFileSize(5368709120)
      expect(result).toContain('GB')
    })

    it('should round to 2 decimal places', () => {
      const result = formatFileSize(1536)
      // Use bounded quantifier to prevent catastrophic backtracking
      // Limit digits before decimal point to prevent DoS vulnerability
      // Match: 1-20 digits, a dot, then 1-2 digits
      expect(result).toMatch(/\d{1,20}\.\d{1,2}/)
    })
  })

  describe('formatDuration', () => {
    it('should format seconds only', () => {
      expect(formatDuration(30)).toBe('30s')
    })

    it('should format minutes and seconds', () => {
      expect(formatDuration(90)).toBe('1m 30s')
    })

    it('should format minutes only when seconds are zero', () => {
      expect(formatDuration(120)).toBe('2m')
    })

    it('should return 0s for zero seconds', () => {
      expect(formatDuration(0)).toBe('0s')
    })

    it('should return 0s for null input', () => {
      expect(formatDuration(null)).toBe('0s')
    })

    it('should handle single minute', () => {
      expect(formatDuration(60)).toBe('1m')
    })

    it('should handle multiple minutes', () => {
      expect(formatDuration(185)).toBe('3m 5s')
    })

    it('should handle large durations', () => {
      expect(formatDuration(3661)).toBe('61m 1s')
    })

    it('should handle exactly 60 seconds', () => {
      expect(formatDuration(60)).toBe('1m')
    })

    it('should handle 59 seconds', () => {
      expect(formatDuration(59)).toBe('59s')
    })
  })

  describe('parseChange', () => {
    it('should parse positive change string', () => {
      expect(parseChange('+5%')).toBe(5)
    })

    it('should parse negative change string', () => {
      expect(parseChange('-3.2%')).toBe(-3.2)
    })

    it('should parse change string without sign', () => {
      expect(parseChange('5.5%')).toBe(5.5)
    })

    it('should parse decimal change string', () => {
      expect(parseChange('+12.34%')).toBe(12.34)
    })

    it('should return 0 for null input', () => {
      expect(parseChange(null)).toBe(0)
    })

    it('should return 0 for undefined input', () => {
      expect(parseChange(undefined)).toBe(0)
    })

    it('should return 0 for empty string', () => {
      expect(parseChange('')).toBe(0)
    })

    it('should return 0 for invalid string', () => {
      expect(parseChange('invalid')).toBe(0)
    })

    it('should return 0 for non-string input', () => {
      expect(parseChange(123)).toBe(0)
    })

    it('should parse integer change', () => {
      expect(parseChange('+10%')).toBe(10)
    })

    it('should handle change without percentage symbol', () => {
      expect(parseChange('+5')).toBe(5)
    })

    it('should handle negative without percentage symbol', () => {
      expect(parseChange('-3')).toBe(-3)
    })

    it('should handle string with spaces', () => {
      expect(parseChange(' +5% ')).toBe(5)
    })

    it('should return 0 for string without numbers', () => {
      expect(parseChange('abc%')).toBe(0)
    })
  })
})

