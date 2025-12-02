/**
 * Unit tests for useStoreBase composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useStoreBase } from '../useStoreBase.js'

describe('useStoreBase', () => {
  let storeBase

  beforeEach(() => {
    storeBase = useStoreBase()
  })

  describe('initial state', () => {
    it('should have initial state', () => {
      expect(storeBase.loading.value).toBe(false)
      expect(storeBase.error.value).toBe(null)
      expect(storeBase.isLoading.value).toBe(false)
      expect(storeBase.hasError.value).toBe(false)
    })
  })

  describe('setLoading', () => {
    it('should set loading state', () => {
      storeBase.setLoading(true)
      
      expect(storeBase.loading.value).toBe(true)
      expect(storeBase.isLoading.value).toBe(true)
    })

    it('should clear loading state', () => {
      storeBase.setLoading(true)
      storeBase.setLoading(false)
      
      expect(storeBase.loading.value).toBe(false)
    })
  })

  describe('setError', () => {
    it('should set error from string', () => {
      storeBase.setError('Test error')
      
      expect(storeBase.error.value).toBe('Test error')
      expect(storeBase.hasError.value).toBe(true)
    })

    it('should set error from Error object', () => {
      const error = new Error('Test error')
      storeBase.setError(error)
      
      expect(storeBase.error.value).toBe('Test error')
    })

    it('should clear error when null', () => {
      storeBase.setError('Test error')
      storeBase.setError(null)
      
      expect(storeBase.error.value).toBe(null)
      expect(storeBase.hasError.value).toBe(false)
    })
  })

  describe('clearError', () => {
    it('should clear error', () => {
      storeBase.setError('Test error')
      storeBase.clearError()
      
      expect(storeBase.error.value).toBe(null)
    })
  })

  describe('resetState', () => {
    it('should reset state to initial values', () => {
      storeBase.setLoading(true)
      storeBase.setError('Test error')
      
      storeBase.resetState()
      
      expect(storeBase.loading.value).toBe(false)
      expect(storeBase.error.value).toBe(null)
    })
  })

  describe('executeAction', () => {
    it('should execute action with loading state', async () => {
      const action = async () => {
        return 'success'
      }

      const result = await storeBase.executeAction(action)

      expect(result).toBe('success')
      expect(storeBase.loading.value).toBe(false)
    })

    it('should handle action errors', async () => {
      const action = async () => {
        throw new Error('Action failed')
      }

      await expect(storeBase.executeAction(action)).rejects.toThrow()
      expect(storeBase.error.value).toBeTruthy()
      expect(storeBase.loading.value).toBe(false)
    })

    it('should call onSuccess callback', async () => {
      const onSuccess = vi.fn()
      const action = async () => 'success'

      await storeBase.executeAction(action, { onSuccess })

      expect(onSuccess).toHaveBeenCalledWith('success')
    })

    it('should call onError callback', async () => {
      const onError = vi.fn()
      const error = new Error('Action failed')
      const action = async () => {
        throw error
      }

      await expect(storeBase.executeAction(action, { onError })).rejects.toThrow()

      expect(onError).toHaveBeenCalledWith(error)
    })
  })
})

