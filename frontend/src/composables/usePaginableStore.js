/**
 * Composable for stores with pagination
 * Extends useStoreBase with pagination functionality
 */
import { ref, computed } from 'vue'
import { useStoreBase } from './useStoreBase'

/**
 * Create paginable store composable
 * @param {Object} options - Options
 * @param {number} options.initialPage - Initial page (default: 1)
 * @param {number} options.initialPageSize - Initial page size (default: 10)
 * @returns {Object} Pagination state and methods
 */
export function usePaginableStore(options = {}) {
  const {
    initialPage = 1,
    initialPageSize = 10
  } = options

  // Pagination state
  const currentPage = ref(initialPage)
  const itemsPerPage = ref(initialPageSize)
  const totalPages = ref(1)
  const totalItems = ref(0)

  // Computed
  const hasNextPage = computed(() => currentPage.value < totalPages.value)
  const hasPreviousPage = computed(() => currentPage.value > 1)
  const isFirstPage = computed(() => currentPage.value === 1)
  const isLastPage = computed(() => currentPage.value === totalPages.value)

  /**
   * Update pagination from API response
   * @param {Object} response - API response
   */
  const updatePagination = (response) => {
    if (response.count !== undefined) {
      totalItems.value = response.count
      totalPages.value = Math.ceil(response.count / itemsPerPage.value)
    } else if (response.total !== undefined) {
      totalItems.value = response.total
      totalPages.value = Math.ceil(response.total / itemsPerPage.value)
    } else if (response.total_pages !== undefined) {
      totalPages.value = response.total_pages
      if (response.total_items !== undefined) {
        totalItems.value = response.total_items
      }
    }

    if (response.page !== undefined) {
      currentPage.value = response.page
    }

    if (response.page_size !== undefined) {
      itemsPerPage.value = response.page_size
    }
  }

  /**
   * Go to next page
   */
  const nextPage = () => {
    if (hasNextPage.value) {
      currentPage.value++
    }
  }

  /**
   * Go to previous page
   */
  const previousPage = () => {
    if (hasPreviousPage.value) {
      currentPage.value--
    }
  }

  /**
   * Go to specific page
   * @param {number} page - Page number
   */
  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page
    }
  }

  /**
   * Change page size
   * @param {number} size - Page size
   */
  const setPageSize = (size) => {
    if (size > 0) {
      itemsPerPage.value = size
      currentPage.value = 1 // Reset to first page
    }
  }

  /**
   * Reset pagination
   */
  const resetPagination = () => {
    currentPage.value = initialPage
    itemsPerPage.value = initialPageSize
    totalPages.value = 1
    totalItems.value = 0
  }

  return {
    // State
    currentPage,
    itemsPerPage,
    totalPages,
    totalItems,

    // Computed
    hasNextPage,
    hasPreviousPage,
    isFirstPage,
    isLastPage,

    // Methods
    updatePagination,
    nextPage,
    previousPage,
    goToPage,
    setPageSize,
    resetPagination
  }
}

