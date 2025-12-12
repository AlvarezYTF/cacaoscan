<template>
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden" data-cy="data-table">
    <!-- Controls slot -->
    <div v-if="$slots.controls" class="p-6 border-b border-gray-200 bg-gradient-to-r from-green-50 to-green-50">
      <slot name="controls" />
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="p-12 text-center">
      <div class="inline-flex flex-col items-center space-y-4">
        <div class="w-12 h-12 border-4 border-gray-300 border-t-green-600 rounded-full animate-spin"></div>
        <p class="text-sm text-gray-600">{{ loadingText || 'Cargando datos...' }}</p>
      </div>
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto">
      <table 
        class="min-w-full divide-y divide-gray-200" 
        :aria-label="tableLabel || 'Tabla de datos'"
      >
        <caption v-if="tableLabel" class="sr-only">{{ tableLabel }}</caption>
        
        <!-- Header -->
        <thead class="bg-gradient-to-r from-gray-50 to-gray-50">
          <tr>
            <!-- Selection checkbox -->
            <th 
              v-if="selectable"
              scope="col"
              class="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"
            >
              <input
                type="checkbox"
                :checked="isAllSelected"
                :indeterminate="isSomeSelected"
                @change="handleSelectAll"
                class="rounded border-gray-300 text-green-600 focus:ring-green-500"
                aria-label="Seleccionar todos"
              />
            </th>

            <!-- Column headers -->
            <th
              v-for="column in columns"
              :key="column.key"
              scope="col"
              class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"
              :class="[
                column.align === 'right' ? 'text-right' : 'text-left',
                column.sortable ? 'cursor-pointer hover:bg-green-50 transition-all duration-200' : '',
                column.width || '',
                sortKey === column.key ? 'bg-green-100' : ''
              ]"
              @click="column.sortable ? handleSort(column.key) : null"
            >
              <div class="flex items-center space-x-1">
                <span>{{ column.label }}</span>
                <svg 
                  v-if="column.sortable && sortKey === column.key" 
                  class="w-4 h-4 text-green-600" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path 
                    v-if="sortOrder === 'asc'" 
                    stroke-linecap="round" 
                    stroke-linejoin="round" 
                    stroke-width="2" 
                    d="M5 15l7-7 7 7"
                  />
                  <path 
                    v-else 
                    stroke-linecap="round" 
                    stroke-linejoin="round" 
                    stroke-width="2" 
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
                <svg 
                  v-else-if="column.sortable" 
                  class="w-4 h-4 text-gray-400" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path 
                    stroke-linecap="round" 
                    stroke-linejoin="round" 
                    stroke-width="2" 
                    d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"
                  />
                </svg>
              </div>
            </th>

            <!-- Actions column -->
            <th 
              v-if="actions && actions.length > 0"
              scope="col"
              class="px-6 py-4 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider"
            >
              Acciones
            </th>
          </tr>
        </thead>

        <!-- Body -->
        <tbody class="bg-white divide-y divide-gray-200">
          <tr 
            v-for="(row, index) in displayedData" 
            :key="getRowKey(row, index)"
            class="hover:bg-green-50 transition-all duration-200"
            :class="[
              selectable && isRowSelected(row) ? 'bg-green-100 border-l-4 border-green-500' : '',
              rowClickable ? 'cursor-pointer' : ''
            ]"
            @click="rowClickable ? handleRowClick(row, index) : null"
          >
            <!-- Selection checkbox -->
            <td 
              v-if="selectable"
              class="px-4 py-4 whitespace-nowrap"
              @click.stop
            >
              <input
                type="checkbox"
                :checked="isRowSelected(row)"
                @change="handleRowSelect(row, $event.target.checked)"
                class="rounded border-gray-300 text-green-600 focus:ring-green-500"
                :aria-label="`Seleccionar fila ${index + 1}`"
              />
            </td>

            <!-- Data cells -->
            <td 
              v-for="column in columns" 
              :key="column.key"
              class="px-6 py-4 whitespace-nowrap"
              :class="[
                column.align === 'right' ? 'text-right' : 'text-left',
                column.className || ''
              ]"
            >
              <slot 
                :name="`cell-${column.key}`" 
                :row="row" 
                :column="column" 
                :index="index"
                :value="row[column.key]"
              >
                {{ formatCellValue(row[column.key], column) }}
              </slot>
            </td>

            <!-- Actions cell -->
            <td 
              v-if="actions && actions.length > 0"
              class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"
              @click.stop
            >
              <slot name="actions" :row="row" :index="index">
                <div class="flex items-center justify-end space-x-2">
                  <button
                    v-for="action in actions"
                    :key="action.key"
                    @click="handleActionClick(action, row, index)"
                    :class="[
                      'px-3 py-1 rounded-md text-sm font-medium transition-colors',
                      action.variant === 'danger' ? 'text-red-600 hover:bg-red-50' : '',
                      action.variant === 'warning' ? 'text-yellow-600 hover:bg-yellow-50' : '',
                      action.variant === 'info' ? 'text-blue-600 hover:bg-blue-50' : '',
                      !action.variant ? 'text-green-600 hover:bg-green-50' : ''
                    ]"
                    :title="action.title"
                  >
                    {{ action.label }}
                  </button>
                </div>
              </slot>
            </td>
          </tr>

          <!-- Empty state -->
          <tr v-if="displayedData.length === 0">
            <td :colspan="totalColumns" class="px-6 py-16 text-center">
              <slot name="empty">
                <div class="flex flex-col items-center space-y-4">
                  <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
                    <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 002 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
                    </svg>
                  </div>
                  <div>
                    <p class="text-base font-bold text-gray-900 mb-1">No hay datos disponibles</p>
                    <p class="text-sm text-gray-600">{{ emptyMessage || 'Intenta ajustar los filtros o agregar nuevos registros' }}</p>
                  </div>
                </div>
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination slot -->
    <div v-if="$slots.pagination || (pagination && pagination.totalPages > 1)" class="border-t border-gray-200">
      <slot name="pagination" :pagination="pagination" />
    </div>

    <!-- Table info -->
    <div v-if="showTableInfo && !loading" class="px-6 py-4 bg-gradient-to-r from-green-50 to-green-50 border-t border-gray-200 text-sm text-gray-600">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-1 sm:space-y-0">
        <span>Mostrando {{ startItem }} a {{ endItem }} de {{ totalItems }} resultados</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { usePagination } from '@/composables/usePagination'

const props = defineProps({
  columns: {
    type: Array,
    required: true,
    validator: (value) => value.every(col => 'key' in col && 'label' in col)
  },
  data: {
    type: Array,
    required: true,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  loadingText: {
    type: String,
    default: null
  },
  selectable: {
    type: Boolean,
    default: false
  },
  selectedRows: {
    type: Array,
    default: () => []
  },
  sortable: {
    type: Boolean,
    default: true
  },
  filterable: {
    type: Boolean,
    default: false
  },
  rowClickable: {
    type: Boolean,
    default: false
  },
  actions: {
    type: Array,
    default: null,
    validator: (value) => {
      if (!value) return true
      return value.every(action => 'key' in action && 'label' in action)
    }
  },
  pagination: {
    type: Object,
    default: null
  },
  tableLabel: {
    type: String,
    default: ''
  },
  emptyMessage: {
    type: String,
    default: null
  },
  showTableInfo: {
    type: Boolean,
    default: true
  },
  rowKey: {
    type: [String, Function],
    default: 'id'
  }
})

const emit = defineEmits(['sort', 'filter', 'row-select', 'row-click', 'action-click', 'select-all'])

// Sorting state
const sortKey = ref(null)
const sortOrder = ref('asc')

// Pagination
const paginationState = usePagination({
  initialPage: props.pagination?.currentPage || 1,
  initialItemsPerPage: props.pagination?.itemsPerPage || 10
})

// Computed
const totalColumns = computed(() => {
  let count = props.columns.length
  if (props.selectable) count++
  if (props.actions && props.actions.length > 0) count++
  return count
})

const displayedData = computed(() => {
  let result = [...props.data]

  // Apply sorting
  if (sortKey.value && props.sortable) {
    result.sort((a, b) => {
      const aVal = a[sortKey.value]
      const bVal = b[sortKey.value]
      
      if (aVal === bVal) return 0
      
      const comparison = aVal > bVal ? 1 : -1
      return sortOrder.value === 'asc' ? comparison : -comparison
    })
  }

  // Apply pagination if not provided externally
  if (!props.pagination && props.data.length > paginationState.itemsPerPage.value) {
    const start = (paginationState.currentPage.value - 1) * paginationState.itemsPerPage.value
    const end = start + paginationState.itemsPerPage.value
    result = result.slice(start, end)
  }

  return result
})

const totalItems = computed(() => {
  return props.pagination?.totalItems || props.data.length
})

const startItem = computed(() => {
  if (props.pagination) {
    return (props.pagination.currentPage - 1) * props.pagination.itemsPerPage + 1
  }
  return paginationState.startItem.value
})

const endItem = computed(() => {
  if (props.pagination) {
    return Math.min(props.pagination.currentPage * props.pagination.itemsPerPage, totalItems.value)
  }
  return paginationState.endItem.value
})

const isAllSelected = computed(() => {
  if (!props.selectable || displayedData.value.length === 0) return false
  return displayedData.value.every(row => isRowSelected(row))
})

const isSomeSelected = computed(() => {
  if (!props.selectable) return false
  const selectedCount = displayedData.value.filter(row => isRowSelected(row)).length
  return selectedCount > 0 && selectedCount < displayedData.value.length
})

// Methods
const getRowKey = (row, index) => {
  if (typeof props.rowKey === 'function') {
    return props.rowKey(row, index)
  }
  return row[props.rowKey] || index
}

const isRowSelected = (row) => {
  const key = getRowKey(row, 0)
  return props.selectedRows.includes(key)
}

const handleSort = (key) => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
  emit('sort', { key: sortKey.value, order: sortOrder.value })
}

const handleRowSelect = (row, checked) => {
  const key = getRowKey(row, 0)
  emit('row-select', { row, key, selected: checked })
}

const handleSelectAll = (event) => {
  emit('select-all', { selected: event.target.checked })
}

const handleRowClick = (row, index) => {
  emit('row-click', { row, index })
}

const handleActionClick = (action, row, index) => {
  emit('action-click', { action: action.key, row, index })
}

const formatCellValue = (value, column) => {
  if (value === null || value === undefined) {
    return column.emptyValue || '-'
  }
  
  if (column.formatter && typeof column.formatter === 'function') {
    return column.formatter(value)
  }
  
  return value
}
</script>

<style scoped>
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>

