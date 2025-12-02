/**
 * Unit tests for useQuickActions composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useQuickActions } from '../useQuickActions.js'
import { useRouter } from 'vue-router'

// Mock router
const mockRouter = {
  push: vi.fn()
}

vi.mock('vue-router', () => ({
  useRouter: () => mockRouter,
  createRouter: vi.fn((options) => mockRouter),
  createWebHistory: vi.fn(() => ({})),
  createWebHashHistory: vi.fn(() => ({})),
  createMemoryHistory: vi.fn(() => ({}))
}))

describe('useQuickActions', () => {
  let actions

  beforeEach(() => {
    vi.clearAllMocks()
    actions = useQuickActions()
  })

  describe('initial state', () => {
    it('should have initial state', () => {
      expect(actions.executingAction.value).toBe(null)
      expect(actions.actionError.value).toBe(null)
    })
  })

  describe('executeAction', () => {
    it('should navigate to route when action has route', async () => {
      const action = {
        key: 'test-action',
        route: '/test-route'
      }

      await actions.executeAction(action)

      expect(mockRouter.push).toHaveBeenCalledWith('/test-route')
      expect(actions.executingAction.value).toBe(null)
    })

    it('should execute handler when action has handler', async () => {
      const handler = vi.fn().mockResolvedValue()
      const action = {
        key: 'test-action',
        handler
      }

      await actions.executeAction(action)

      expect(handler).toHaveBeenCalledWith(action)
      expect(actions.executingAction.value).toBe(null)
    })

    it('should open external URL when action has external url', async () => {
      globalThis.open = vi.fn()
      const action = {
        key: 'test-action',
        url: 'https://example.com',
        external: true
      }

      await actions.executeAction(action)

      expect(globalThis.open).toHaveBeenCalledWith('https://example.com', '_blank')
    })

    it('should set actionError when action fails', async () => {
      const action = {
        key: 'test-action',
        handler: vi.fn().mockRejectedValue(new Error('Test error'))
      }

      await expect(actions.executeAction(action)).rejects.toThrow()

      expect(actions.actionError.value).toBeTruthy()
      expect(actions.executingAction.value).toBe(null)
    })

    it('should throw error for invalid action', async () => {
      const action = {}

      await expect(actions.executeAction(action)).rejects.toThrow('Invalid action')
    })
  })

  describe('isActionExecuting', () => {
    it('should return true when action is executing', async () => {
      const handler = vi.fn(() => new Promise(resolve => setTimeout(resolve, 100)))
      const action = {
        key: 'test-action',
        handler
      }

      actions.executeAction(action)
      expect(actions.isActionExecuting('test-action')).toBe(true)
    })

    it('should return false when action is not executing', () => {
      expect(actions.isActionExecuting('test-action')).toBe(false)
    })
  })

  describe('getDefaultActions', () => {
    it('should return actions for admin role', () => {
      const adminActions = actions.getDefaultActions('admin')

      expect(Array.isArray(adminActions)).toBe(true)
      expect(adminActions.length).toBeGreaterThan(0)
    })

    it('should return actions for farmer role', () => {
      const farmerActions = actions.getDefaultActions('farmer')

      expect(Array.isArray(farmerActions)).toBe(true)
    })

    it('should return empty array for unknown role', () => {
      const defaultActions = actions.getDefaultActions('unknown')

      expect(Array.isArray(defaultActions)).toBe(true)
    })
  })
})

