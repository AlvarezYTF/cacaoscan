/**
 * Unit tests for useDateFormatting composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  formatDateTime,
  formatDate,
  formatRelativeTime,
  formatDuration,
  getMinBirthdate,
  getMaxBirthdate,
  calculateAge,
  validateBirthdateRange,
  formatDimensions,
  useDateFormatting,
  useBirthdateRange
} from '../useDateFormatting.js'

describe('useDateFormatting', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('formatDateTime', () => {
    it('should format date and time', () => {
      const date = new Date('2024-01-15T10:30:00')
      const result = formatDateTime(date)
      
      expect(result).toBeTruthy()
      expect(typeof result).toBe('string')
    })

    it('should return N/A for null', () => {
      expect(formatDateTime(null)).toBe('N/A')
    })

    it('should return N/A for undefined', () => {
      expect(formatDateTime(undefined)).toBe('N/A')
    })

    it('should handle date string', () => {
      const result = formatDateTime('2024-01-15T10:30:00')
      
      expect(result).toBeTruthy()
      expect(result).not.toBe('N/A')
    })

    it('should return N/A for invalid date', () => {
      expect(formatDateTime('invalid-date')).toBe('N/A')
    })
  })

  describe('formatDate', () => {
    it('should format date without time', () => {
      const date = new Date('2024-01-15T10:30:00')
      const result = formatDate(date)
      
      expect(result).toBeTruthy()
      expect(typeof result).toBe('string')
    })

    it('should return N/A for null', () => {
      expect(formatDate(null)).toBe('N/A')
    })

    it('should handle date string', () => {
      const result = formatDate('2024-01-15')
      
      expect(result).toBeTruthy()
      expect(result).not.toBe('N/A')
    })
  })

  describe('formatRelativeTime', () => {
    it('should format recent time', () => {
      const now = new Date()
      const fiveMinutesAgo = new Date(now.getTime() - 5 * 60000)
      
      const result = formatRelativeTime(fiveMinutesAgo)
      
      expect(result).toContain('minuto')
    })

    it('should return "Hace un momento" for very recent', () => {
      const now = new Date()
      const thirtySecondsAgo = new Date(now.getTime() - 30 * 1000)
      
      const result = formatRelativeTime(thirtySecondsAgo)
      
      expect(result).toBe('Hace un momento')
    })

    it('should format hours ago', () => {
      const now = new Date()
      const twoHoursAgo = new Date(now.getTime() - 2 * 3600000)
      
      const result = formatRelativeTime(twoHoursAgo)
      
      expect(result).toContain('hora')
    })

    it('should format days ago', () => {
      const now = new Date()
      const threeDaysAgo = new Date(now.getTime() - 3 * 86400000)
      
      const result = formatRelativeTime(threeDaysAgo)
      
      expect(result).toContain('día')
    })

    it('should return formatted date for old dates', () => {
      const oldDate = new Date('2020-01-01')
      
      const result = formatRelativeTime(oldDate)
      
      expect(result).toBeTruthy()
      expect(result).not.toContain('Hace')
    })

    it('should return N/A for null', () => {
      expect(formatRelativeTime(null)).toBe('N/A')
    })
  })

  describe('formatDuration', () => {
    it('should format duration with hours', () => {
      expect(formatDuration('1:23:45')).toContain('1h')
      expect(formatDuration('1:23:45')).toContain('23m')
    })

    it('should format duration with minutes only', () => {
      expect(formatDuration('0:23:45')).toContain('23m')
      expect(formatDuration('0:23:45')).toContain('45s')
    })

    it('should format duration with seconds only', () => {
      expect(formatDuration('0:0:45')).toContain('45s')
    })

    it('should return N/A for null', () => {
      expect(formatDuration(null)).toBe('N/A')
    })

    it('should return original string for invalid format', () => {
      expect(formatDuration('invalid')).toBe('invalid')
    })
  })

  describe('getMinBirthdate', () => {
    it('should return date 120 years ago', () => {
      const minDate = getMinBirthdate()
      
      expect(minDate).toBeTruthy()
      expect(typeof minDate).toBe('string')
      expect(minDate).toMatch(/^\d{4}-\d{2}-\d{2}$/)
    })
  })

  describe('getMaxBirthdate', () => {
    it('should return date 14 years ago', () => {
      const maxDate = getMaxBirthdate()
      
      expect(maxDate).toBeTruthy()
      expect(typeof maxDate).toBe('string')
      expect(maxDate).toMatch(/^\d{4}-\d{2}-\d{2}$/)
    })
  })

  describe('calculateAge', () => {
    it('should calculate age correctly', () => {
      const today = new Date()
      const birthYear = today.getFullYear() - 25
      const birthdate = new Date(birthYear, today.getMonth(), today.getDate())
      
      const age = calculateAge(birthdate)
      
      expect(age).toBe(25)
    })

    it('should handle age adjustment for upcoming birthday', () => {
      const today = new Date()
      const birthYear = today.getFullYear() - 25
      // Birthday hasn't occurred this year yet
      const birthdate = new Date(birthYear, today.getMonth() + 1, today.getDate())
      
      const age = calculateAge(birthdate)
      
      expect(age).toBe(24)
    })

    it('should return null for invalid date', () => {
      expect(calculateAge('invalid')).toBe(null)
    })

    it('should return null for null input', () => {
      expect(calculateAge(null)).toBe(null)
    })
  })

  describe('validateBirthdateRange', () => {
    it('should validate valid birthdate', () => {
      const today = new Date()
      const birthYear = today.getFullYear() - 25
      const birthdate = new Date(birthYear, today.getMonth(), today.getDate())
      
      const result = validateBirthdateRange(birthdate)
      
      expect(result.isValid).toBe(true)
      expect(result.message).toBe(null)
    })

    it('should reject birthdate for person too young', () => {
      const today = new Date()
      const birthYear = today.getFullYear() - 10 // 10 years old
      const birthdate = new Date(birthYear, today.getMonth(), today.getDate())
      
      const result = validateBirthdateRange(birthdate)
      
      expect(result.isValid).toBe(false)
      expect(result.message).toContain('14 años')
    })

    it('should reject birthdate for person too old', () => {
      const today = new Date()
      const birthYear = today.getFullYear() - 130 // 130 years old
      const birthdate = new Date(birthYear, today.getMonth(), today.getDate())
      
      const result = validateBirthdateRange(birthdate)
      
      expect(result.isValid).toBe(false)
      expect(result.message).toContain('120 años')
    })

    it('should return error for null birthdate', () => {
      const result = validateBirthdateRange(null)
      
      expect(result.isValid).toBe(false)
      expect(result.message).toBeTruthy()
    })

    it('should return error for invalid date', () => {
      const result = validateBirthdateRange('invalid-date')
      
      expect(result.isValid).toBe(false)
      expect(result.message).toBeTruthy()
    })
  })

  describe('formatDimensions', () => {
    it('should format dimensions correctly', () => {
      const prediction = {
        width: 10.5,
        height: 12.3,
        thickness: 5.2
      }
      
      const result = formatDimensions(prediction)
      
      expect(result).toContain('10.50')
      expect(result).toContain('12.30')
      expect(result).toContain('5.20')
      expect(result).toContain('mm')
    })

    it('should use custom formatter function', () => {
      const prediction = {
        width: 10.5,
        height: 12.3,
        thickness: 5.2
      }
      
      const customFormatter = (value) => Math.round(value).toString()
      const result = formatDimensions(prediction, customFormatter)
      
      expect(result).toContain('11')
      expect(result).toContain('12')
      expect(result).toContain('5')
    })

    it('should return N/A for null prediction', () => {
      expect(formatDimensions(null)).toBe('N/A')
    })
  })

  describe('useDateFormatting', () => {
    it('should return all formatting functions', () => {
      const formatting = useDateFormatting()
      
      expect(typeof formatting.formatDateTime).toBe('function')
      expect(typeof formatting.formatDate).toBe('function')
      expect(typeof formatting.formatRelativeTime).toBe('function')
      expect(typeof formatting.formatDuration).toBe('function')
      expect(typeof formatting.calculateAge).toBe('function')
      expect(typeof formatting.validateBirthdateRange).toBe('function')
    })
  })

  describe('useBirthdateRange', () => {
    it('should return computed birthdate range', () => {
      const range = useBirthdateRange()
      
      expect(range.minBirthdate.value).toBeTruthy()
      expect(range.maxBirthdate.value).toBeTruthy()
    })
  })
})

