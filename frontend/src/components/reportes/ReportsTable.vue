<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
    <div class="px-4 py-3 md:px-6 md:py-4 border-b border-gray-200">
      <h3 class="text-lg md:text-xl font-semibold text-gray-900">Reportes Generados</h3>
      <p class="mt-1 text-sm md:text-base text-gray-500">Lista de todos los reportes disponibles</p>
    </div>
    
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200" aria-label="Tabla de reportes generados">
        <caption class="sr-only">Tabla de reportes mostrando nombre, tipo, período, fecha de creación, estado y acciones disponibles</caption>
        <thead class="bg-gray-50">
          <tr>
            <th v-for="column in columns" :key="column.key" 
                class="px-3 py-3 md:px-6 md:py-4 text-left text-xs md:text-sm font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors duration-200"
                :class="[
                  column.mobileHidden ? 'mobile-hidden' : '',
                  sortKey === column.key ? 'sorted' : ''
                ]"
                @click="handleSort(column.key)">
              <div class="flex items-center space-x-1">
                <span>{{ column.label }}</span>
                <svg v-if="sortKey === column.key" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path v-if="sortOrder === 'asc'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"></path>
                  <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </div>
            </th>
            <th class="px-3 py-3 md:px-6 md:py-4 text-right text-xs md:text-sm font-medium text-gray-500 uppercase tracking-wider">
              Acciones
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="(report, index) in reports" :key="report.id" 
              class="hover:bg-gray-50 transition-colors duration-200">
            <td class="px-3 py-3 md:px-6 md:py-4 whitespace-nowrap text-sm md:text-base text-gray-900">
              {{ report.name }}
            </td>
            <td class="px-3 py-3 md:px-6 md:py-4 whitespace-nowrap text-sm md:text-base text-gray-900 mobile-hidden">
              {{ report.type }}
            </td>
            <td class="px-3 py-3 md:px-6 md:py-4 whitespace-nowrap text-sm md:text-base text-gray-900 mobile-hidden">
              {{ report.period }}
            </td>
            <td class="px-3 py-3 md:px-6 md:py-4 whitespace-nowrap text-sm md:text-base text-gray-900">
              {{ report.createdAt }}
            </td>
            <td class="px-3 py-3 md:px-6 md:py-4 whitespace-nowrap text-sm md:text-base">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" 
                    :class="getStatusClasses(report.status)">
                {{ report.status }}
              </span>
            </td>
            <td class="px-3 py-3 md:px-6 md:py-4 whitespace-nowrap text-right text-sm md:text-base font-medium">
              <div class="flex items-center justify-end space-x-2">
                <button @click="handleView(report)" 
                        class="text-indigo-600 hover:text-indigo-900 transition-colors duration-200 p-1 rounded-md hover:bg-indigo-50"
                        title="Ver reporte">
                  <svg class="w-4 h-4 md:w-5 md:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                  </svg>
                </button>
                <button @click="handleDownload(report)" 
                        class="text-green-600 hover:text-green-900 transition-colors duration-200 p-1 rounded-md hover:bg-green-50"
                        title="Descargar reporte">
                  <svg class="w-4 h-4 md:w-5 md:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                </button>
                <button @click="handleDelete(report)" 
                        class="text-red-600 hover:text-red-900 transition-colors duration-200 p-1 rounded-md hover:bg-red-50"
                        title="Eliminar reporte">
                  <svg class="w-4 h-4 md:w-5 md:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                  </svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- Estado vacío -->
      <div v-if="reports.length === 0" class="text-center py-12 px-4">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
        <h3 class="mt-2 text-sm md:text-base font-medium text-gray-900">No hay reportes</h3>
        <p class="mt-1 text-sm text-gray-500">Comienza generando tu primer reporte.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useTable } from '@/composables/useTable'
import { formatReportStatus, getReportStatusClass } from '@/composables/useReports'
import { useDateFormatting } from '@/composables/useDateFormatting'

const props = defineProps({
  reports: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['sort', 'view', 'download', 'delete'])

const { formatDate } = useDateFormatting()

// Use table composable for sorting
const table = useTable({
  initialSortKey: 'createdAt',
  initialSortOrder: 'desc',
  enableSelection: false
})

const columns = [
  { key: 'name', label: 'Nombre del Reporte', mobileHidden: false },
  { key: 'type', label: 'Tipo', mobileHidden: true },
  { key: 'period', label: 'Período', mobileHidden: true },
  { key: 'createdAt', label: 'Fecha de Creación', mobileHidden: false },
  { key: 'status', label: 'Estado', mobileHidden: false }
]

const handleSort = (key) => {
  table.handleSort(key)
}

const getStatusClasses = (status) => {
  const statusClass = getReportStatusClass(status)
  const classMap = {
    'status-completed': 'bg-green-100 text-green-800',
    'status-processing': 'bg-yellow-100 text-yellow-800',
    'status-generating': 'bg-yellow-100 text-yellow-800',
    'status-pending': 'bg-gray-100 text-gray-800',
    'status-error': 'bg-red-100 text-red-800'
  }
  return classMap[statusClass] || classMap['status-pending']
}

const handleView = (report) => {
  emit('view', report)
}

const handleDownload = (report) => {
  emit('download', report)
}

const handleDelete = (report) => {
  emit('delete', report)
}

const formatReportDate = (dateString) => formatDate(dateString)
const formatReportStatusLabel = (status) => formatReportStatus(status)
</script>

<style scoped>
/* Mejoras de responsividad para la tabla de reportes */
@media (max-width: 768px) {
  .md\:px-6 {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  .md\:py-4 {
    padding-top: 1rem;
    padding-bottom: 1rem;
  }
  
  .md\:text-xl {
    font-size: 1.25rem;
    line-height: 1.75rem;
  }
  
  .md\:text-base {
    font-size: 1rem;
    line-height: 1.5rem;
  }
  
  .md\:w-5.md\:h-5 {
    width: 1.25rem;
    height: 1.25rem;
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
  
  .text-lg {
    font-size: 1.125rem;
    line-height: 1.75rem;
  }
  
  .text-sm {
    font-size: 0.875rem;
    line-height: 1.25rem;
  }
  
  .text-xs {
    font-size: 0.75rem;
    line-height: 1rem;
  }
  
  .w-4.h-4 {
    width: 1rem;
    height: 1rem;
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
  
  .space-x-2 > * + * {
    margin-left: 0.25rem;
  }
  
  .rounded-xl {
    border-radius: 0.5rem;
  }
}

/* Ocultar columnas menos importantes en móviles */
@media (max-width: 640px) {
  .mobile-hidden {
    display: none !important;
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
  
  button {
    min-width: 44px;
    min-height: 44px;
  }
}

/* Efectos de hover mejorados */
.hover\:bg-gray-50:hover {
  background-color: #f9fafb;
}

.hover\:bg-gray-100:hover {
  background-color: #f3f4f6;
}

.hover\:bg-indigo-50:hover {
  background-color: #eef2ff;
}

.hover\:bg-green-50:hover {
  background-color: #f0fdf4;
}

.hover\:bg-red-50:hover {
  background-color: #fef2f2;
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

/* Estados de carga */
.loading tbody tr {
  opacity: 0.6;
  pointer-events: none;
}

.loading tbody tr::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 20px;
  height: 20px;
  margin: -10px 0 0 -10px;
  border: 2px solid transparent;
  border-top-color: #9ca3af;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Mejoras para accesibilidad */
th:focus, button:focus {
  outline: 2px solid #10b981;
  outline-offset: 2px;
}

/* Responsive para pantallas muy grandes */
@media (min-width: 1280px) {
  .lg\:px-8 {
    padding-left: 2rem;
    padding-right: 2rem;
  }
  
  .lg\:py-5 {
    padding-top: 1.25rem;
    padding-bottom: 1.25rem;
  }
}

/* Mejoras para orientación landscape en móviles */
@media (max-width: 768px) and (orientation: landscape) {
  .py-3 {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }
  
  .text-lg {
    font-size: 1rem;
    line-height: 1.5rem;
  }
}

/* Estados de hover para botones de acción */
button:hover {
  transform: scale(1.05);
}

button:active {
  transform: scale(0.95);
}

/* Mejoras para tablas con muchos datos */
tbody tr:nth-child(even) {
  background-color: #fafafa;
}

tbody tr:nth-child(even):hover {
  background-color: #f3f4f6;
}

/* Mejoras específicas para móviles */
@media (max-width: 640px) {
  table {
    font-size: 0.875rem;
  }
  
  .overflow-x-auto {
    -webkit-overflow-scrolling: touch;
  }
  
  /* Ajustar espaciado en móviles */
  .space-x-2 > * + * {
    margin-left: 0.25rem;
  }
  
  /* Hacer botones más grandes en móviles */
  button {
    padding: 0.5rem;
  }
}

/* Mejoras para pantallas muy pequeñas */
@media (max-width: 480px) {
  .px-4 {
    padding-left: 0.5rem;
    padding-right: 0.5rem;
  }
  
  .py-3 {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }
  
  /* Reducir el tamaño de los iconos en pantallas muy pequeñas */
  .w-4.h-4 {
    width: 0.875rem;
    height: 0.875rem;
  }
  
  .md\:w-5.md\:h-5 {
    width: 1rem;
    height: 1rem;
  }
}
</style>
