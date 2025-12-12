<template>
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden" data-section="alerts">
    <div class="bg-gradient-to-r from-red-50 to-orange-50 px-6 py-4 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <div class="bg-red-100 p-2 rounded-xl mr-3">
            <svg class="text-xl text-red-600 w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
            </svg>
          </div>
          <div>
            <h2 class="text-lg font-bold text-gray-900">Alertas Inteligentes</h2>
            <p class="text-sm text-gray-600">Sistema de alertas del cultivo</p>
          </div>
        </div>
        <span v-if="alerts.length > 0" class="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full">
          {{ alerts.length }}
        </span>
      </div>
    </div>
    
    <div class="p-6">
      <div v-if="loading" class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        <p class="text-gray-600 mt-2">Cargando alertas...</p>
      </div>
      
      <div v-else-if="alerts.length === 0" class="text-center py-8">
        <div class="text-green-500 text-4xl mb-2">✓</div>
        <p class="text-gray-600 font-medium">No hay alertas activas</p>
        <p class="text-gray-500 text-sm mt-1">Todo está funcionando correctamente</p>
      </div>
      
      <div v-else class="space-y-3">
        <div
          v-for="alert in alerts"
          :key="alert.id"
          :class="[
            'p-4 rounded-xl border-l-4 transition-all duration-200',
            alert.priority === 'high' ? 'bg-red-50 border-red-500' :
            alert.priority === 'medium' ? 'bg-yellow-50 border-yellow-500' :
            'bg-blue-50 border-blue-500'
          ]"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-2">
                <span
                  :class="[
                    'px-2 py-1 rounded text-xs font-bold',
                    alert.priority === 'high' ? 'bg-red-500 text-white' :
                    alert.priority === 'medium' ? 'bg-yellow-500 text-white' :
                    'bg-blue-500 text-white'
                  ]"
                >
                  {{ alert.priority === 'high' ? 'Alta' : alert.priority === 'medium' ? 'Media' : 'Baja' }}
                </span>
                <span class="text-sm font-semibold text-gray-900">{{ alert.title }}</span>
              </div>
              <p class="text-sm text-gray-700 mb-3">{{ alert.message }}</p>
              <button
                v-if="alert.action"
                @click="$emit('action-click', alert.action)"
                :class="[
                  'text-sm font-semibold px-4 py-2 rounded-lg transition-colors',
                  alert.priority === 'high' ? 'bg-red-500 hover:bg-red-600 text-white' :
                  alert.priority === 'medium' ? 'bg-yellow-500 hover:bg-yellow-600 text-white' :
                  'bg-blue-500 hover:bg-blue-600 text-white'
                ]"
              >
                {{ alert.action.label }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  alerts: {
    type: Array,
    required: true,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['action-click'])
</script>

