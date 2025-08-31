<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200">
    <!-- Header with filters and actions -->
    <div class="px-6 py-4 border-b border-gray-200">
      <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <!-- Title and stats -->
        <div>
          <h3 class="text-lg font-semibold text-gray-900">
            Dataset de Imágenes
          </h3>
          <p class="text-sm text-gray-600">
            {{ totalItems }} imagen{{ totalItems !== 1 ? 'es' : '' }} en total
            <span v-if="selectedRows.length > 0" class="text-blue-600">
              • {{ selectedRows.length }} seleccionada{{ selectedRows.length !== 1 ? 's' : '' }}
            </span>
          </p>
        </div>
        
        <!-- Actions -->
        <div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3">
          <!-- Bulk actions -->
          <div v-if="selectedRows.length > 0" class="flex space-x-2">
            <button
              @click="showBulkEditModal = true"
              class="px-3 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Editar {{ selectedRows.length }}
            </button>
            
            <button
              @click="confirmBulkDelete"
              class="px-3 py-2 bg-red-600 text-white text-sm font-medium rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Eliminar {{ selectedRows.length }}
            </button>
          </div>
          
          <!-- Regular actions -->
          <div class="flex space-x-2">
            <button
              @click="toggleFilters"
              class="px-3 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500"
              :class="{ 'bg-gray-100': showFilters }"
            >
              <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
              Filtros
            </button>
            
            <button
              @click="exportData"
              :disabled="isLoading"
              class="px-3 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
            >
              <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-4-4m4 4l4-4m-6 4h8" />
              </svg>
              Exportar CSV
            </button>
            
            <button
              @click="refreshData"
              :disabled="isLoading"
              class="px-3 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
            >
              <svg class="w-4 h-4 inline mr-1" :class="{ 'animate-spin': isLoading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Actualizar
            </button>
          </div>
        </div>
      </div>
      
      <!-- Filters (collapsible) -->
      <Transition name="slide-down">
        <div v-if="showFilters" class="mt-4 pt-4 border-t border-gray-200">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">Calidad</label>
              <select 
                v-model="filters.predicted_quality"
                @change="applyFilters"
                class="w-full text-sm border border-gray-300 rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="">Todas</option>
                <option value="excellent">Excelente</option>
                <option value="good">Buena</option>
                <option value="fair">Regular</option>
                <option value="poor">Pobre</option>
              </select>
            </div>
            
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">Estado</label>
              <select 
                v-model="filters.is_processed"
                @change="applyFilters"
                class="w-full text-sm border border-gray-300 rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="">Todos</option>
                <option value="true">Procesado</option>
                <option value="false">Sin procesar</option>
              </select>
            </div>
            
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">Lote</label>
              <input
                v-model="filters.batch_number"
                @input="debouncedFilter"
                type="text"
                placeholder="Número de lote..."
                class="w-full text-sm border border-gray-300 rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
            
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">Origen</label>
              <input
                v-model="filters.origin"
                @input="debouncedFilter"
                type="text"
                placeholder="País/región..."
                class="w-full text-sm border border-gray-300 rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
          </div>
          
          <div class="flex justify-end mt-3">
            <button
              @click="clearFilters"
              class="text-sm text-gray-500 hover:text-gray-700 underline"
            >
              Limpiar filtros
            </button>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Data Table -->
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <!-- Select all checkbox -->
            <th scope="col" class="px-3 py-3 text-left">
              <input
                type="checkbox"
                :checked="allRowsSelected"
                :indeterminate="someRowsSelected"
                @change="toggleSelectAll"
                class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
              />
            </th>
            
            <!-- Sortable columns -->
            <th
              v-for="column in tableColumns"
              :key="column.key"
              scope="col"
              class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              :class="column.className"
              @click="handleSort(column.key)"
            >
              <div class="flex items-center space-x-1">
                <span>{{ column.label }}</span>
                <svg v-if="sortField === column.key" class="w-4 h-4" :class="sortDirection === 'asc' ? 'text-green-500' : 'text-green-500 rotate-180'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
                </svg>
                <svg v-else class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
                </svg>
              </div>
            </th>
            
            <!-- Actions column -->
            <th scope="col" class="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Acciones
            </th>
          </tr>
        </thead>
        
        <tbody class="bg-white divide-y divide-gray-200">
          <!-- Loading state -->
          <tr v-if="isLoading">
            <td :colspan="tableColumns.length + 2" class="px-3 py-8 text-center">
              <div class="flex items-center justify-center space-x-2">
                <svg class="animate-spin h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span class="text-sm text-gray-500">Cargando datos...</span>
              </div>
            </td>
          </tr>
          
          <!-- No data state -->
          <tr v-else-if="paginatedData.length === 0">
            <td :colspan="tableColumns.length + 2" class="px-3 py-8 text-center">
              <div class="flex flex-col items-center space-y-2">
                <svg class="w-8 h-8 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                </svg>
                <p class="text-sm font-medium text-gray-500">No hay datos disponibles</p>
                <p class="text-xs text-gray-400">
                  {{ hasActiveFilters ? 'Intenta ajustar los filtros' : 'Agrega nuevas imágenes al dataset' }}
                </p>
              </div>
            </td>
          </tr>
          
          <!-- Data rows -->
          <tr
            v-else
            v-for="item in paginatedData"
            :key="item.id"
            class="hover:bg-gray-50 transition-colors duration-150"
            :class="{ 'bg-blue-50': selectedRows.includes(item.id) }"
          >
            <!-- Selection checkbox -->
            <td class="px-3 py-4">
              <input
                type="checkbox"
                :value="item.id"
                v-model="selectedRows"
                class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
              />
            </td>
            
            <!-- Image thumbnail -->
            <td class="px-3 py-4">
              <div class="flex items-center">
                <div class="flex-shrink-0 h-10 w-10">
                  <img
                    v-if="item.image_url"
                    :src="item.image_url"
                    :alt="`Imagen ${item.id}`"
                    class="h-10 w-10 object-cover rounded border border-gray-200"
                    @error="handleImageError"
                  />
                  <div v-else class="h-10 w-10 bg-gray-200 rounded flex items-center justify-center">
                    <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                </div>
              </div>
            </td>
            
            <!-- ID -->
            <td class="px-3 py-4 text-sm text-gray-900">
              #{{ item.id }}
            </td>
            
            <!-- Dimensions -->
            <td class="px-3 py-4 text-sm text-gray-900">
              <div class="space-y-1">
                <div>{{ formatNumber(item.width) }} × {{ formatNumber(item.height) }} × {{ formatNumber(item.thickness) }} mm</div>
                <div class="text-xs text-gray-500">Vol: {{ formatVolume(item) }} mm³</div>
              </div>
            </td>
            
            <!-- Weight -->
            <td class="px-3 py-4 text-sm text-gray-900">
              {{ formatNumber(item.weight) }} g
            </td>
            
            <!-- Quality -->
            <td class="px-3 py-4">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" :class="getQualityBadgeClass(item.predicted_quality)">
                {{ getQualityLabel(item.predicted_quality) }}
              </span>
              <div v-if="item.quality_score" class="text-xs text-gray-500 mt-1">
                Score: {{ Math.round(item.quality_score * 100) }}%
              </div>
            </td>
            
            <!-- Status -->
            <td class="px-3 py-4">
              <span v-if="item.is_processed" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                Procesado
              </span>
              <span v-else class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
                </svg>
                Pendiente
              </span>
            </td>
            
            <!-- Batch -->
            <td class="px-3 py-4 text-sm text-gray-900">
              {{ item.batch_number || '-' }}
            </td>
            
            <!-- Origin -->
            <td class="px-3 py-4 text-sm text-gray-900">
              {{ item.origin || '-' }}
            </td>
            
            <!-- Date -->
            <td class="px-3 py-4 text-sm text-gray-500">
              {{ formatDate(item.created_at) }}
            </td>
            
            <!-- Actions -->
            <td class="px-3 py-4 text-right text-sm">
              <div class="flex items-center justify-end space-x-2">
                <button
                  @click="viewItem(item)"
                  class="text-gray-400 hover:text-gray-600"
                  title="Ver detalles"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>
                
                <button
                  @click="editItem(item)"
                  class="text-gray-400 hover:text-blue-600"
                  title="Editar"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                
                <button
                  @click="deleteItem(item)"
                  class="text-gray-400 hover:text-red-600"
                  title="Eliminar"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="!isLoading && totalItems > 0" class="px-6 py-4 border-t border-gray-200">
      <Pagination
        :current-page="currentPage"
        :total-pages="totalPages"
        :total-items="totalItems"
        :items-per-page="itemsPerPage"
        :show-items-per-page="true"
        @page-change="handlePageChange"
        @items-per-page-change="handleItemsPerPageChange"
      />
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, watch, onMounted } from 'vue';
import { getDatasetImages, exportDatasetCSV, formatNumber } from '@/services/datasetApi.js';
import Pagination from '@/components/agricultores/Pagination.vue';

// Debounce utility (DRY)
const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

export default {
  name: 'DatasetTable',
  components: {
    Pagination
  },
  
  // Props (SRP - configuración modular)
  props: {
    autoRefresh: {
      type: Boolean,
      default: false
    },
    refreshInterval: {
      type: Number,
      default: 30000 // 30 segundos
    }
  },
  
  // Eventos (SRP - comunicación clara)
  emits: ['item-view', 'item-edit', 'item-delete', 'bulk-edit', 'bulk-delete', 'data-refresh'],
  
  setup(props, { emit }) {
    // Estado reactivo (separado por responsabilidad)
    const isLoading = ref(false);
    const showFilters = ref(false);
    const showBulkEditModal = ref(false);
    const data = ref([]);
    const selectedRows = ref([]);
    
    // Paginación
    const currentPage = ref(1);
    const itemsPerPage = ref(20);
    const totalItems = ref(0);
    
    // Ordenamiento
    const sortField = ref('created_at');
    const sortDirection = ref('desc');
    
    // Filtros (reactivos)
    const filters = reactive({
      predicted_quality: '',
      is_processed: '',
      batch_number: '',
      origin: '',
      date_from: '',
      date_to: ''
    });
    
    // Configuración de tabla (KISS - definición simple)
    const tableColumns = ref([
      { key: 'image', label: 'Imagen', className: 'w-16' },
      { key: 'id', label: 'ID', className: 'w-20' },
      { key: 'dimensions', label: 'Dimensiones', className: 'w-32' },
      { key: 'weight', label: 'Peso', className: 'w-24' },
      { key: 'predicted_quality', label: 'Calidad', className: 'w-28' },
      { key: 'is_processed', label: 'Estado', className: 'w-28' },
      { key: 'batch_number', label: 'Lote', className: 'w-32' },
      { key: 'origin', label: 'Origen', className: 'w-32' },
      { key: 'created_at', label: 'Fecha', className: 'w-32' }
    ]);
    
    // Computed properties (DRY - cálculos reutilizables)
    const totalPages = computed(() => Math.ceil(totalItems.value / itemsPerPage.value));
    
    const paginatedData = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage.value;
      const end = start + itemsPerPage.value;
      return data.value.slice(start, end);
    });
    
    const allRowsSelected = computed(() => {
      return paginatedData.value.length > 0 && 
             paginatedData.value.every(item => selectedRows.value.includes(item.id));
    });
    
    const someRowsSelected = computed(() => {
      return selectedRows.value.length > 0 && !allRowsSelected.value;
    });
    
    const hasActiveFilters = computed(() => {
      return Object.values(filters).some(value => value !== '' && value !== null);
    });
    
    // Métodos de datos (SRP - solo gestión de datos)
    const loadData = async () => {
      isLoading.value = true;
      
      try {
        const queryFilters = { ...filters };
        
        // Limpiar filtros vacíos
        Object.keys(queryFilters).forEach(key => {
          if (queryFilters[key] === '' || queryFilters[key] === null) {
            delete queryFilters[key];
          }
        });
        
        // Agregar ordenamiento
        if (sortField.value) {
          queryFilters.ordering = sortDirection.value === 'desc' ? `-${sortField.value}` : sortField.value;
        }
        
        const response = await getDatasetImages(queryFilters, currentPage.value, itemsPerPage.value);
        
        data.value = response.results || [];
        totalItems.value = response.count || 0;
        
        emit('data-refresh', {
          total: totalItems.value,
          filtered: data.value.length,
          page: currentPage.value
        });
        
      } catch (error) {
        console.error('Error cargando datos:', error);
        data.value = [];
        totalItems.value = 0;
      } finally {
        isLoading.value = false;
      }
    };
    
    const refreshData = () => {
      selectedRows.value = []; // Limpiar selección
      loadData();
    };
    
    // Métodos de filtros (DRY - lógica reutilizable)
    const applyFilters = () => {
      currentPage.value = 1; // Reset a primera página
      loadData();
    };
    
    const clearFilters = () => {
      Object.keys(filters).forEach(key => {
        filters[key] = '';
      });
      applyFilters();
    };
    
    const toggleFilters = () => {
      showFilters.value = !showFilters.value;
    };
    
    // Debounced filter para inputs de texto
    const debouncedFilter = debounce(applyFilters, 500);
    
    // Métodos de ordenamiento (KISS - lógica simple)
    const handleSort = (field) => {
      if (sortField.value === field) {
        sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
      } else {
        sortField.value = field;
        sortDirection.value = 'asc';
      }
      loadData();
    };
    
    // Métodos de selección (DRY - lógica centralizada)
    const toggleSelectAll = () => {
      if (allRowsSelected.value) {
        selectedRows.value = selectedRows.value.filter(id => 
          !paginatedData.value.some(item => item.id === id)
        );
      } else {
        const newSelections = paginatedData.value
          .map(item => item.id)
          .filter(id => !selectedRows.value.includes(id));
        selectedRows.value = [...selectedRows.value, ...newSelections];
      }
    };
    
    // Métodos de paginación (SRP - solo paginación)
    const handlePageChange = (page) => {
      currentPage.value = page;
      loadData();
    };
    
    const handleItemsPerPageChange = (newSize) => {
      itemsPerPage.value = newSize;
      currentPage.value = 1;
      loadData();
    };
    
    // Métodos de acciones (SRP - solo acciones de elementos)
    const viewItem = (item) => {
      emit('item-view', item);
    };
    
    const editItem = (item) => {
      emit('item-edit', item);
    };
    
    const deleteItem = (item) => {
      emit('item-delete', item);
    };
    
    const confirmBulkDelete = () => {
      if (selectedRows.value.length > 0) {
        emit('bulk-delete', selectedRows.value);
      }
    };
    
    // Métodos de exportación (SRP - solo exportación)
    const exportData = async () => {
      try {
        isLoading.value = true;
        
        const queryFilters = { ...filters };
        Object.keys(queryFilters).forEach(key => {
          if (queryFilters[key] === '' || queryFilters[key] === null) {
            delete queryFilters[key];
          }
        });
        
        const blob = await exportDatasetCSV(queryFilters);
        
        // Descargar archivo
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `dataset_export_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
      } catch (error) {
        console.error('Error exportando datos:', error);
      } finally {
        isLoading.value = false;
      }
    };
    
    // Utilidades de formato (DRY - funciones reutilizables)
    const formatDate = (dateString) => {
      if (!dateString) return '-';
      const date = new Date(dateString);
      return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    };
    
    const formatVolume = (item) => {
      if (!item.width || !item.height || !item.thickness) return '-';
      const volume = item.width * item.height * item.thickness;
      return formatNumber(volume, 0);
    };
    
    const getQualityLabel = (quality) => {
      const labels = {
        excellent: 'Excelente',
        good: 'Buena',
        fair: 'Regular',
        poor: 'Pobre'
      };
      return labels[quality] || quality || '-';
    };
    
    const getQualityBadgeClass = (quality) => {
      const classes = {
        excellent: 'bg-green-100 text-green-800',
        good: 'bg-blue-100 text-blue-800',
        fair: 'bg-yellow-100 text-yellow-800',
        poor: 'bg-red-100 text-red-800'
      };
      return classes[quality] || 'bg-gray-100 text-gray-800';
    };
    
    const handleImageError = (event) => {
      event.target.style.display = 'none';
    };
    
    // Auto-refresh (opcional)
    let refreshTimer = null;
    
    const setupAutoRefresh = () => {
      if (props.autoRefresh && props.refreshInterval > 0) {
        refreshTimer = setInterval(loadData, props.refreshInterval);
      }
    };
    
    const cleanupAutoRefresh = () => {
      if (refreshTimer) {
        clearInterval(refreshTimer);
        refreshTimer = null;
      }
    };
    
    // Watchers (reactividad específica)
    watch(() => props.autoRefresh, (newValue) => {
      if (newValue) {
        setupAutoRefresh();
      } else {
        cleanupAutoRefresh();
      }
    });
    
    // Lifecycle
    onMounted(() => {
      loadData();
      setupAutoRefresh();
    });
    
    return {
      // Estado
      isLoading,
      showFilters,
      showBulkEditModal,
      data,
      selectedRows,
      currentPage,
      itemsPerPage,
      totalItems,
      sortField,
      sortDirection,
      filters,
      tableColumns,
      
      // Computed
      totalPages,
      paginatedData,
      allRowsSelected,
      someRowsSelected,
      hasActiveFilters,
      
      // Métodos
      loadData,
      refreshData,
      applyFilters,
      clearFilters,
      toggleFilters,
      debouncedFilter,
      handleSort,
      toggleSelectAll,
      handlePageChange,
      handleItemsPerPageChange,
      viewItem,
      editItem,
      deleteItem,
      confirmBulkDelete,
      exportData,
      
      // Utilidades
      formatDate,
      formatVolume,
      formatNumber,
      getQualityLabel,
      getQualityBadgeClass,
      handleImageError
    };
  }
};
</script>

<style scoped>
/* Transiciones */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.slide-down-enter-from,
.slide-down-leave-to {
  max-height: 0;
  opacity: 0;
}

.slide-down-enter-to,
.slide-down-leave-from {
  max-height: 200px;
  opacity: 1;
}

/* Hover effects */
tr:hover {
  background-color: #f9fafb;
}

/* Loading states */
.loading {
  opacity: 0.6;
  pointer-events: none;
}

/* Custom scrollbar */
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

/* Focus states */
.focus-visible:focus {
  outline: 2px solid #10b981;
  outline-offset: 2px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .md\:grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
}
</style>
