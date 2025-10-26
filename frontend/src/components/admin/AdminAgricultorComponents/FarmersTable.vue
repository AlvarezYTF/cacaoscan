<template>
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
    <!-- Estado vacío -->
    <div v-if="filteredFarmers.length === 0" class="text-center py-16 px-6">
      <div class="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-6">
        <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
        </svg>
      </div>
      <h3 class="text-lg font-bold text-gray-900 mb-2">No se encontraron agricultores</h3>
      <p class="text-gray-600 mb-6">
        {{ searchQuery || filters.region !== 'all' || filters.status !== 'all' 
          ? 'Intenta ajustar los filtros o la búsqueda' 
          : 'Comienza agregando tu primer agricultor' }}
      </p>
      <button 
        v-if="!searchQuery && filters.region === 'all' && filters.status === 'all'"
        @click="$emit('new-farmer')"
        class="inline-flex items-center px-6 py-3 text-sm font-semibold text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all duration-200 shadow-md hover:shadow-lg"
      >
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
        </svg>
        Agregar Primer Agricultor
      </button>
    </div>

    <!-- Tabla con datos -->
    <DataTable 
      v-else
      :columns="tableColumns"
      :data="filteredFarmers"
      :show-table-info="false"
    >
      <!-- Celda personalizada para Agricultor -->
      <template #cell-farmer="{ row }">
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-full bg-gradient-to-br from-green-100 to-green-200 flex items-center justify-center text-green-700 font-semibold text-sm border-2 border-green-100">
            {{ row.initials }}
          </div>
          <div class="ml-3">
            <div class="text-sm font-medium text-gray-900">{{ row.name }}</div>
            <div class="text-xs text-gray-500">{{ row.email }}</div>
          </div>
        </div>
      </template>

      <!-- Celda personalizada para Finca -->
      <template #cell-farm="{ row }">
        <div class="text-sm text-gray-900 font-medium">{{ row.farm }}</div>
        <div class="text-xs text-gray-500">{{ row.hectares }} hectáreas</div>
      </template>

      <!-- Celda personalizada para Estado -->
      <template #cell-status="{ row }">
        <span :class="getStatusClasses(row.status)" class="px-3 py-1.5 inline-flex text-xs leading-4 font-semibold rounded-full">
          {{ row.status }}
        </span>
      </template>

      <!-- Celda personalizada para Acciones -->
      <template #cell-actions="{ row }">
        <div class="flex items-center space-x-3">
          <button class="text-green-600 hover:text-green-700 hover:bg-green-50 p-1.5 rounded-md transition-all duration-200" title="Ver detalles">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
            </svg>
          </button>
          <button class="text-blue-600 hover:text-blue-700 hover:bg-blue-50 p-1.5 rounded-md transition-all duration-200" title="Editar">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
            </svg>
          </button>
          <button class="text-red-600 hover:text-red-700 hover:bg-red-50 p-1.5 rounded-md transition-all duration-200" title="Eliminar">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
          </button>
        </div>
      </template>

      <!-- Paginación -->
      <template #pagination>
        <div class="bg-gray-50 px-6 py-4 border-t border-gray-200">
          <Pagination 
            :current-page="currentPage"
            :total-pages="totalPages"
            :total-items="totalItems"
            :items-per-page="itemsPerPage"
            @page-change="$emit('page-change', $event)"
          />
        </div>
      </template>
    </DataTable>
  </div>
</template>

<script>
import DataTable from './DataTable.vue';
import Pagination from './Pagination.vue';

export default {
  name: 'FarmersTable',
  components: { DataTable, Pagination },
  props: {
    filteredFarmers: {
      type: Array,
      required: true
    },
    searchQuery: {
      type: String,
      required: true
    },
    filters: {
      type: Object,
      required: true
    },
    tableColumns: {
      type: Array,
      required: true
    },
    currentPage: {
      type: Number,
      required: true
    },
    totalPages: {
      type: Number,
      required: true
    },
    totalItems: {
      type: Number,
      required: true
    },
    itemsPerPage: {
      type: Number,
      required: true
    }
  },
  emits: ['new-farmer', 'page-change'],
  methods: {
    getStatusClasses(status) {
      switch (status) {
        case 'Activo':
          return 'bg-green-100 text-green-800';
        case 'En revisión':
          return 'bg-amber-100 text-amber-800';
        case 'Inactivo':
          return 'bg-red-100 text-red-800';
        default:
          return 'bg-gray-100 text-gray-800';
      }
    }
  }
};
</script>

