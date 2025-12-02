/**
 * Unit tests for useSearchFilter composable
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { nextTick } from 'vue'
import { useSearchFilter, useFilters } from '../useSearchFilter.js'

describe('useSearchFilter', () => {
  beforeEach(() => {
    vi.clearAllTimers()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  describe('initial state', () => {
    it('should have initial empty query', () => {
      const search = useSearchFilter()
      
      expect(search.searchQuery.value).toBe('')
      expect(search.debouncedQuery.value).toBe('')
    })

    it('should accept initial query', () => {
      const search = useSearchFilter({ initialQuery: 'test query' })
      
      expect(search.searchQuery.value).toBe('test query')
    })
  })

  describe('debouncing', () => {
    it('should debounce query updates', async () => {
      const search = useSearchFilter({ debounceMs: 300 })
      
      search.searchQuery.value = 'test'
      await nextTick()
      expect(search.debouncedQuery.value).toBe('')
      
      vi.advanceTimersByTime(300)
      
      expect(search.debouncedQuery.value).toBe('test')
    })

    it('should clear previous debounce timer', async () => {
      const search = useSearchFilter({ debounceMs: 300 })
      
      search.searchQuery.value = 'test'
      await nextTick()
      search.searchQuery.value = 'updated'
      await nextTick()
      
      vi.advanceTimersByTime(300)
      
      expect(search.debouncedQuery.value).toBe('updated')
      expect(search.debouncedQuery.value).not.toBe('test')
    })

    it('should use custom debounce delay', async () => {
      const search = useSearchFilter({ debounceMs: 500 })
      
      search.searchQuery.value = 'test'
      await nextTick()
      
      vi.advanceTimersByTime(300)
      expect(search.debouncedQuery.value).toBe('')
      
      vi.advanceTimersByTime(200)
      expect(search.debouncedQuery.value).toBe('test')
    })
  })

  describe('clearSearch', () => {
    it('should clear search query', () => {
      const search = useSearchFilter()
      
      search.searchQuery.value = 'test'
      search.clearSearch()
      
      expect(search.searchQuery.value).toBe('')
      expect(search.debouncedQuery.value).toBe('')
    })

    it('should clear debounce timer', () => {
      const search = useSearchFilter({ debounceMs: 300 })
      
      search.searchQuery.value = 'test'
      search.clearSearch()
      
      vi.advanceTimersByTime(300)
      
      expect(search.debouncedQuery.value).toBe('')
    })
  })

  describe('hasSearchQuery', () => {
    it('should return false for empty query', () => {
      const search = useSearchFilter()
      
      expect(search.hasSearchQuery.value).toBe(false)
    })

    it('should return false for whitespace only', () => {
      const search = useSearchFilter()
      search.searchQuery.value = '   '
      
      expect(search.hasSearchQuery.value).toBe(false)
    })

    it('should return true for non-empty query', () => {
      const search = useSearchFilter()
      search.searchQuery.value = 'test'
      
      expect(search.hasSearchQuery.value).toBe(true)
    })
  })
})

describe('useFilters', () => {
  describe('initial state', () => {
    it('should have initial filters', () => {
      const filters = useFilters({ status: 'active', type: 'all' })
      
      expect(filters.filters.value).toEqual({ status: 'active', type: 'all' })
    })

    it('should have empty filters by default', () => {
      const filters = useFilters()
      
      expect(filters.filters.value).toEqual({})
    })
  })

  describe('updateFilter', () => {
    it('should update single filter', () => {
      const filters = useFilters({ status: 'active' })
      
      filters.updateFilter('status', 'inactive')
      
      expect(filters.filters.value.status).toBe('inactive')
    })

    it('should add new filter', () => {
      const filters = useFilters({ status: 'active' })
      
      filters.updateFilter('type', 'new')
      
      expect(filters.filters.value.type).toBe('new')
      expect(filters.filters.value.status).toBe('active')
    })
  })

  describe('updateFilters', () => {
    it('should update multiple filters', () => {
      const filters = useFilters({ status: 'active', type: 'all' })
      
      filters.updateFilters({ status: 'inactive', category: 'new' })
      
      expect(filters.filters.value).toEqual({
        status: 'inactive',
        type: 'all',
        category: 'new'
      })
    })
  })

  describe('clearFilters', () => {
    it('should reset to initial filters', () => {
      const filters = useFilters({ status: 'active', type: 'all' })
      
      filters.updateFilter('status', 'inactive')
      filters.clearFilters()
      
      expect(filters.filters.value).toEqual({ status: 'active', type: 'all' })
    })
  })

  describe('resetFilter', () => {
    it('should reset specific filter to initial value', () => {
      const filters = useFilters({ status: 'active', type: 'all' })
      
      filters.updateFilter('status', 'inactive')
      filters.resetFilter('status')
      
      expect(filters.filters.value.status).toBe('active')
    })

    it('should not reset filter not in initial', () => {
      const filters = useFilters({ status: 'active' })
      
      filters.updateFilter('newFilter', 'value')
      filters.resetFilter('newFilter')
      
      expect(filters.filters.value.newFilter).toBe('value')
    })
  })

  describe('hasActiveFilters', () => {
    it('should return false when no filters changed', () => {
      const filters = useFilters({ status: 'active' })
      
      expect(filters.hasActiveFilters.value).toBe(false)
    })

    it('should return true when any filter changed', () => {
      const filters = useFilters({ status: 'active' })
      
      filters.updateFilter('status', 'inactive')
      
      expect(filters.hasActiveFilters.value).toBe(true)
    })
  })

  describe('activeFiltersCount', () => {
    it('should return 0 when no filters changed', () => {
      const filters = useFilters({ status: 'active', type: 'all' })
      
      expect(filters.activeFiltersCount.value).toBe(0)
    })

    it('should return count of changed filters', () => {
      const filters = useFilters({ status: 'active', type: 'all' })
      
      filters.updateFilter('status', 'inactive')
      
      expect(filters.activeFiltersCount.value).toBe(1)
      
      filters.updateFilter('type', 'new')
      
      expect(filters.activeFiltersCount.value).toBe(2)
    })
  })
})

