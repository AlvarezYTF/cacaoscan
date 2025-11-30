/**
 * Composable for pagination logic
 * Provides reusable pagination state and handlers
 */
import { ref, computed } from 'vue'

/**
 * Creates pagination state and handlers
 * @param {Object} options - Pagination options
 * @param {number} options.initialPage - Initial page number (default: 1)
 * @param {number} options.initialItemsPerPage - Initial items per page (default: 10)
 * @param {number} options.maxVisiblePages - Maximum visible page numbers (default: 5)
 * @returns {Object} Pagination state and methods
 */
export function usePagination(options = {}) {
  const {
    initialPage = 1,
    initialItemsPerPage = 10,
    maxVisiblePages = 5
  } = options

  // State
  const currentPage = ref(initialPage)
  const itemsPerPage = ref(initialItemsPerPage)
  const totalItems = ref(0)
  const maxVisible = ref(maxVisiblePages)

  // Computed
  const totalPages = computed(() => {
    if (totalItems.value === 0) return 1
    return Math.ceil(totalItems.value / itemsPerPage.value)
  })

  const startItem = computed(() => {
    if (totalItems.value === 0) return 0
    return (currentPage.value - 1) * itemsPerPage.value + 1
  })

  const endItem = computed(() => {
    return Math.min(currentPage.value * itemsPerPage.value, totalItems.value)
  })

  const hasNextPage = computed(() => {
    return currentPage.value < totalPages.value
  })

  const hasPreviousPage = computed(() => {
    return currentPage.value > 1
  })

  const visiblePages = computed(() => {
    const pages = []
    const total = totalPages.value

    if (total <= maxVisible.value) {
      // Show all pages if total is less than max visible
      for (let i = 1; i <= total; i++) {
        pages.push(i)
      }
    } else if (currentPage.value <= 3) {
      // Near the beginning
      for (let i = 1; i <= 3; i++) {
        pages.push(i)
      }
    } else if (currentPage.value >= total - 2) {
      // Near the end
      for (let i = total - 2; i <= total; i++) {
        pages.push(i)
      }
    } else {
      // In the middle
      for (let i = currentPage.value - 1; i <= currentPage.value + 1; i++) {
        pages.push(i)
      }
    }

    return pages
  })

  const showPageSeparator = computed(() => {
    return totalPages.value > maxVisible.value &&
           (currentPage.value > 3 && currentPage.value < totalPages.value - 2)
  })

  // Methods
  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages.value && page !== currentPage.value) {
      currentPage.value = page
      return true
    }
    return false
  }

  const nextPage = () => {
    return goToPage(currentPage.value + 1)
  }

  const previousPage = () => {
    return goToPage(currentPage.value - 1)
  }

  const firstPage = () => {
    return goToPage(1)
  }

  const lastPage = () => {
    return goToPage(totalPages.value)
  }

  const setItemsPerPage = (newItemsPerPage) => {
    if (newItemsPerPage > 0) {
      itemsPerPage.value = newItemsPerPage
      // Reset to first page when changing items per page
      currentPage.value = 1
    }
  }

  const setTotalItems = (total) => {
    totalItems.value = Math.max(0, total)
    // Adjust current page if it's beyond total pages
    if (currentPage.value > totalPages.value && totalPages.value > 0) {
      currentPage.value = totalPages.value
    }
  }

  const updateFromApiResponse = (responseData) => {
    if (responseData) {
      currentPage.value = responseData.page || responseData.currentPage || 1
      totalItems.value = responseData.count || responseData.totalItems || 0
      itemsPerPage.value = responseData.page_size || responseData.itemsPerPage || initialItemsPerPage
      
      // Update totalPages if provided
      if (responseData.total_pages || responseData.totalPages) {
        // Validate that computed totalPages matches
        const apiTotalPages = responseData.total_pages || responseData.totalPages
        const computedTotalPages = totalPages.value
        if (Math.abs(apiTotalPages - computedTotalPages) > 1) {
          console.warn('Pagination mismatch: API total_pages does not match computed value')
        }
      }
    }
  }

  const reset = () => {
    currentPage.value = initialPage
    itemsPerPage.value = initialItemsPerPage
    totalItems.value = 0
  }

  const getPaginationParams = () => {
    return {
      page: currentPage.value,
      page_size: itemsPerPage.value
    }
  }

  /**
   * Syncs pagination state with URL query parameters
   * @param {Object} route - Vue Router route object (optional, will be imported if not provided)
   * @param {Object} router - Vue Router router object (optional, will be imported if not provided)
   * @returns {void}
   */
  const syncWithQuery = (route = null, router = null) => {
    // Lazy import to avoid circular dependencies
    let routeObj = route
    let routerObj = router

    if (!routeObj || !routerObj) {
      try {
        const { useRoute, useRouter } = require('vue-router')
        routeObj = routeObj || useRoute()
        routerObj = routerObj || useRouter()
      } catch (error) {
        console.warn('Vue Router not available for query sync:', error)
        return
      }
    }

    // Read from query params
    if (routeObj.query.page) {
      const page = Number.parseInt(routeObj.query.page, 10)
      if (!Number.isNaN(page) && page >= 1) {
        currentPage.value = page
      }
    }

    if (routeObj.query.page_size) {
      const pageSize = Number.parseInt(routeObj.query.page_size, 10)
      if (!Number.isNaN(pageSize) && pageSize > 0) {
        itemsPerPage.value = pageSize
      }
    }

    // Watch for changes and update query params
    const updateQuery = () => {
      if (routerObj) {
        routerObj.replace({
          query: {
            ...routeObj.query,
            page: currentPage.value > 1 ? currentPage.value : undefined,
            page_size: itemsPerPage.value === initialItemsPerPage ? undefined : itemsPerPage.value
          }
        })
      }
    }

    // Return a function to manually sync (call this after state changes)
    return updateQuery
  }

  return {
    // State
    currentPage,
    itemsPerPage,
    totalItems,
    maxVisible,

    // Computed
    totalPages,
    startItem,
    endItem,
    hasNextPage,
    hasPreviousPage,
    visiblePages,
    showPageSeparator,

    // Methods
    goToPage,
    nextPage,
    previousPage,
    firstPage,
    lastPage,
    setItemsPerPage,
    setTotalItems,
    updateFromApiResponse,
    reset,
    getPaginationParams,
    syncWithQuery
  }
}

