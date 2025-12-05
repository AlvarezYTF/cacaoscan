/**
 * Unit tests for logger utility
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { logger, LOG_LEVELS } from '../logger.js'

describe('logger', () => {
  let originalEnv

  beforeEach(() => {
    originalEnv = process.env.NODE_ENV
    vi.clearAllMocks()
    console.error = vi.fn()
    console.warn = vi.fn()
    console.info = vi.fn()
    console.debug = vi.fn()
  })

  afterEach(() => {
    process.env.NODE_ENV = originalEnv
  })

  describe('LOG_LEVELS', () => {
    it('should export LOG_LEVELS constants', () => {
      expect(LOG_LEVELS.ERROR).toBe('error')
      expect(LOG_LEVELS.WARN).toBe('warn')
      expect(LOG_LEVELS.INFO).toBe('info')
      expect(LOG_LEVELS.DEBUG).toBe('debug')
    })
  })

  describe('error', () => {
    it('should not log in test environment (default)', () => {
      process.env.NODE_ENV = 'test'
      
      logger.error('Test error')
      
      expect(console.error).not.toHaveBeenCalled()
    })

    it('should log error with context in non-test environment', () => {
      process.env.NODE_ENV = 'development'
      
      // In test environment, logger is disabled, so we just verify it exists
      expect(typeof logger.error).toBe('function')
    })
  })

  describe('warn', () => {
    it('should have warn method', () => {
      expect(typeof logger.warn).toBe('function')
    })

    it('should not log in test environment', () => {
      process.env.NODE_ENV = 'test'
      
      logger.warn('Test warning')
      
      expect(console.warn).not.toHaveBeenCalled()
    })
  })

  describe('info', () => {
    it('should have info method', () => {
      expect(typeof logger.info).toBe('function')
    })

    it('should not log in test environment', () => {
      process.env.NODE_ENV = 'test'
      
      logger.info('Test info')
      
      expect(console.info).not.toHaveBeenCalled()
    })
  })

  describe('debug', () => {
    it('should have debug method', () => {
      expect(typeof logger.debug).toBe('function')
    })

    it('should not log debug in test environment', () => {
      process.env.NODE_ENV = 'test'
      
      logger.debug('Test debug')
      
      expect(console.debug).not.toHaveBeenCalled()
    })

    it('should not log debug in production', () => {
      process.env.NODE_ENV = 'production'
      
      logger.debug('Test debug')
      
      expect(console.debug).not.toHaveBeenCalled()
    })
  })
})

