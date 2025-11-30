/**
 * Composable for table logic (sorting, selection, filtering)
 * Provides reusable table state and handlers
 */
import { ref, computed } from 'vue'

/**
 * Creates table state and handlers
 * @param {Object} options - Table options
 * @param {string} options.initialSortKey - Initial sort key (default: '')
 * @param {string} options.initialSortOrder - Initial sort order: 'asc' or 'desc' (default: 'asc')
 * @param {boolean} options.enableSelection - Enable row selection (default: false)
 * @param {Array} options.initialSelectedRows - Initially selected row IDs (default: [])
 * @returns {Object} Table state and methods
 */
export function useTable(options = {}) {
  const {
    initialSortKey = '',
    initialSortOrder = 'asc',
    enableSelection = false,
    initialSelectedRows = []
  } = options

  // Sorting state
  const sortKey = ref(initialSortKey)
  const sortOrder = ref(initialSortOrder)

  // Selection state
  const selectedRows = ref([...initialSelectedRows])
  const isSelectAll = ref(false)

  // Computed
  const isSorted = computed(() => {
    return sortKey.value !== ''
  })

  const sortIcon = computed(() => {
    if (!isSorted.value) return null
    return sortOrder.value === 'asc' ? 'up' : 'down'
  })

  // Methods - Sorting
  const handleSort = (key) => {
    if (key === sortKey.value) {
      // Toggle order if same key
      sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    } else {
      // New key, default to ascending
      sortKey.value = key
      sortOrder.value = 'asc'
    }
  }

  const setSort = (key, order = 'asc') => {
    sortKey.value = key
    sortOrder.value = order
  }

  const clearSort = () => {
    sortKey.value = ''
    sortOrder.value = 'asc'
  }

  const getSortParams = () => {
    if (!sortKey.value) return {}
    return {
      sort_by: sortKey.value,
      sort_order: sortOrder.value
    }
  }

  // Methods - Selection
  const toggleRowSelection = (rowId) => {
    if (!enableSelection) return

    const index = selectedRows.value.indexOf(rowId)
    if (index > -1) {
      selectedRows.value.splice(index, 1)
    } else {
      selectedRows.value.push(rowId)
    }
    updateSelectAllState()
  }

  const selectRow = (rowId) => {
    if (!enableSelection) return
    if (!selectedRows.value.includes(rowId)) {
      selectedRows.value.push(rowId)
      updateSelectAllState()
    }
  }

  const deselectRow = (rowId) => {
    if (!enableSelection) return
    const index = selectedRows.value.indexOf(rowId)
    if (index > -1) {
      selectedRows.value.splice(index, 1)
      updateSelectAllState()
    }
  }

  const selectAll = (allRowIds) => {
    if (!enableSelection) return
    if (isSelectAll.value) {
      selectedRows.value = []
    } else {
      selectedRows.value = [...allRowIds]
    }
    isSelectAll.value = !isSelectAll.value
  }

  const clearSelection = () => {
    selectedRows.value = []
    isSelectAll.value = false
  }

  const updateSelectAllState = () => {
    // This should be called with total available rows to determine select all state
    // For now, we'll just track if all current selected rows match
  }

  const isRowSelected = (rowId) => {
    return selectedRows.value.includes(rowId)
  }

  const getSelectedCount = computed(() => {
    return selectedRows.value.length
  })

  const hasSelection = computed(() => {
    return selectedRows.value.length > 0
  })

  // Methods - Filtering (basic)
  const filterData = (data, filterFn) => {
    if (!filterFn || typeof filterFn !== 'function') {
      return data
    }
    return data.filter(filterFn)
  }

  // Methods - Combined sorting and filtering
  const processTableData = (data, options = {}) => {
    let processed = [...data]

    // Apply custom filter if provided
    if (options.filterFn) {
      processed = filterData(processed, options.filterFn)
    }

    // Apply sorting if sort key is set
    if (sortKey.value && processed.length > 0) {
      processed.sort((a, b) => {
        const aValue = a[sortKey.value]
        const bValue = b[sortKey.value]

        // Handle null/undefined
        if (aValue == null && bValue == null) return 0
        if (aValue == null) return 1
        if (bValue == null) return -1

        // Compare values
        let comparison = 0
        if (typeof aValue === 'string' && typeof bValue === 'string') {
          comparison = aValue.localeCompare(bValue)
        } else if (typeof aValue === 'number' && typeof bValue === 'number') {
          comparison = aValue - bValue
        } else if (aValue instanceof Date && bValue instanceof Date) {
          comparison = aValue.getTime() - bValue.getTime()
        } else {
          comparison = String(aValue).localeCompare(String(bValue))
        }

        return sortOrder.value === 'asc' ? comparison : -comparison
      })
    }

    return processed
  }

  const reset = () => {
    sortKey.value = initialSortKey
    sortOrder.value = initialSortOrder
    selectedRows.value = [...initialSelectedRows]
    isSelectAll.value = false
  }

  return {
    // Sorting state
    sortKey,
    sortOrder,
    isSorted,
    sortIcon,

    // Selection state
    selectedRows,
    isSelectAll,
    hasSelection,
    getSelectedCount,

    // Sorting methods
    handleSort,
    setSort,
    clearSort,
    getSortParams,

    // Selection methods
    toggleRowSelection,
    selectRow,
    deselectRow,
    selectAll,
    clearSelection,
    isRowSelected,

    // Data processing
    filterData,
    processTableData,

    // Utility
    reset
  }
}

