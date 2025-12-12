/**
 * Unit tests for useRecentActivity composable
 */

import { describe, it, expect, vi } from 'vitest'
import { useRecentActivity } from '../useRecentActivity.js'

describe('useRecentActivity', () => {
  describe('initial state', () => {
    it('should have initial state', () => {
      const activity = useRecentActivity()
      
      expect(activity.activities.value).toEqual([])
      expect(activity.loading.value).toBe(false)
      expect(activity.error.value).toBe(null)
    })

    it('should accept custom limit', () => {
      const activity = useRecentActivity({ limit: 5 })
      
      expect(activity.recentActivities.value).toBeDefined()
    })
  })

  describe('fetchActivities', () => {
    it('should fetch activities successfully', async () => {
      const fetchFn = vi.fn().mockResolvedValue([
        { id: 1, action: 'upload' },
        { id: 2, action: 'delete' }
      ])
      const activity = useRecentActivity({ fetchFn })

      await activity.fetchActivities()

      expect(fetchFn).toHaveBeenCalled()
      expect(activity.activities.value).toHaveLength(2)
      expect(activity.loading.value).toBe(false)
    })

    it('should handle error', async () => {
      const fetchFn = vi.fn().mockRejectedValue(new Error('Network error'))
      const activity = useRecentActivity({ fetchFn })

      await expect(activity.fetchActivities()).rejects.toThrow()

      expect(activity.error.value).toBeTruthy()
      expect(activity.loading.value).toBe(false)
    })

    it('should throw error when fetchFn not provided', async () => {
      const activity = useRecentActivity()

      await expect(activity.fetchActivities()).rejects.toThrow('fetchFn is required')
    })
  })

  describe('addActivity', () => {
    it('should add activity to beginning', () => {
      const activity = useRecentActivity()
      const newActivity = { id: 1, action: 'test' }

      activity.addActivity(newActivity)

      expect(activity.activities.value[0]).toEqual(newActivity)
    })

    it('should limit activities to max', () => {
      const activity = useRecentActivity({ limit: 5 })
      
      // Add more than limit * 2
      for (let i = 0; i < 15; i++) {
        activity.addActivity({ id: i, action: 'test' })
      }

      expect(activity.activities.value.length).toBeLessThanOrEqual(10) // limit * 2
    })
  })

  describe('removeActivity', () => {
    it('should remove activity by id', () => {
      const activity = useRecentActivity()
      activity.activities.value = [
        { id: 1, action: 'test1' },
        { id: 2, action: 'test2' }
      ]

      activity.removeActivity(1)

      expect(activity.activities.value).toHaveLength(1)
      expect(activity.activities.value[0].id).toBe(2)
    })
  })

  describe('clearActivities', () => {
    it('should clear all activities', () => {
      const activity = useRecentActivity()
      activity.activities.value = [
        { id: 1, action: 'test1' },
        { id: 2, action: 'test2' }
      ]

      activity.clearActivities()

      expect(activity.activities.value).toHaveLength(0)
      expect(activity.error.value).toBe(null)
    })
  })

  describe('recentActivities computed', () => {
    it('should limit to specified limit', () => {
      const activity = useRecentActivity({ limit: 2 })
      activity.activities.value = [
        { id: 1 },
        { id: 2 },
        { id: 3 }
      ]

      expect(activity.recentActivities.value).toHaveLength(2)
    })
  })

  describe('hasActivities computed', () => {
    it('should return false when no activities', () => {
      const activity = useRecentActivity()
      expect(activity.hasActivities.value).toBe(false)
    })

    it('should return true when activities exist', () => {
      const activity = useRecentActivity()
      activity.activities.value = [{ id: 1 }]
      expect(activity.hasActivities.value).toBe(true)
    })
  })

  describe('fetchActivities', () => {
    it('should handle array response', async () => {
      const fetchFn = vi.fn().mockResolvedValue([
        { id: 1, action: 'upload' },
        { id: 2, action: 'delete' }
      ])
      const activity = useRecentActivity({ fetchFn })

      await activity.fetchActivities()

      expect(activity.activities.value).toHaveLength(2)
      expect(activity.lastFetch.value).toBeInstanceOf(Date)
    })

    it('should handle object with data property', async () => {
      const fetchFn = vi.fn().mockResolvedValue({
        data: [{ id: 1 }, { id: 2 }]
      })
      const activity = useRecentActivity({ fetchFn })

      await activity.fetchActivities()

      expect(activity.activities.value).toHaveLength(2)
    })

    it('should handle object with results property', async () => {
      const fetchFn = vi.fn().mockResolvedValue({
        results: [{ id: 1 }, { id: 2 }]
      })
      const activity = useRecentActivity({ fetchFn })

      await activity.fetchActivities()

      expect(activity.activities.value).toHaveLength(2)
    })

    it('should handle error with response data', async () => {
      const error = {
        response: {
          data: {
            detail: 'Custom error message'
          }
        },
        message: 'Network error'
      }
      const fetchFn = vi.fn().mockRejectedValue(error)
      const activity = useRecentActivity({ fetchFn })

      await expect(activity.fetchActivities()).rejects.toEqual(error)
      expect(activity.error.value).toBe('Custom error message')
    })

    it('should handle error with message only', async () => {
      const error = { message: 'Network error' }
      const fetchFn = vi.fn().mockRejectedValue(error)
      const activity = useRecentActivity({ fetchFn })

      await expect(activity.fetchActivities()).rejects.toEqual(error)
      expect(activity.error.value).toBe('Network error')
    })

    it('should handle error with generic message', async () => {
      const error = {}
      const fetchFn = vi.fn().mockRejectedValue(error)
      const activity = useRecentActivity({ fetchFn })

      await expect(activity.fetchActivities()).rejects.toEqual(error)
      expect(activity.error.value).toBe('Error al cargar actividades recientes')
    })

    it('should pass limit to fetchFn', async () => {
      const fetchFn = vi.fn().mockResolvedValue([])
      const activity = useRecentActivity({ limit: 5, fetchFn })

      await activity.fetchActivities({ custom: 'param' })

      expect(fetchFn).toHaveBeenCalledWith({ custom: 'param', limit: 5 })
    })
  })

  describe('addActivity', () => {
    it('should not add null activity', () => {
      const activity = useRecentActivity()
      activity.addActivity(null)
      expect(activity.activities.value).toHaveLength(0)
    })

    it('should not add undefined activity', () => {
      const activity = useRecentActivity()
      activity.addActivity(undefined)
      expect(activity.activities.value).toHaveLength(0)
    })
  })

  describe('removeActivity', () => {
    it('should not remove when activity not found', () => {
      const activity = useRecentActivity()
      activity.activities.value = [{ id: 1 }]
      
      activity.removeActivity(999)
      
      expect(activity.activities.value).toHaveLength(1)
    })
  })

  describe('formatActivity', () => {
    it('should format activity with all fields', () => {
      const activity = useRecentActivity()
      const input = {
        id: 1,
        title: 'Test Title',
        description: 'Test Description',
        timestamp: '2024-01-01',
        type: 'create',
        icon: 'test-icon',
        user: { id: 1, name: 'User' },
        link: '/test'
      }

      const formatted = activity.formatActivity(input)

      expect(formatted).toEqual({
        id: 1,
        title: 'Test Title',
        description: 'Test Description',
        timestamp: '2024-01-01',
        type: 'create',
        icon: 'test-icon',
        user: { id: 1, name: 'User' },
        link: '/test'
      })
    })

    it('should format activity with fallback fields', () => {
      const activity = useRecentActivity()
      const input = {
        id: 1,
        action: 'create',
        message: 'Test Message',
        created_at: '2024-01-01',
        action_type: 'info',
        usuario: { id: 1 },
        route: '/test'
      }

      const formatted = activity.formatActivity(input)

      expect(formatted.title).toBe('create')
      expect(formatted.description).toBe('Test Message')
      expect(formatted.timestamp).toBe('2024-01-01')
      expect(formatted.type).toBe('info')
      expect(formatted.user).toEqual({ id: 1 })
      expect(formatted.link).toBe('/test')
    })

    it('should format activity with date fallback', () => {
      const activity = useRecentActivity()
      const input = {
        id: 1,
        date: '2024-01-01'
      }

      const formatted = activity.formatActivity(input)

      expect(formatted.timestamp).toBe('2024-01-01')
    })

    it('should return null for null input', () => {
      const activity = useRecentActivity()
      expect(activity.formatActivity(null)).toBe(null)
    })

    it('should use default values when fields missing', () => {
      const activity = useRecentActivity()
      const input = { id: 1 }

      const formatted = activity.formatActivity(input)

      expect(formatted.title).toBe('Actividad')
      expect(formatted.description).toBe('')
      expect(formatted.type).toBe('info')
    })
  })

  describe('getDefaultIcon', () => {
    it('should return correct icon for create', () => {
      const activity = useRecentActivity()
      expect(activity.getDefaultIcon('create')).toBe('plus-circle')
    })

    it('should return correct icon for update', () => {
      const activity = useRecentActivity()
      expect(activity.getDefaultIcon('update')).toBe('pencil')
    })

    it('should return correct icon for delete', () => {
      const activity = useRecentActivity()
      expect(activity.getDefaultIcon('delete')).toBe('trash')
    })

    it('should return correct icon for view', () => {
      const activity = useRecentActivity()
      expect(activity.getDefaultIcon('view')).toBe('eye')
    })

    it('should return correct icon for login', () => {
      const activity = useRecentActivity()
      expect(activity.getDefaultIcon('login')).toBe('sign-in')
    })

    it('should return correct icon for logout', () => {
      const activity = useRecentActivity()
      expect(activity.getDefaultIcon('logout')).toBe('sign-out')
    })

    it('should return correct icon for upload', () => {
      const activity = useRecentActivity()
      expect(activity.getDefaultIcon('upload')).toBe('upload')
    })

    it('should return correct icon for download', () => {
      const activity = useRecentActivity()
      expect(activity.getDefaultIcon('download')).toBe('download')
    })

    it('should return correct icon for analysis', () => {
      const activity = useRecentActivity()
      expect(activity.getDefaultIcon('analysis')).toBe('chart-bar')
    })

    it('should return correct icon for prediction', () => {
      const activity = useRecentActivity()
      expect(activity.getDefaultIcon('prediction')).toBe('camera')
    })

    it('should return correct icon for info', () => {
      const activity = useRecentActivity()
      expect(activity.getDefaultIcon('info')).toBe('info-circle')
    })

    it('should return correct icon for success', () => {
      const activity = useRecentActivity()
      expect(activity.getDefaultIcon('success')).toBe('check-circle')
    })

    it('should return correct icon for warning', () => {
      const activity = useRecentActivity()
      expect(activity.getDefaultIcon('warning')).toBe('exclamation-triangle')
    })

    it('should return correct icon for error', () => {
      const activity = useRecentActivity()
      expect(activity.getDefaultIcon('error')).toBe('x-circle')
    })

    it('should return circle as fallback for unknown type', () => {
      const activity = useRecentActivity()
      expect(activity.getDefaultIcon('unknown')).toBe('circle')
    })
  })

  describe('groupByDate', () => {
    it('should group activities by date', () => {
      const activity = useRecentActivity()
      activity.activities.value = [
        { id: 1, timestamp: '2024-01-15T10:00:00Z' },
        { id: 2, timestamp: '2024-01-15T11:00:00Z' },
        { id: 3, created_at: '2024-01-16T10:00:00Z' },
        { id: 4, date: '2024-01-16T11:00:00Z' }
      ]

      const groups = activity.groupByDate()

      expect(Object.keys(groups).length).toBe(2)
      expect(groups[Object.keys(groups)[0]].length).toBe(2)
      expect(groups[Object.keys(groups)[1]].length).toBe(2)
    })

    it('should return empty object when no activities', () => {
      const activity = useRecentActivity()
      const groups = activity.groupByDate()
      expect(groups).toEqual({})
    })

    it('should handle activities with different date formats', () => {
      const activity = useRecentActivity()
      activity.activities.value = [
        { id: 1, timestamp: '2024-01-15' },
        { id: 2, created_at: '2024-01-15' },
        { id: 3, date: '2024-01-15' }
      ]

      const groups = activity.groupByDate()
      expect(Object.keys(groups).length).toBe(1)
    })
  })
})

