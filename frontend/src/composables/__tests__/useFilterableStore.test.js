/**
 * Unit tests for useFilterableStore composable
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { useFilterableStore } from '../useFilterableStore.js'

describe('useFilterableStore', () => {
  let filterableStore

  beforeEach(() => {
    filterableStore = useFilterableStore()
  })

  describe('initial state', () => {
    it('should have initial empty filters', () => {
      expect(filterableStore.filters).toEqual({})
    })

    it('should accept initial filters', () => {
      const initialFilters = { status: 'active', type: 'user' }
      const store = useFilterableStore({ initialFilters })
      
      expect(store.filters.status).toBe('active')
      expect(store.filters.type).toBe('user')
    })
  })

  describe('setFilter', () => {
    it('should set filter value', () => {
      filterableStore.setFilter('status', 'active')
      
      expect(filterableStore.filters.status).toBe('active')
    })
  })

  describe('getFilter', () => {
    it('should get filter value', () => {
      filterableStore.setFilter('status', 'active')
      
      expect(filterableStore.getFilter('status')).toBe('active')
    })

    it('should return undefined for non-existent filter', () => {
      expect(filterableStore.getFilter('nonexistent')).toBeUndefined()
    })
  })

  describe('applyFilters', () => {
    it('should filter items by string value', () => {
      const items = [
        { name: 'Item 1', status: 'active' },
        { name: 'Item 2', status: 'inactive' },
        { name: 'Item 3', status: 'active' }
      ]

      filterableStore.setFilter('status', 'active')
      const filtered = filterableStore.applyFilters(items)

      expect(filtered).toHaveLength(2)
      expect(filtered[0].name).toBe('Item 1')
    })

    it('should filter items by array value', () => {
      const items = [
        { id: 1, type: 'a' },
        { id: 2, type: 'b' },
        { id: 3, type: 'a' }
      ]

      filterableStore.setFilter('type', ['a'])
      const filtered = filterableStore.applyFilters(items)

      expect(filtered).toHaveLength(2)
    })

    const createCustomFilterFn = () => {
      return (items, filters) => {
        return items.filter(item => item.value > filters.minValue)
      }
    }

    it('should use custom filter function', () => {
      const items = [{ value: 1 }, { value: 2 }, { value: 3 }]
      const customFilterFn = createCustomFilterFn()

      const store = useFilterableStore({ filterFn: customFilterFn })
      store.setFilter('minValue', 2)
      
      const filtered = store.applyFilters(items)

      expect(filtered).toHaveLength(1)
      expect(filtered[0].value).toBe(3)
    })

    it('should return empty array for invalid input', () => {
      const filtered = filterableStore.applyFilters(null)
      
      expect(filtered).toEqual([])
    })
  })

  describe('clearFilters', () => {
    it('should clear all filters', () => {
      const initialFilters = { status: 'active' }
      const store = useFilterableStore({ initialFilters })
      
      store.setFilter('status', 'inactive')
      store.clearFilters()

      expect(store.filters.status).toBe('active')
    })
  })

  describe('clearFilter', () => {
    it('should clear specific filter', () => {
      const initialFilters = { status: 'active', type: 'user' }
      const store = useFilterableStore({ initialFilters })
      
      store.setFilter('status', 'inactive')
      store.clearFilter('status')

      expect(store.filters.status).toBe('active')
    })
  })

  describe('hasActiveFilters', () => {
    it('should return false when no filters active', () => {
      expect(filterableStore.hasActiveFilters.value).toBe(false)
    })

    it('should return true when filter is active', () => {
      filterableStore.setFilter('status', 'active')
      
      expect(filterableStore.hasActiveFilters.value).toBe(true)
    })
  })
})

