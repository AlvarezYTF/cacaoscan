<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-all duration-300">
    <!-- Controles de tabla (opcional) -->
    <div v-if="$slots.controls" class="p-3 md:p-4 border-b border-gray-100 bg-gray-50">
      <slot name="controls"></slot>
    </div>
    
    <!-- Tabla responsiva -->
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th 
              v-for="column in columns" 
              :key="column.key"
              scope="col" 
              class="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              :class="[
                column.align === 'right' ? 'text-right' : 'text-left',
                column.sortable ? 'cursor-pointer hover:bg-gray-100' : '',
                column.width ? column.width : ''
              ]"
              @click="column.sortable ? handleSort(column.key) : null"
            >
              <div class="flex items-center space-x-1">
                <span>{{ column.label }}</span>
                <svg v-if="column.sortable" class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"></path>
                </svg>
              </div>
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr 
            v-for="(row, index) in paginatedData" 
            :key="row.id || index"
            class="hover:bg-gray-50 transition-all duration-200"
            :class="{ 'bg-blue-50': selectedRows.includes(row.id || index) }"
          >
            <td 
              v-for="column in columns" 
              :key="column.key"
              class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap"
              :class="[
                column.align === 'right' ? 'text-right' : 'text-left',
                column.className || ''
              ]"
            >
              <slot :name="`cell-${column.key}`" :row="row" :column="column" :index="index">
                {{ row[column.key] }}
              </slot>
            </td>
          </tr>
          
          <!-- Fila vacía cuando no hay datos -->
          <tr v-if="paginatedData.length === 0">
            <td :colspan="columns.length" class="px-3 md:px-6 py-8 text-center text-gray-500">
              <div class="flex flex-col items-center space-y-2">
                <svg class="w-8 h-8 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 002 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
                </svg>
                <p class="text-sm font-medium">No hay datos disponibles</p>
                <p class="text-xs text-gray-400">Intenta ajustar los filtros o agregar nuevos registros</p>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Paginación -->
    <slot name="pagination"></slot>
    
    <!-- Información de la tabla -->
    <div v-if="showTableInfo" class="px-3 md:px-6 py-2 md:py-3 bg-gray-50 border-t border-gray-100 text-xs text-gray-500">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-1 sm:space-y-0">
        <span>Mostrando {{ startItem }} a {{ endItem }} de {{ totalItems }} resultados</span>
        <span v-if="loading" class="flex items-center space-x-1">
          <svg class="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>Cargando...</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue';

export default {
  name: 'DataTable',
  props: {
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
    showTableInfo: {
      type: Boolean,
      default: true
    },
    itemsPerPage: {
      type: Number,
      default: 10
    },
    currentPage: {
      type: Number,
      default: 1
    },
    selectedRows: {
      type: Array,
      default: () => []
    }
  },
  emits: ['sort', 'row-select'],
  setup(props, { emit }) {
    const paginatedData = computed(() => {
      const start = (props.currentPage - 1) * props.itemsPerPage;
      const end = start + props.itemsPerPage;
      return props.data.slice(start, end);
    });

    const totalItems = computed(() => props.data.length);
    const startItem = computed(() => (props.currentPage - 1) * props.itemsPerPage + 1);
    const endItem = computed(() => Math.min(props.currentPage * props.itemsPerPage, totalItems.value));

    const handleSort = (key) => {
      emit('sort', key);
    };

    return {
      paginatedData,
      totalItems,
      startItem,
      endItem,
      handleSort
    };
  }
};
</script>

<style scoped>
/* Mejoras de responsividad para la tabla */
@media (max-width: 768px) {
  .md\:px-6 {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  .md\:py-4 {
    padding-top: 0.75rem;
    padding-bottom: 0.75rem;
  }
  
  .text-xs {
    font-size: 0.75rem;
    line-height: 1rem;
  }
}

@media (max-width: 640px) {
  .px-3 {
    padding-left: 0.5rem;
    padding-right: 0.5rem;
  }
  
  .py-3 {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }
  
  .text-xs {
    font-size: 0.75rem;
    line-height: 1rem;
  }
  
  /* Ocultar columnas menos importantes en móviles */
  .mobile-hidden {
    display: none;
  }
}

@media (max-width: 480px) {
  .px-3 {
    padding-left: 0.375rem;
    padding-right: 0.375rem;
  }
  
  .py-3 {
    padding-top: 0.375rem;
    padding-bottom: 0.375rem;
  }
  
  .rounded-xl {
    border-radius: 0.5rem;
  }
}

/* Transiciones suaves */
* {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}

/* Mejoras para dispositivos táctiles */
@media (hover: none) and (pointer: coarse) {
  th, td {
    min-height: 44px;
  }
  
  .overflow-x-auto {
    -webkit-overflow-scrolling: touch;
  }
}

/* Efectos de hover mejorados */
tbody tr:hover {
  background-color: #f9fafb;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

/* Animación de entrada para filas */
tbody tr {
  animation: fadeInUp 0.3s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive para pantallas muy grandes */
@media (min-width: 1280px) {
  .lg\:px-8 {
    padding-left: 2rem;
    padding-right: 2rem;
  }
  
  .lg\:py-6 {
    padding-top: 1.5rem;
    padding-bottom: 1.5rem;
  }
}

/* Mejoras para orientación landscape en móviles */
@media (max-width: 768px) and (orientation: landscape) {
  .py-3 {
    padding-top: 0.375rem;
    padding-bottom: 0.375rem;
  }
  
  .py-2 {
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
  }
}

/* Estados de selección */
tbody tr.selected {
  background-color: #eff6ff;
  border-left: 3px solid #3b82f6;
}

/* Estados de carga */
.loading tbody tr {
  opacity: 0.6;
  pointer-events: none;
}

/* Mejoras para accesibilidad */
th:focus-visible,
td:focus-visible {
  outline: 2px solid #10b981;
  outline-offset: 2px;
}

/* Scrollbar personalizado */
.overflow-x-auto::-webkit-scrollbar {
  height: 6px;
}

.overflow-x-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.overflow-x-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.overflow-x-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
