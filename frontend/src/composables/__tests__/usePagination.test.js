/**
 * Unit tests for usePagination composable
 */

import { describe, it, expect, vi } from 'vitest'
import { usePagination } from '../usePagination.js'

describe('usePagination', () => {
  describe('initial state', () => {
    it('should have default initial state', () => {
      const pagination = usePagination()
      
      expect(pagination.currentPage.value).toBe(1)
      expect(pagination.itemsPerPage.value).toBe(10)
      expect(pagination.totalItems.value).toBe(0)
      expect(pagination.maxVisible.value).toBe(5)
    })

    it('should accept custom initial values', () => {
      const pagination = usePagination({
        initialPage: 2,
        initialItemsPerPage: 20,
        maxVisiblePages: 7
      })
      
      expect(pagination.currentPage.value).toBe(2)
      expect(pagination.itemsPerPage.value).toBe(20)
      expect(pagination.maxVisible.value).toBe(7)
    })
  })

  describe('computed properties', () => {
    it('should compute totalPages correctly', () => {
      const pagination = usePagination()
      
      pagination.totalItems.value = 0
      expect(pagination.totalPages.value).toBe(1)
      
      pagination.totalItems.value = 25
      pagination.itemsPerPage.value = 10
      expect(pagination.totalPages.value).toBe(3)
    })

    it('should compute startItem correctly', () => {
      const pagination = usePagination()
      
      pagination.totalItems.value = 25
      pagination.itemsPerPage.value = 10
      pagination.currentPage.value = 1
      expect(pagination.startItem.value).toBe(1)
      
      pagination.currentPage.value = 2
      expect(pagination.startItem.value).toBe(11)
    })

    it('should compute endItem correctly', () => {
      const pagination = usePagination()
      
      pagination.totalItems.value = 25
      pagination.itemsPerPage.value = 10
      pagination.currentPage.value = 1
      expect(pagination.endItem.value).toBe(10)
      
      pagination.currentPage.value = 3
      expect(pagination.endItem.value).toBe(25)
    })

    it('should compute hasNextPage correctly', () => {
      const pagination = usePagination()
      
      pagination.totalItems.value = 25
      pagination.itemsPerPage.value = 10
      pagination.currentPage.value = 1
      expect(pagination.hasNextPage.value).toBe(true)
      
      pagination.currentPage.value = 3
      expect(pagination.hasNextPage.value).toBe(false)
    })

    it('should compute hasPreviousPage correctly', () => {
      const pagination = usePagination()
      
      pagination.currentPage.value = 1
      expect(pagination.hasPreviousPage.value).toBe(false)
      
      pagination.currentPage.value = 2
      expect(pagination.hasPreviousPage.value).toBe(true)
    })

    it('should compute visiblePages correctly', () => {
      const pagination = usePagination()
      
      pagination.totalItems.value = 50
      pagination.itemsPerPage.value = 10
      pagination.currentPage.value = 1
      
      const pages = pagination.visiblePages.value
      expect(pages.length).toBeGreaterThan(0)
      expect(pages).toContain(1)
    })
  })

  describe('navigation methods', () => {
    it('should go to specific page', () => {
      const pagination = usePagination()
      pagination.totalItems.value = 50
      pagination.itemsPerPage.value = 10
      
      const result = pagination.goToPage(3)
      
      expect(result).toBe(true)
      expect(pagination.currentPage.value).toBe(3)
    })

    it('should not go to invalid page', () => {
      const pagination = usePagination()
      pagination.totalItems.value = 50
      pagination.itemsPerPage.value = 10
      
      expect(pagination.goToPage(0)).toBe(false)
      expect(pagination.goToPage(10)).toBe(false)
      expect(pagination.currentPage.value).toBe(1)
    })

    it('should go to next page', () => {
      const pagination = usePagination()
      pagination.totalItems.value = 50
      pagination.itemsPerPage.value = 10
      
      pagination.nextPage()
      expect(pagination.currentPage.value).toBe(2)
    })

    it('should go to previous page', () => {
      const pagination = usePagination()
      pagination.totalItems.value = 50
      pagination.itemsPerPage.value = 10
      pagination.currentPage.value = 3
      
      pagination.previousPage()
      expect(pagination.currentPage.value).toBe(2)
    })

    it('should go to first page', () => {
      const pagination = usePagination()
      pagination.totalItems.value = 50
      pagination.itemsPerPage.value = 10
      pagination.currentPage.value = 3
      
      pagination.firstPage()
      expect(pagination.currentPage.value).toBe(1)
    })

    it('should go to last page', () => {
      const pagination = usePagination()
      pagination.totalItems.value = 50
      pagination.itemsPerPage.value = 10
      
      pagination.lastPage()
      expect(pagination.currentPage.value).toBe(5)
    })
  })

  describe('setItemsPerPage', () => {
    it('should set items per page and reset to first page', () => {
      const pagination = usePagination()
      pagination.currentPage.value = 3
      
      pagination.setItemsPerPage(20)
      
      expect(pagination.itemsPerPage.value).toBe(20)
      expect(pagination.currentPage.value).toBe(1)
    })

    it('should not set invalid items per page', () => {
      const pagination = usePagination()
      const original = pagination.itemsPerPage.value
      
      pagination.setItemsPerPage(0)
      expect(pagination.itemsPerPage.value).toBe(original)
      
      pagination.setItemsPerPage(-5)
      expect(pagination.itemsPerPage.value).toBe(original)
    })
  })

  describe('setTotalItems', () => {
    it('should set total items', () => {
      const pagination = usePagination()
      
      pagination.setTotalItems(100)
      
      expect(pagination.totalItems.value).toBe(100)
    })

    it('should adjust current page if beyond total', () => {
      const pagination = usePagination()
      pagination.totalItems.value = 50
      pagination.itemsPerPage.value = 10
      pagination.currentPage.value = 5
      
      pagination.setTotalItems(20)
      
      expect(pagination.currentPage.value).toBe(2)
    })
  })

  describe('updateFromApiResponse', () => {
    it('should update from API response', () => {
      const pagination = usePagination()
      
      pagination.updateFromApiResponse({
        page: 2,
        count: 50,
        page_size: 20
      })
      
      expect(pagination.currentPage.value).toBe(2)
      expect(pagination.totalItems.value).toBe(50)
      expect(pagination.itemsPerPage.value).toBe(20)
    })
  })

  describe('reset', () => {
    it('should reset to initial values', () => {
      const pagination = usePagination({
        initialPage: 1,
        initialItemsPerPage: 10
      })
      
      pagination.currentPage.value = 5
      pagination.itemsPerPage.value = 20
      pagination.totalItems.value = 100
      
      pagination.reset()
      
      expect(pagination.currentPage.value).toBe(1)
      expect(pagination.itemsPerPage.value).toBe(10)
      expect(pagination.totalItems.value).toBe(0)
    })
  })

  describe('getPaginationParams', () => {
    it('should return pagination params', () => {
      const pagination = usePagination()
      pagination.currentPage.value = 2
      pagination.itemsPerPage.value = 20
      
      const params = pagination.getPaginationParams()
      
      expect(params).toEqual({
        page: 2,
        page_size: 20
      })
    })
  })

  describe('visiblePages', () => {
    it('should show all pages when total <= maxVisible', () => {
      const pagination = usePagination({ maxVisiblePages: 5 })
      pagination.totalItems.value = 30
      pagination.itemsPerPage.value = 10
      
      const pages = pagination.visiblePages.value
      
      expect(pages).toEqual([1, 2, 3])
    })

    it('should show first 3 pages when near beginning', () => {
      const pagination = usePagination({ maxVisiblePages: 5 })
      pagination.totalItems.value = 100
      pagination.itemsPerPage.value = 10
      pagination.currentPage.value = 2
      
      const pages = pagination.visiblePages.value
      
      expect(pages).toEqual([1, 2, 3])
    })

    it('should show last 3 pages when near end', () => {
      const pagination = usePagination({ maxVisiblePages: 5 })
      pagination.totalItems.value = 100
      pagination.itemsPerPage.value = 10
      pagination.currentPage.value = 9
      
      const pages = pagination.visiblePages.value
      
      expect(pages).toEqual([8, 9, 10])
    })

    it('should show middle pages when in middle', () => {
      const pagination = usePagination({ maxVisiblePages: 5 })
      pagination.totalItems.value = 100
      pagination.itemsPerPage.value = 10
      pagination.currentPage.value = 5
      
      const pages = pagination.visiblePages.value
      
      expect(pages).toEqual([4, 5, 6])
    })
  })

  describe('showPageSeparator', () => {
    it('should show separator when in middle of many pages', () => {
      const pagination = usePagination({ maxVisiblePages: 5 })
      pagination.totalItems.value = 100
      pagination.itemsPerPage.value = 10
      pagination.currentPage.value = 5
      
      expect(pagination.showPageSeparator.value).toBe(true)
    })

    it('should not show separator when at beginning', () => {
      const pagination = usePagination({ maxVisiblePages: 5 })
      pagination.totalItems.value = 100
      pagination.itemsPerPage.value = 10
      pagination.currentPage.value = 2
      
      expect(pagination.showPageSeparator.value).toBe(false)
    })

    it('should not show separator when at end', () => {
      const pagination = usePagination({ maxVisiblePages: 5 })
      pagination.totalItems.value = 100
      pagination.itemsPerPage.value = 10
      pagination.currentPage.value = 9
      
      expect(pagination.showPageSeparator.value).toBe(false)
    })

    it('should not show separator when total pages <= maxVisible', () => {
      const pagination = usePagination({ maxVisiblePages: 5 })
      pagination.totalItems.value = 30
      pagination.itemsPerPage.value = 10
      
      expect(pagination.showPageSeparator.value).toBe(false)
    })
  })

  describe('goToPage edge cases', () => {
    it('should not go to same page', () => {
      const pagination = usePagination()
      pagination.totalItems.value = 50
      pagination.itemsPerPage.value = 10
      pagination.currentPage.value = 2
      
      const result = pagination.goToPage(2)
      
      expect(result).toBe(false)
      expect(pagination.currentPage.value).toBe(2)
    })

    it('should not go to page beyond total', () => {
      const pagination = usePagination()
      pagination.totalItems.value = 50
      pagination.itemsPerPage.value = 10
      
      const result = pagination.goToPage(10)
      
      expect(result).toBe(false)
    })
  })

  describe('updateFromApiResponse edge cases', () => {
    it('should handle response with total_pages', () => {
      const pagination = usePagination()
      
      pagination.updateFromApiResponse({
        page: 2,
        count: 50,
        page_size: 20,
        total_pages: 3
      })
      
      expect(pagination.currentPage.value).toBe(2)
      expect(pagination.totalItems.value).toBe(50)
      expect(pagination.itemsPerPage.value).toBe(20)
    })

    it('should handle response with totalPages (camelCase)', () => {
      const pagination = usePagination()
      
      pagination.updateFromApiResponse({
        currentPage: 2,
        totalItems: 50,
        itemsPerPage: 20,
        totalPages: 3
      })
      
      expect(pagination.currentPage.value).toBe(2)
      expect(pagination.totalItems.value).toBe(50)
      expect(pagination.itemsPerPage.value).toBe(20)
    })

    it('should handle response with page mismatch warning', () => {
      const consoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => {})
      const pagination = usePagination()
      
      pagination.updateFromApiResponse({
        page: 2,
        count: 50,
        page_size: 20,
        total_pages: 10 // Mismatch with computed
      })
      
      // Should warn about mismatch
      expect(consoleWarn).toHaveBeenCalled()
      consoleWarn.mockRestore()
    })

    it('should handle null response', () => {
      const pagination = usePagination()
      const initialPage = pagination.currentPage.value
      
      pagination.updateFromApiResponse(null)
      
      expect(pagination.currentPage.value).toBe(initialPage)
    })
  })

  describe('updatePagination', () => {
    it('should update page only', () => {
      const pagination = usePagination()
      
      pagination.updatePagination({ page: 3 })
      
      expect(pagination.currentPage.value).toBe(3)
    })

    it('should update page_size only', () => {
      const pagination = usePagination()
      
      pagination.updatePagination({ page_size: 25 })
      
      expect(pagination.itemsPerPage.value).toBe(25)
    })

    it('should update count only', () => {
      const pagination = usePagination()
      
      pagination.updatePagination({ count: 100 })
      
      expect(pagination.totalItems.value).toBe(100)
    })

    it('should update all params', () => {
      const pagination = usePagination()
      
      pagination.updatePagination({
        page: 3,
        page_size: 25,
        count: 100
      })
      
      expect(pagination.currentPage.value).toBe(3)
      expect(pagination.itemsPerPage.value).toBe(25)
      expect(pagination.totalItems.value).toBe(100)
    })

    it('should handle null params', () => {
      const pagination = usePagination()
      const initialPage = pagination.currentPage.value
      
      pagination.updatePagination(null)
      
      expect(pagination.currentPage.value).toBe(initialPage)
    })
  })

  describe('setTotalItems edge cases', () => {
    it('should not adjust page if current page is valid', () => {
      const pagination = usePagination()
      pagination.totalItems.value = 50
      pagination.itemsPerPage.value = 10
      pagination.currentPage.value = 3
      
      pagination.setTotalItems(100)
      
      expect(pagination.currentPage.value).toBe(3)
    })

    it('should handle zero total items', () => {
      const pagination = usePagination()
      pagination.currentPage.value = 5
      
      pagination.setTotalItems(0)
      
      expect(pagination.totalItems.value).toBe(0)
    })

    it('should handle negative total items', () => {
      const pagination = usePagination()
      
      pagination.setTotalItems(-10)
      
      expect(pagination.totalItems.value).toBe(0)
    })
  })

  describe('syncWithQuery', () => {
    it('should sync from query params', () => {
      const mockRoute = {
        query: {
          page: '3',
          page_size: '25'
        }
      }
      const mockRouter = {
        replace: vi.fn()
      }

      const pagination = usePagination()
      pagination.syncWithQuery(mockRoute, mockRouter)

      expect(pagination.currentPage.value).toBe(3)
      expect(pagination.itemsPerPage.value).toBe(25)
    })

    it('should handle invalid page in query', () => {
      const mockRoute = {
        query: {
          page: 'invalid',
          page_size: '25'
        }
      }
      const mockRouter = {
        replace: vi.fn()
      }

      const pagination = usePagination({ initialItemsPerPage: 10 })
      pagination.syncWithQuery(mockRoute, mockRouter)

      expect(pagination.currentPage.value).toBe(1) // Should remain default
    })

    it('should handle invalid page_size in query', () => {
      const mockRoute = {
        query: {
          page: '2',
          page_size: 'invalid'
        }
      }
      const mockRouter = {
        replace: vi.fn()
      }

      const pagination = usePagination({ initialItemsPerPage: 10 })
      pagination.syncWithQuery(mockRoute, mockRouter)

      expect(pagination.itemsPerPage.value).toBe(10) // Should remain default
    })

    it('should return updateQuery function', () => {
      const mockRoute = {
        query: {}
      }
      const mockRouter = {
        replace: vi.fn()
      }

      const pagination = usePagination()
      pagination.syncWithQuery(mockRoute, mockRouter)

      expect(typeof updateQuery).toBe('function')
      
      pagination.currentPage.value = 2
      updateQuery()

      expect(mockRouter.replace).toHaveBeenCalled()
    })

    it('should handle missing vue-router', () => {
      const consoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => {})
      
      const pagination = usePagination()
      
      // Mock require to throw error
      const originalRequire = globalThis.require
      globalThis.require = vi.fn(() => {
        throw new Error('Module not found')
      })

      pagination.syncWithQuery()

      expect(consoleWarn).toHaveBeenCalled()
      
      globalThis.require = originalRequire
      consoleWarn.mockRestore()
    })

    it('should not include page=1 in query', () => {
      const mockRoute = {
        query: {}
      }
      const mockRouter = {
        replace: vi.fn()
      }

      const pagination = usePagination()
      pagination.currentPage.value = 1
      pagination.syncWithQuery(mockRoute, mockRouter)
      updateQuery()

      const replaceCall = mockRouter.replace.mock.calls[0][0]
      expect(replaceCall.query.page).toBeUndefined()
    })

    it('should not include default page_size in query', () => {
      const mockRoute = {
        query: {}
      }
      const mockRouter = {
        replace: vi.fn()
      }

      const pagination = usePagination({ initialItemsPerPage: 10 })
      pagination.itemsPerPage.value = 10
      pagination.syncWithQuery(mockRoute, mockRouter)
      updateQuery()

      const replaceCall = mockRouter.replace.mock.calls[0][0]
      expect(replaceCall.query.page_size).toBeUndefined()
    })
  })
})

