<template>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <!-- System Alerts -->
    <div class="bg-white rounded-2xl border-2 border-gray-200 hover:shadow-xl hover:border-green-300 transition-all duration-300">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-xl font-bold text-gray-900">{{ alertsTitle }}</h3>
      </div>
      <div class="p-6">
        <div v-if="alerts.length === 0" class="text-center py-8">
          <svg class="w-12 h-12 text-green-500 mx-auto mb-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
          </svg>
          <p class="text-gray-500">{{ noAlertsMessage }}</p>
        </div>
        <div v-else class="space-y-3">
          <div 
            v-for="alert in alerts" 
            :key="alert.id"
            class="flex items-start p-4 rounded-lg border-l-4 animate-slide-in"
            :class="getAlertBorderClass(alert.type)"
          >
            <div class="flex-shrink-0">
              <svg class="w-5 h-5" :class="getAlertIconClass(alert.type)" fill="currentColor" viewBox="0 0 20 20">
                <path :d="getAlertIconPath(alert.type)"></path>
              </svg>
            </div>
            <div class="ml-3 flex-1">
              <h4 class="text-sm font-medium text-gray-900">{{ alert.title }}</h4>
              <p class="text-sm text-gray-600 mt-1">{{ alert.message }}</p>
              <p class="text-xs text-gray-500 mt-2">{{ formatDateTime(alert.created_at) }}</p>
            </div>
            <div class="ml-3 flex-shrink-0">
              <button 
                @click="handleDismissAlert(alert.id)"
                type="button"
                class="text-gray-400 hover:text-red-600 p-2 rounded-lg hover:bg-red-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-red-500"
                :title="`Descartar alerta: ${alert.title}`"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Reports Statistics -->
    <div class="bg-white rounded-2xl border-2 border-gray-200 hover:shadow-xl hover:border-green-300 transition-all duration-300">
      <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <h3 class="text-xl font-bold text-gray-900">{{ reportsTitle }}</h3>
        <router-link 
          :to="reportsLink" 
          class="text-sm text-green-600 hover:text-green-700 font-medium transition-colors duration-200"
        >
          {{ reportsLinkText }}
        </router-link>
      </div>
      <div class="p-6">
        <div class="grid grid-cols-2 gap-4">
          <div class="text-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200">
            <div class="text-2xl font-bold text-gray-900">{{ reportStats.total_reportes || 0 }}</div>
            <div class="text-sm text-gray-600">{{ totalReportsLabel }}</div>
          </div>
          <div class="text-center p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors duration-200">
            <div class="text-2xl font-bold text-green-600">{{ reportStats.reportes_completados || 0 }}</div>
            <div class="text-sm text-gray-600">{{ completedReportsLabel }}</div>
          </div>
          <div class="text-center p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors duration-200">
            <div class="text-2xl font-bold text-blue-600">{{ reportStats.reportes_generando || 0 }}</div>
            <div class="text-sm text-gray-600">{{ generatingReportsLabel }}</div>
          </div>
          <div class="text-center p-4 bg-red-50 rounded-lg hover:bg-red-100 transition-colors duration-200">
            <div class="text-2xl font-bold text-red-600">{{ reportStats.reportes_fallidos || 0 }}</div>
            <div class="text-sm text-gray-600">{{ failedReportsLabel }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 1. Vue core
import { defineProps, defineEmits } from 'vue'

// Props
const props = defineProps({
  alertsTitle: {
    type: String,
    default: 'Alertas del Sistema'
  },
  noAlertsMessage: {
    type: String,
    default: 'No hay alertas activas'
  },
  reportsTitle: {
    type: String,
    default: 'Reportes Generados'
  },
  reportsLink: {
    type: String,
    default: '/admin/reports'
  },
  reportsLinkText: {
    type: String,
    default: 'Gestionar Reportes'
  },
  totalReportsLabel: {
    type: String,
    default: 'Total Reportes'
  },
  completedReportsLabel: {
    type: String,
    default: 'Completados'
  },
  generatingReportsLabel: {
    type: String,
    default: 'Generando'
  },
  failedReportsLabel: {
    type: String,
    default: 'Fallidos'
  },
  alerts: {
    type: Array,
    default: () => []
  },
  reportStats: {
    type: Object,
    default: () => ({
      total_reportes: 0,
      reportes_completados: 0,
      reportes_generando: 0,
      reportes_fallidos: 0
    })
  }
})

// Emits
const emit = defineEmits(['dismiss-alert'])

// Functions
const handleDismissAlert = (alertId) => {
  emit('dismiss-alert', alertId)
}

const getAlertBorderClass = (type) => {
  const borderClasses = {
    'success': 'border-green-400 bg-green-50',
    'warning': 'border-yellow-400 bg-yellow-50',
    'error': 'border-red-400 bg-red-50',
    'info': 'border-blue-400 bg-blue-50',
    'critical': 'border-red-600 bg-red-100'
  }
  return borderClasses[type?.toLowerCase()] || 'border-gray-400 bg-gray-50'
}

const getAlertIconClass = (type) => {
  const iconClasses = {
    'success': 'text-green-500',
    'warning': 'text-yellow-500',
    'error': 'text-red-500',
    'info': 'text-blue-500',
    'critical': 'text-red-600'
  }
  return iconClasses[type?.toLowerCase()] || 'text-gray-500'
}

const getAlertIconPath = (type) => {
  const iconPaths = {
    'success': 'M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z',
    'warning': 'M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z',
    'error': 'M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z',
    'info': 'M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z',
    'critical': 'M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z'
  }
  return iconPaths[type?.toLowerCase()] || iconPaths['info']
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString('es-ES', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
/* Solo animación personalizada que no está en Tailwind */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.animate-slide-in {
  animation: slideIn 0.3s ease-out;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .space-y-3 > div {
    padding: 0.75rem;
  }
}
</style>
