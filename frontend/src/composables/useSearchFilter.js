/**
 * Composable for managing search and filter state
 * Provides debounced search query and filter management utilities
 */
import { ref, computed, watch } from 'vue'

/**
 * Creates a search filter composable with debouncing
 * @param {Object} options - Configuration options
 * @param {string} options.initialQuery - Initial search query value
 * @param {number} options.debounceMs - Debounce delay in milliseconds
 * @returns {Object} Search filter state and utilities
 */
export function useSearchFilter(options = {}) {
  const {
    initialQuery = '',
    debounceMs = 300
  } = options

  // Search query (immediate update)
  const searchQuery = ref(initialQuery)
  
  // Debounced search query (for API calls)
  const debouncedQuery = ref(initialQuery)
  
  // Debounce timer
  let debounceTimer = null

  // Watch search query and debounce
  watch(searchQuery, (newValue) => {
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }
    
    debounceTimer = setTimeout(() => {
      debouncedQuery.value = newValue
    }, debounceMs)
  }, { immediate: true })

  /**
   * Clear search query
   */
  const clearSearch = () => {
    searchQuery.value = ''
    debouncedQuery.value = ''
    if (debounceTimer) {
      clearTimeout(debounceTimer)
      debounceTimer = null
    }
  }

  /**
   * Check if search query is empty
   */
  const hasSearchQuery = computed(() => {
    return searchQuery.value.trim().length > 0
  })

  return {
    searchQuery,
    debouncedQuery,
    clearSearch,
    hasSearchQuery
  }
}

/**
 * Creates a filter composable for managing multiple filters
 * @param {Object} initialFilters - Initial filter values
 * @returns {Object} Filter state and utilities
 */
export function useFilters(initialFilters = {}) {
  const filters = ref({ ...initialFilters })

  /**
   * Update a specific filter value
   * @param {string} key - Filter key
   * @param {*} value - Filter value
   */
  const updateFilter = (key, value) => {
    filters.value[key] = value
  }

  /**
   * Update multiple filters at once
   * @param {Object} newFilters - Object with filter updates
   */
  const updateFilters = (newFilters) => {
    filters.value = {
      ...filters.value,
      ...newFilters
    }
  }

  /**
   * Clear all filters to initial values
   */
  const clearFilters = () => {
    filters.value = { ...initialFilters }
  }

  /**
   * Reset a specific filter to initial value
   * @param {string} key - Filter key to reset
   */
  const resetFilter = (key) => {
    if (key in initialFilters) {
      filters.value[key] = initialFilters[key]
    }
  }

  /**
   * Check if any filter is active (not equal to initial value)
   */
  const hasActiveFilters = computed(() => {
    return Object.keys(filters.value).some(key => {
      return filters.value[key] !== initialFilters[key]
    })
  })

  /**
   * Get count of active filters
   */
  const activeFiltersCount = computed(() => {
    return Object.keys(filters.value).filter(key => {
      return filters.value[key] !== initialFilters[key]
    }).length
  })

  return {
    filters,
    updateFilter,
    updateFilters,
    clearFilters,
    resetFilter,
    hasActiveFilters,
    activeFiltersCount
  }
}

