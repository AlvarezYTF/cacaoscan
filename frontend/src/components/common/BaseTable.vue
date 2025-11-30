<template>
  <div class="base-table-container bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
    <!-- Table Header (optional) -->
    <div v-if="$slots.header || title" class="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-gray-50">
      <slot name="header">
        <h3 v-if="title" class="text-lg font-semibold text-gray-900">{{ title }}</h3>
        <p v-if="subtitle" class="text-sm text-gray-600 mt-1">{{ subtitle }}</p>
      </slot>
    </div>

    <!-- Controls Slot (optional) -->
    <div v-if="$slots.controls" class="p-4 border-b border-gray-200 bg-white">
      <slot name="controls"></slot>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="p-12 text-center">
      <div class="inline-flex flex-col items-center space-y-4">
        <svg class="w-12 h-12 text-gray-400 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="text-sm text-gray-600">{{ loadingText || 'Cargando datos...' }}</p>
      </div>
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto">
      <table 
        class="min-w-full divide-y divide-gray-200" 
        :aria-label="ariaLabel || 'Tabla de datos'"
      >
        <caption v-if="caption" class="sr-only">{{ caption }}</caption>
        <thead class="bg-gradient-to-r from-gray-50 to-gray-50">
          <tr>
            <!-- Selection checkbox column -->
            <th 
              v-if="enableSelection"
              scope="col"
              class="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"
            >
              <input
                type="checkbox"
                :checked="isSelectAll"
                @change="handleSelectAll"
                class="rounded border-gray-300 text-green-600 focus:ring-green-500"
                :aria-label="'Seleccionar todos'"
              />
            </th>

            <!-- Data columns -->
            <th
              v-for="column in columns"
              :key="column.key"
              scope="col"
              class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"
              :class="[
                column.align === 'right' ? 'text-right' : 'text-left',
                column.sortable ? 'cursor-pointer hover:bg-green-50 transition-all duration-200' : '',
                column.width ? column.width : '',
                sortKey === column.key ? 'bg-green-100' : ''
              ]"
              @click="column.sortable ? handleSortClick(column.key) : null"
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
                  ></path>
                  <path 
                    v-else 
                    stroke-linecap="round" 
                    stroke-linejoin="round" 
                    stroke-width="2" 
                    d="M19 9l-7 7-7-7"
                  ></path>
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
                  ></path>
                </svg>
              </div>
            </th>

            <!-- Actions column (if slot provided) -->
            <th 
              v-if="$slots.actions"
              scope="col"
              class="px-6 py-4 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider"
            >
              Acciones
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr
            v-for="(row, index) in processedData"
            :key="getRowKey(row, index)"
            class="hover:bg-gray-50 transition-colors duration-200"
            :class="[
              isRowSelected(getRowKey(row, index)) ? 'bg-green-50 border-l-4 border-green-500' : '',
              rowClass ? rowClass(row, index) : ''
            ]"
            @click="handleRowClick(row, index)"
          >
            <!-- Selection checkbox -->
            <td 
              v-if="enableSelection"
              class="px-4 py-4 whitespace-nowrap"
              @click.stop
            >
              <input
                type="checkbox"
                :checked="isRowSelected(getRowKey(row, index))"
                @change="handleRowSelection(getRowKey(row, index))"
                class="rounded border-gray-300 text-green-600 focus:ring-green-500"
                :aria-label="`Seleccionar fila ${index + 1}`"
              />
            </td>

            <!-- Data cells -->
            <td
              v-for="column in columns"
              :key="column.key"
              class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
              :class="[
                column.align === 'right' ? 'text-right' : 'text-left',
                column.className ? column.className : ''
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
              v-if="$slots.actions"
              class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"
              @click.stop
            >
              <slot name="actions" :row="row" :index="index"></slot>
            </td>
          </tr>

          <!-- Empty State -->
          <tr v-if="processedData.length === 0">
            <td 
              :colspan="totalColumns" 
              class="px-6 py-16 text-center"
            >
              <slot name="empty">
                <div class="flex flex-col items-center space-y-4">
                  <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
                    <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 002 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
                    </svg>
                  </div>
                  <div>
                    <p class="text-base font-bold text-gray-900 mb-1">{{ emptyText || 'No hay datos disponibles' }}</p>
                    <p class="text-sm text-gray-600">{{ emptySubtext || 'Intenta ajustar los filtros o agregar nuevos registros' }}</p>
                  </div>
                </div>
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination Slot -->
    <div v-if="$slots.pagination" class="border-t border-gray-200">
      <slot name="pagination"></slot>
    </div>

    <!-- Table Info Footer -->
    <div 
      v-if="showTableInfo && !loading" 
      class="px-6 py-4 bg-gradient-to-r from-gray-50 to-gray-50 border-t border-gray-200 text-sm text-gray-600"
    >
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-1 sm:space-y-0">
        <span>
          Mostrando {{ startItem }} a {{ endItem }} de {{ totalItems }} resultados
        </span>
        <span v-if="selectedRows.length > 0" class="text-green-600 font-medium">
          {{ selectedRows.length }} seleccionado{{ selectedRows.length > 1 ? 's' : '' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useTable } from '@/composables/useTable'
import { usePagination } from '@/composables/usePagination'

const props = defineProps({
  columns: {
    type: Array,
    required: true,
    validator: (value) => value.every(col => 'key' in col && 'label' in col)
  },
  data: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  loadingText: {
    type: String,
    default: 'Cargando datos...'
  },
  enableSelection: {
    type: Boolean,
    default: false
  },
  enablePagination: {
    type: Boolean,
    default: false
  },
  itemsPerPage: {
    type: Number,
    default: 10
  },
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  ariaLabel: {
    type: String,
    default: 'Tabla de datos'
  },
  caption: {
    type: String,
    default: ''
  },
  emptyText: {
    type: String,
    default: 'No hay datos disponibles'
  },
  emptySubtext: {
    type: String,
    default: 'Intenta ajustar los filtros o agregar nuevos registros'
  },
  showTableInfo: {
    type: Boolean,
    default: true
  },
  rowKey: {
    type: [String, Function],
    default: 'id'
  },
  rowClass: {
    type: Function,
    default: null
  },
  filterFn: {
    type: Function,
    default: null
  }
})

const emit = defineEmits(['sort', 'row-click', 'row-select', 'select-all'])

// Use table composable
const table = useTable({
  initialSortKey: '',
  initialSortOrder: 'asc',
  enableSelection: props.enableSelection
})

// Use pagination composable if enabled
const pagination = props.enablePagination 
  ? usePagination({
      initialItemsPerPage: props.itemsPerPage
    })
  : null

// Expose table state
const { sortKey, sortOrder, selectedRows, isSelectAll } = table

// Computed
const totalColumns = computed(() => {
  let count = props.columns.length
  if (props.enableSelection) count++
  if (props.$slots.actions) count++
  return count
})

const processedData = computed(() => {
  let result = [...props.data]

  // Apply filtering if provided
  if (props.filterFn && typeof props.filterFn === 'function') {
    result = table.filterData(result, props.filterFn)
  }

  // Apply sorting
  if (sortKey.value) {
    result = table.processTableData(result, { filterFn: null })
  }

  // Apply pagination if enabled
  if (props.enablePagination && pagination) {
    const start = (pagination.currentPage.value - 1) * pagination.itemsPerPage.value
    const end = start + pagination.itemsPerPage.value
    result = result.slice(start, end)
    
    // Update pagination total
    pagination.setTotalItems(props.data.length)
  }

  return result
})

const startItem = computed(() => {
  if (props.enablePagination && pagination) {
    return pagination.startItem.value
  }
  return 1
})

const endItem = computed(() => {
  if (props.enablePagination && pagination) {
    return pagination.endItem.value
  }
  return props.data.length
})

const totalItems = computed(() => {
  return props.data.length
})

// Methods
const getRowKey = (row, index) => {
  if (typeof props.rowKey === 'function') {
    return props.rowKey(row, index)
  }
  return row[props.rowKey] || index
}

const handleSortClick = (key) => {
  table.handleSort(key)
  emit('sort', {
    key: table.sortKey.value,
    order: table.sortOrder.value
  })
}

const handleRowClick = (row, index) => {
  emit('row-click', row, index)
}

const handleRowSelection = (rowId) => {
  table.toggleRowSelection(rowId)
  emit('row-select', rowId, table.isRowSelected(rowId))
}

const handleSelectAll = () => {
  const allRowIds = processedData.value.map((row, index) => getRowKey(row, index))
  table.selectAll(allRowIds)
  emit('select-all', table.isSelectAll.value)
}

const formatCellValue = (value, column) => {
  if (value === null || value === undefined) {
    return column.emptyText || 'N/A'
  }
  
  if (column.formatter && typeof column.formatter === 'function') {
    return column.formatter(value)
  }
  
  return value
}

// Expose methods and state
defineExpose({
  ...table,
  pagination,
  processedData,
  clearSelection: table.clearSelection,
  selectAll: handleSelectAll
})
</script>

<style scoped>
.base-table-container {
  @apply w-full;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
</style>

