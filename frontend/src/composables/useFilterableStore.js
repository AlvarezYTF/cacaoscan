/**
 * Composable for stores with filtering
 * Provides reactive filter state and methods
 */
import { reactive, computed } from 'vue'

/**
 * Create filterable store composable
 * @param {Object} options - Options
 * @param {Object} options.initialFilters - Initial filter values
 * @param {Function} options.filterFn - Custom filter function
 * @returns {Object} Filter state and methods
 */
export function useFilterableStore(options = {}) {
  const {
    initialFilters = {},
    filterFn = null
  } = options

  // Filter state
  const filters = reactive({ ...initialFilters })

  /**
   * Apply filters to items
   * @param {Array} items - Items to filter
   * @returns {Array} Filtered items
   */
  const applyFilters = (items) => {
    if (!items || !Array.isArray(items)) {
      return []
    }

    if (filterFn && typeof filterFn === 'function') {
      return filterFn(items, filters)
    }

    // Default filter implementation
    return items.filter(item => {
      return Object.entries(filters).every(([key, value]) => {
        if (value == null || (!Array.isArray(value) && value == '')) {
          return true
        }

        const itemValue = item[key]

        if (Array.isArray(value)) {
          return value.includes(itemValue)
        }

        if (typeof value === 'string') {
          return String(itemValue).toLowerCase() === String(value).toLowerCase()
        }

        return itemValue === value
      })
    })
  }

  /**
   * Set filter value
   * @param {string} key - Filter key
   * @param {any} value - Filter value
   */
  const setFilter = (key, value) => {
    filters[key] = value
  }

  /**
   * Get filter value
   * @param {string} key - Filter key
   * @returns {any} Filter value
   */
  const getFilter = (key) => {
    return filters[key]
  }

  /**
   * Clear all filters
   */
  const clearFilters = () => {
    for (const key of Object.keys(filters)) {
      filters[key] = initialFilters[key] || null
    }
  }

  /**
   * Clear specific filter
   * @param {string} key - Filter key
   */
  const clearFilter = (key) => {
    if (filters.hasOwnProperty(key)) {
      filters[key] = initialFilters[key] || null
    }
  }

  /**
   * Check if any filter is active
   * @returns {boolean} True if any filter is active
   */
  const hasActiveFilters = computed(() => {
    return Object.values(filters).some(value => {
      if (Array.isArray(value)) {
        return value.length > 0
      }
      if (value == null) {
        return false
      }
      return String(value) !== ''
    })
  })

  /**
   * Get active filters count
   * @returns {number} Number of active filters
   */
  const activeFiltersCount = computed(() => {
    return Object.values(filters).filter(value => {
      if (Array.isArray(value)) {
        return value.length > 0
      }
      if (value == null) {
        return false
      }
      return String(value) !== ''
    }).length
  })

  return {
    // State
    filters,

    // Computed
    hasActiveFilters,
    activeFiltersCount,

    // Methods
    applyFilters,
    setFilter,
    getFilter,
    clearFilters,
    clearFilter
  }
}

