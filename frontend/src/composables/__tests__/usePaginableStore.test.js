/**
 * Unit tests for usePaginableStore composable
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { usePaginableStore } from '../usePaginableStore.js'

describe('usePaginableStore', () => {
  let paginableStore

  beforeEach(() => {
    paginableStore = usePaginableStore()
  })

  describe('initial state', () => {
    it('should have initial pagination state', () => {
      expect(paginableStore.currentPage.value).toBe(1)
      expect(paginableStore.itemsPerPage.value).toBe(10)
      expect(paginableStore.totalPages.value).toBe(1)
      expect(paginableStore.totalItems.value).toBe(0)
    })

    it('should accept custom initial values', () => {
      const store = usePaginableStore({
        initialPage: 2,
        initialPageSize: 20
      })
      
      expect(store.currentPage.value).toBe(2)
      expect(store.itemsPerPage.value).toBe(20)
    })
  })

  describe('computed properties', () => {
    it('should compute hasNextPage', () => {
      paginableStore.currentPage.value = 1
      paginableStore.totalPages.value = 3
      
      expect(paginableStore.hasNextPage.value).toBe(true)
      
      paginableStore.currentPage.value = 3
      expect(paginableStore.hasNextPage.value).toBe(false)
    })

    it('should compute hasPreviousPage', () => {
      paginableStore.currentPage.value = 1
      expect(paginableStore.hasPreviousPage.value).toBe(false)
      
      paginableStore.currentPage.value = 2
      expect(paginableStore.hasPreviousPage.value).toBe(true)
    })
  })

  describe('updatePagination', () => {
    it('should update from API response with count', () => {
      const response = {
        count: 100,
        page: 2,
        page_size: 10
      }
      
      paginableStore.updatePagination(response)
      
      expect(paginableStore.totalItems.value).toBe(100)
      expect(paginableStore.totalPages.value).toBe(10)
      expect(paginableStore.currentPage.value).toBe(2)
    })

    it('should update from API response with total', () => {
      const response = {
        total: 50,
        page: 1
      }
      
      paginableStore.updatePagination(response)
      
      expect(paginableStore.totalItems.value).toBe(50)
    })
  })

  describe('nextPage', () => {
    it('should go to next page', () => {
      paginableStore.totalPages.value = 3
      paginableStore.currentPage.value = 1
      
      paginableStore.nextPage()
      
      expect(paginableStore.currentPage.value).toBe(2)
    })

    it('should not go beyond last page', () => {
      paginableStore.totalPages.value = 3
      paginableStore.currentPage.value = 3
      
      paginableStore.nextPage()
      
      expect(paginableStore.currentPage.value).toBe(3)
    })
  })

  describe('previousPage', () => {
    it('should go to previous page', () => {
      paginableStore.currentPage.value = 2
      
      paginableStore.previousPage()
      
      expect(paginableStore.currentPage.value).toBe(1)
    })

    it('should not go below first page', () => {
      paginableStore.currentPage.value = 1
      
      paginableStore.previousPage()
      
      expect(paginableStore.currentPage.value).toBe(1)
    })
  })

  describe('goToPage', () => {
    it('should go to specific page', () => {
      paginableStore.totalPages.value = 5
      
      paginableStore.goToPage(3)
      
      expect(paginableStore.currentPage.value).toBe(3)
    })

    it('should not go to invalid page', () => {
      paginableStore.totalPages.value = 5
      paginableStore.currentPage.value = 2
      
      paginableStore.goToPage(10)
      
      expect(paginableStore.currentPage.value).toBe(2)
    })
  })

  describe('setPageSize', () => {
    it('should set page size', () => {
      paginableStore.setPageSize(20)
      
      expect(paginableStore.itemsPerPage.value).toBe(20)
      expect(paginableStore.currentPage.value).toBe(1) // Reset to first page
    })
  })

  describe('resetPagination', () => {
    it('should reset pagination', () => {
      paginableStore.currentPage.value = 5
      paginableStore.itemsPerPage.value = 20
      
      paginableStore.resetPagination()
      
      expect(paginableStore.currentPage.value).toBe(1)
      expect(paginableStore.itemsPerPage.value).toBe(10)
    })
  })
})

